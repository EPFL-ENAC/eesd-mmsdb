<template>
  <q-page>
    <div class="q-pa-md">
      <h3>Related projects</h3>
      <q-list>
        <essential-link
          title="Masonry Shake Table Database"
          caption="Open database of shake table tests and numerical models of URM buildings"
          link="https://masonrydb.epfl.ch/"
          icon="table_view"
        />
        <essential-link
          title="Stone Masonry Database"
          caption="Stone Masonry Database"
          link="https://eesd-epfl.github.io/StoneMasonryDatabase/"
          icon="table_view"
        />
      </q-list>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import EssentialLink from 'src/components/EssentialLink.vue';
// const { t } = useI18n();
</script>
