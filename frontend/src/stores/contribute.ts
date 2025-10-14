import { defineStore } from 'pinia';
import { LocalStorage } from 'quasar';
import { api } from 'src/boot/api';
import type { UploadInfo, Contribution } from 'src/models';

const CONTRIB_STORAGE_NAME = 'mms_contrib';

export const useContributeStore = defineStore('contribute', () => {

  const uploadInfos = ref<UploadInfo[]>([]);

  function initUploadInfos(): UploadInfo[] {
    const uploadInfosSaved = LocalStorage.getItem(CONTRIB_STORAGE_NAME);
    if (uploadInfosSaved !== null) {
      if (typeof uploadInfosSaved === 'string') {
        uploadInfos.value = JSON.parse(uploadInfosSaved);
      } else if (typeof uploadInfosSaved === 'object') {
        uploadInfos.value = uploadInfosSaved as UploadInfo[];
      }
    }
    return uploadInfos.value;
  }

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

  async function deleteUpload(info: UploadInfo): Promise<void> {
    await api.delete(`/files/upload/${info.path}`);
    deleteUploadInfo(info);
  }

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

  function saveUploadInfo(uploadInfoData: UploadInfo) {
    // update by name if already exists
    const index = uploadInfos.value.findIndex((info) => info.path === uploadInfoData.path);
    if (index !== -1) {
      uploadInfos.value[index] = uploadInfoData;
      LocalStorage.set(CONTRIB_STORAGE_NAME, JSON.stringify(uploadInfos.value));
      return;
    }
    uploadInfos.value.push(uploadInfoData);
    LocalStorage.set(CONTRIB_STORAGE_NAME, JSON.stringify(uploadInfos.value));
  }

  function deleteUploadInfo(uploadInfoData: UploadInfo) {
    const index = uploadInfos.value.findIndex((info) => info.path === uploadInfoData.path);
    if (index !== -1) {
      uploadInfos.value.splice(index, 1);
      LocalStorage.set(CONTRIB_STORAGE_NAME, JSON.stringify(uploadInfos.value));
    }
  }

  return {
    uploadInfos,
    initUploadInfos,
    saveUploadInfo,
    upload,
    deleteUpload,
    downloadUpload,
  };
});
