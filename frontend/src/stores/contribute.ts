import { AxiosError } from 'axios';
import { defineStore } from 'pinia';
import { LocalStorage } from 'quasar';
import { api } from 'src/boot/api';
import type { UploadInfo, Contribution, UploadInfoState, User } from 'src/models';

const CONTRIB_STORAGE_NAME = 'mms_contrib';

export const useContributeStore = defineStore('contribute', () => {

  const userInfo = ref<User>();
  const uploadInfos = ref<UploadInfo[]>([]);
  const allUploadInfos = ref<UploadInfo[]>([]);

  /**
   * Initiate GitHub login by redirecting to the authentication URL.
   */
  async function login() {
    const response = await api.get('/auth/login');
    // redirect to GitHub authentication URL
    const authUrl = response.data.url as string;
    window.location.href = authUrl;
  }

  /**
   * Logout the current user by deleting the session on the server and clearing local user info.
   */
  async function logout() {
    try {
      await api.delete('/auth/session');
    } finally {
      userInfo.value = undefined;
    }
  }

  /**
   * Fetch the current user's information from the server.
   */
  async function fetchUserInfo() {
    try {
      const response = await api.get('/auth/userinfo');
      userInfo.value = response.data;
      return userInfo.value;
    } catch (error: unknown) {
      await handleErrorResponse(error);
      return undefined;
    }
  }

  async function handleErrorResponse(error: unknown) {
    console.error('Error fetching user info:', error);
    if (error instanceof AxiosError && error.response && error.response.status === 401 && error.response.data?.detail === 'invalid_token') {
      // not authenticated
      await logout();
    } else {
      throw error;
    }
  }

  /**
   * Initialize the user's upload infos from local storage and verify their state from the server.
   * If the upload is no longer accessible, it is removed from the list.
   *
   * @returns Promise<UploadInfo[]>
   */
  async function initMyUploadInfos(): Promise<UploadInfo[]> {
    const uploadInfosSaved = LocalStorage.getItem(CONTRIB_STORAGE_NAME);
    let parsed: UploadInfo[] = [];
    if (uploadInfosSaved !== null) {
      if (typeof uploadInfosSaved === 'string') {
        parsed = JSON.parse(uploadInfosSaved);
      } else if (typeof uploadInfosSaved === 'object') {
        parsed = uploadInfosSaved as UploadInfo[];
      }
      return Promise.all(parsed.map(async (info) => {
        return api.get(`/files/upload/${encodeURIComponent(info.path)}/_state`)
        .then((response) => {
          const state = response.data as UploadInfoState;
          return { ...info, ...state };
        }).catch(() => {
          // either missing or not accessible anymore
          return null;
        });
      })).then((results) => {
        const filtered = results.filter((info): info is UploadInfo => info !== null);
        uploadInfos.value = filtered;
        // sort by most recent first
        uploadInfos.value.sort(uploadInfoSorter);
        LocalStorage.set(CONTRIB_STORAGE_NAME, JSON.stringify(uploadInfos.value));
        return uploadInfos.value;
      });
    } else {
      uploadInfos.value = parsed;
    }
    return Promise.resolve(uploadInfos.value);
  }

  /**
   * Initialize all upload infos from the server (requires API key).
   *
   * @returns Promise<UploadInfo[]>
   */
  async function initUploadInfos(): Promise<UploadInfo[]> {
    try {
      const response = await api.get('/files/upload-info');
      allUploadInfos.value = response.data as UploadInfo[];
      // sort by most recent first
      allUploadInfos.value.sort(uploadInfoSorter);
      return allUploadInfos.value;
    } catch (error) {
      await handleErrorResponse(error);
      return [];
    }
  }

  /**
   * Upload files with contribution metadata.
   * @param files Array of files to upload.
   * @param contribution Contribution metadata.
   * @returns Promise<UploadInfo>
   */
  async function upload(files: File[], contribution: Contribution): Promise<UploadInfo> {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });
    formData.append('contribution', JSON.stringify(contribution));
    const response = await api.post('/files/upload', formData);
    const result = response.data;
    saveUploadInfo(result as UploadInfo);
    return result as UploadInfo;
  }

  /**
   * Delete an upload by its info.
   * @param info UploadInfo to delete.
   */
  async function deleteUpload(info: UploadInfo): Promise<void> {
    await api.delete(`/files/upload/${info.path}`);
    deleteUploadInfo(info);
  }

  /**
   * Download an upload by its path.
   * @param path Path of the upload to download.
   */
  async function downloadUpload(path: string) {
    const response = await api.get(`/files/upload/${encodeURIComponent(path)}`, {
      responseType: 'blob'
    });
    const contentDisposition = response.headers['content-disposition'];
    const filenameMatch = contentDisposition && contentDisposition.match(/filename="?([^"]+)"?/);
    const filename = filenameMatch ? filenameMatch[1] : 'download.zip';
    const blob = new Blob([response.data], { type: 'application/zip' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }

  /**
   * Save or update an upload info in local storage.
   * @param uploadInfoData UploadInfo to save.
   */
  function saveUploadInfo(uploadInfoData: UploadInfo) {
    // update by name if already exists
    const index = uploadInfos.value.findIndex((info) => info.path === uploadInfoData.path);
    if (index !== -1) {
      uploadInfos.value[index] = uploadInfoData;
      LocalStorage.set(CONTRIB_STORAGE_NAME, JSON.stringify(uploadInfos.value));
      return;
    }
    uploadInfos.value.push(uploadInfoData);
    // sort by most recent first
    uploadInfos.value.sort(uploadInfoSorter);
    LocalStorage.set(CONTRIB_STORAGE_NAME, JSON.stringify(uploadInfos.value));
  }

  /**
   * Delete an upload info from local storage.
   * @param uploadInfoData UploadInfo to delete.
   */
  function deleteUploadInfo(uploadInfoData: UploadInfo) {
    const index = uploadInfos.value.findIndex((info) => info.path === uploadInfoData.path);
    if (index !== -1) {
      uploadInfos.value.splice(index, 1);
      LocalStorage.set(CONTRIB_STORAGE_NAME, JSON.stringify(uploadInfos.value));
    }
  }

  /**
   * Sorts upload information by date.
   * @param a First upload info to compare.
   * @param b Second upload info to compare.
   * @returns A negative number if a is more recent than b, a positive number if b is more recent than a, and 0 if they are equal.
   */
  function uploadInfoSorter(a: UploadInfo, b: UploadInfo): number {
    const dateA = new Date(a.date);
    const dateB = new Date(b.date);
    return dateB.getTime() - dateA.getTime();
  }

  return {
    uploadInfos,
    allUploadInfos,
    userInfo,
    login,
    logout,
    fetchUserInfo,
    initMyUploadInfos,
    initUploadInfos,
    saveUploadInfo,
    upload,
    deleteUpload,
    downloadUpload,
  };
});
