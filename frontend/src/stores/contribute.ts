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

  return {
    uploadInfos,
    initUploadInfos,
    saveUploadInfo,
    upload
  };
});
