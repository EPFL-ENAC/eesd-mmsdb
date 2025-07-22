import { Notify } from 'quasar';
import { t } from 'src/boot/i18n';

export function notifySuccess(message: string) {
  Notify.create({
    type: 'positive',
    message: t(message),
  });
}

export function notifyInfo(message: string) {
  Notify.create({
    type: 'info',
    message: t(message),
  });
}

export function notifyWarning(message: string) {
  Notify.create({
    type: 'warning',
    message: t(message),
  });
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function getErrorMessage(error: any): string {
  let message = error.message;
  if (error.response?.data && error.response.data?.detail) {
    message = error.response.data?.detail;
  }
  else if (error.response?.data && error.response.data?.status) {
    message = t(`error.${error.response?.data.status}`, error.response?.data.arguments);
  }
  return message || t('unknown_error');
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function notifyError(error: any) {
  let message = t('unknown_error');
  if (typeof error === 'string') {
    message = t(error);
  } else {
    console.error(error);
    if (Array.isArray(error)) {
      message = error.map(getErrorMessage).join(' | ');
    } else {
      message = getErrorMessage(error);
    }
  }
  Notify.create({
    type: 'negative',
    message,
  });
}