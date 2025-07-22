import { defineBoot } from '#q-app/wrappers'
import { useSettingsStore } from 'src/stores/settings';

export default defineBoot(() => {
  const settingsStore = useSettingsStore();
  settingsStore.initSettings();
});
