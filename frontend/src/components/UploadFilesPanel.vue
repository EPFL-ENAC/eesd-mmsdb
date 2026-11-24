<template>
  <div>
    <q-tree
      :nodes="fileTree"
      node-key="path"
      no-transition
      :tick-strategy="'none'"
      :label-key="'label'"
    >
      <template v-slot:default-header="prop">
        <q-icon :name="prop.node.icon" :color="prop.node.type === 'FILE' ? 'accent' : 'secondary'" class="q-mr-sm" />
        <span>{{ prop.node.label }}</span>
        <span v-if="prop.node.type === 'FOLDER'" class="text-caption q-ml-sm">({{ t('items_count', { count: prop.node.children.length} ) }})</span>
        <q-btn v-if="prop.node.type === 'FILE'" dense flat round icon="download" size="xs" color="grey-6" :disable="downloading" class="q-ml-md" @click="onDownload($event, prop.node.path)" />
      </template>
    </q-tree>
  </div>
</template>

<script setup lang="ts">
import type { QTreeNode } from 'quasar';

const { t } = useI18n();
const contributeStore = useContributeStore();

const props = defineProps<{
  id: string;
  files: string[];
}>();

interface FileNode extends QTreeNode {
  path: string;
  type: string;
}

const fileTree = ref<FileNode[]>([]);
const downloading = ref(false);

onMounted(init);


function init() {
  const root: FileNode = {path: '/', type: 'FOLDER', children: []}
  props.files.forEach((file) => {
    const parts = file.split('/').filter((part) => part.length > 0);
    insertFile(parts, file, root, 0);
  });
  fileTree.value = [{label: t('contribute.files'), path: '/', type: 'FOLDER', icon: 'folder', children: (root.children || []) as FileNode[]}];
}

function insertFile(parts: string[], file: string, node: FileNode, idx: number) {
  if (parts.length === 0) {
    return;
  }
  const subparts = parts.slice(0, idx + 1);
  if (subparts[idx] === undefined) return;
  const nodePath = subparts.join('/');
  let child = node.children?.find((n) => n.path === nodePath);
  if (idx < parts.length - 1) {
    // FOLDER
    if (child && child.type !== 'FOLDER') {
      console.warn('Conflict in file structure, expected FOLDER but found file:', child);
      return;
    }
    if (child) {
      // Already exists
      insertFile(parts, file, child as FileNode, idx + 1);
      return;
    }
    // Create new FOLDER
    child = {
      label: subparts[idx],
      path: nodePath,
      type: 'FOLDER',
      icon: 'folder',
      children: [],
    };
  } else {
    // File
    child = {
      label: subparts[idx],
      path: file,
      type: 'FILE',
      icon: 'insert_drive_file',
    };
  }
  node.children = node.children || [];
  node.children.push(child);
  insertFile(parts, file, child as FileNode, idx + 1);
}

function onDownload(event: Event, path: string) {
  // do not propagate event to avoid expanding/collapsing tree node
  event.stopPropagation();
  // download as an attached file
  if (path === undefined || path.length === 0) {
    return;
  }
  downloading.value = true;
  contributeStore.downloadDraftFile(props.id, path).catch((error) => {
    console.error('Error downloading attached file:', error);
  }).finally(() => {
    downloading.value = false;
  });
}
</script>
