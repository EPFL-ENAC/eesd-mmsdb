<template>
  <q-page class="max-width">
    <div class="q-pa-md">
      <div class="text-h3 q-mb-md">About</div>
      <div class="q-mt-md">
        <q-list>
          <essential-link
            title="EPFL"
            caption="epfl.ch"
            link="https://www.epfl.ch"
            icon="school"
          />
          <essential-link
            title="EESD Laboratory"
            caption="epfl.ch/labs/eesd"
            link="https://www.epfl.ch/labs/eesd/"
            icon="engineering"
          />
          <essential-link
            title="ENAC-IT4R Development team"
            caption="go.epfl.ch/it4r"
            link="https://go.epfl.ch/it4r"
            icon="construction"
          />
          <essential-link
            title="Source Code"
            caption="epfl-enac/eesd-mmsdb"
            link="https://github.com/EPFL-ENAC/eesd-mmsdb"
            icon="code"
          />
        </q-list>
      </div>

      <div class="q-mt-lg">
        <h4>Scientific Information</h4>
        <div class="scientific-info q-mt-md">
          <h5 class="q-mb-md">Scientific Overview</h5>
          <p>
            This platform hosts the <b>Masonry Microstructure Database (MMS)</b>, the first open-access repository of 3D microstructures of stone masonry walls. Masonry microstructure—defined by the geometry, size, shape, and spatial arrangement of individual stone units—significantly influences structural performance.
          </p>
          <p>
            The database includes 36 walls covering major masonry typologies. Twelve walls are real, built and scanned in laboratories, and twenty-four are virtual, generated using digital masonry microstructure generators from the literature. Each wall is characterized using the Geometric Masonry Quality Index (GMQI), which is based on the well-known Masonry Quality Index (MQI) but considers only geometric parameters.
          </p>
          <h5 class="q-mt-lg q-mb-md">Platform Features</h5>
          <ul>
            <li><b>Open-Access Data:</b> Explore and download 3D meshes of walls and individual stones, with computed geometric parameters.</li>
            <li><b>Interactive Correlation Analysis:</b> Visualize correlations between different geometric features.</li>
            <li><b>Computational Tools:</b>
              <ul>
                <li><b>Line of Minimum Trace (LMT):</b> Compute LMT for user-provided data, including total, vertical, horizontal, and wall-leaf connection lengths.</li>
                <li><b>Masonry Quality Index (MQI):</b> Evaluate masonry quality from 2D images or user data for structural assessment and preservation.</li>
              </ul>
            </li>
            <li><b>Data Contribution:</b> Upload and document new 3D microstructures to foster collaboration and advance research on irregular masonry structures.</li>
          </ul>
          <p>
            This platform provides an interactive scientific environment for the visualization, exploration, and analysis of stone masonry walls, supporting numerical research, seismic assessment, digital twinning studies, and masonry classification, while promoting reproducible research and sustainable preservation of masonry heritage. The database and GMQI method are described in:
          </p>
          <citation-item
            v-bind="citationItems['Shah et al. 2024b']"
            class="q-mt-xs q-mb-xs"
          />
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import CitationItem from 'src/components/CitationItem.vue';
import EssentialLink from 'src/components/EssentialLink.vue';
import citationItems from 'src/assets/citation_items.json';
// const { t } = useI18n();
</script>
