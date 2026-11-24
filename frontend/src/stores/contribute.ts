import { AxiosError } from 'axios';
import { defineStore } from 'pinia';
import { LocalStorage } from 'quasar';
import { api } from 'src/boot/api';
import type { Contributor, Draft, DraftState, Issue, MyContribution, User } from 'src/models';

const CONTRIB_STORAGE_NAME = 'mms_contrib';

export const useContributeStore = defineStore('contribute', () => {

  const userInfo = ref<User>();
  const myContributions = ref<MyContribution[]>([]);
  const drafts = ref<Draft[]>([]);

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
   * Load the contributions saved in this browser and refresh their state from the server.
   * Entries saved by the old upload API (no `id`) are dropped: the new API does not know them.
   */
  async function initMyContributions(): Promise<MyContribution[]> {
    const saved = LocalStorage.getItem(CONTRIB_STORAGE_NAME);
    let parsed: Partial<MyContribution>[] = [];
    if (typeof saved === 'string') {
      parsed = JSON.parse(saved);
    } else if (Array.isArray(saved)) {
      parsed = saved as Partial<MyContribution>[];
    }
    const kept = parsed.filter((c): c is MyContribution => typeof c.id === 'string');
    myContributions.value = await Promise.all(kept.map(async (c) => {
      try {
        const response = await api.get(`/contributions/${encodeURIComponent(c.id)}/state`);
        return { ...c, state: response.data.state as DraftState };
      } catch (error) {
        // 404: the server does not know this id; other errors: keep the last known state
        const notFound = error instanceof AxiosError && error.response?.status === 404;
        return notFound ? { ...c, state: 'unknown' as const } : c;
      }
    }));
    myContributions.value.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
    saveMyContributions();
    return myContributions.value;
  }

  function saveMyContributions() {
    LocalStorage.set(CONTRIB_STORAGE_NAME, JSON.stringify(myContributions.value));
  }

  /**
   * Submit files with the contributor metadata. Throws the axios error on failure,
   * use errorMessages() to show it.
   */
  async function submit(files: File[], contributor: Contributor): Promise<MyContribution> {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });
    formData.append('contributor', JSON.stringify(contributor));
    const response = await api.post('/contributions', formData);
    const saved: MyContribution = {
      id: response.data.id,
      name: contributor.name,
      date: new Date().toISOString(),
      state: 'submitted',
    };
    myContributions.value.unshift(saved);
    saveMyContributions();
    return saved;
  }

  /**
   * Admin: list the drafts, optionally in one state.
   */
  async function fetchDrafts(state?: DraftState): Promise<Draft[]> {
    const response = await api.get('/contributions/drafts', { params: state ? { state } : {} });
    drafts.value = response.data as Draft[];
    return drafts.value;
  }

  /**
   * Admin: move a draft to a new state. Returns the updated draft.
   */
  async function decide(id: string, state: DraftState, comment?: string): Promise<Draft> {
    const response = await api.post(`/contributions/drafts/${encodeURIComponent(id)}/decision`, { state, comment: comment || null });
    const draft = response.data as Draft;
    const index = drafts.value.findIndex((d) => d.id === id);
    if (index !== -1) drafts.value[index] = draft;
    return draft;
  }

  /**
   * Admin: download one file of a draft.
   */
  async function downloadDraftFile(id: string, path: string) {
    const encoded = path.split('/').map(encodeURIComponent).join('/');
    const response = await api.get(`/contributions/drafts/${encodeURIComponent(id)}/files/${encoded}`, {
      responseType: 'blob',
    });
    const url = window.URL.createObjectURL(response.data as Blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', path.split('/').pop() || 'download');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }

  return {
    myContributions,
    drafts,
    userInfo,
    login,
    logout,
    fetchUserInfo,
    initMyContributions,
    submit,
    fetchDrafts,
    decide,
    downloadDraftFile,
  };
});

/**
 * The messages to show for a failed contribution request:
 * the issues of a 422 report ("file: message"), or the `detail` of the error.
 */
export function errorMessages(error: unknown): string[] {
  if (!(error instanceof AxiosError) || !error.response?.data) {
    return [error instanceof Error ? error.message : String(error)];
  }
  const data = error.response.data as { issues?: Issue[]; detail?: unknown };
  if (Array.isArray(data.issues) && data.issues.length > 0) {
    return data.issues.map((i) => (i.file ? `${i.file}: ${i.message}` : i.message));
  }
  if (typeof data.detail === 'string') return [data.detail];
  if (Array.isArray(data.detail)) {
    // pydantic validation errors of the contributor field
    return data.detail.map((d: { loc?: unknown[]; msg?: string }) => `${(d.loc || []).join('.')}: ${d.msg}`);
  }
  return [error.message];
}

/** The badge color of a contribution state. */
export function stateColor(state: string): string {
  const colors: Record<string, string> = { submitted: 'info', accepted: 'primary', rejected: 'negative', published: 'positive', withdrawn: 'warning' };
  return colors[state] || 'grey';
}
