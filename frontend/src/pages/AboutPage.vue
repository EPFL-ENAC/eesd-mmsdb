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

      <p class="q-mt-md">
        If you have any suggestions or encounter issues, please provide your feedback using <a href="https://github.com/EPFL-ENAC/eesd-mmsdb/issues" target="_blank" rel="noopener">GitHub Issues</a>.
      </p>

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

      <div class="q-mt-lg">
        <h4>Frequently Asked Questions</h4>
        <div class="faq-section q-mt-md">
          <q-expansion-item
            group="faq"
            header-class="text-weight-medium"
            expand-separator
            label="What is the difference between GMQI and MQI?"
            icon="help_outline"
          >
            <p>
              <b>GMQI (Geometric Masonry Quality Index)</b> is a metric computed from the 3D microstructure data of each wall. It considers only geometric parameters such as stone shape, dimension, arrangement, and joint staggering. GMQI values are pre-computed and displayed for every wall in the database.
            </p>
            <p>
              <b>MQI (Masonry Quality Index)</b> is a broader assessment method (Borri &amp; De Maria, 2002) that combines both geometric and mechanical parameters. The platform offers an <a :href="router.resolve('/quality-index/mqi-calculator').href">MQI Calculator</a> where you can evaluate the quality of <i>your own</i> masonry wall using the full MQI methodology, including mortar properties, stone mechanical strength, and other non-geometric factors.
            </p>
          </q-expansion-item>

          <q-expansion-item
            group="faq"
            header-class="text-weight-medium"
            expand-separator
            label="What do &quot;Real&quot; and &quot;Virtual&quot; microstructure types mean?"
            icon="layers"
          >
            <p>
              <b>Real</b> walls are physical masonry walls that were built in laboratory settings and digitized through 3D scanning (e.g., photogrammetry or CT scanning). They represent actual constructed specimens.
            </p>
            <p>
              <b>Virtual</b> walls are generated computationally using digital masonry microstructure generators described in the literature. They are synthetic models that follow the geometric rules of specific masonry typologies but were never physically built.
            </p>
          </q-expansion-item>

          <q-expansion-item
            group="faq"
            header-class="text-weight-medium"
            expand-separator
            label="How can I contribute data to the database?"
            icon="upload"
          >
            <p>
              Use the <a :href="router.resolve('/contribute').href">Contribute page</a> (upload icon in the header toolbar). You will need to authenticate using a GitHub account. Once authenticated, you can upload 3D model files (<code>.ply</code>, <code>.obj</code>, <code>.stl</code>) or a <code>.zip</code> archive, along with metadata such as microstructure type, acquisition method, and a reference publication.
            </p>
          </q-expansion-item>

          <q-expansion-item
            group="faq"
            header-class="text-weight-medium"
            expand-separator
            label="What happens after I upload my data?"
            icon="cloud_upload"
          >
            <p>
              Uploaded files are stored and associated with your account. The upload is visible on the <a :href="router.resolve('/contribute').href">Contribute page</a> under "My uploads." A review process will be applied before data is integrated into the publicly browsable database. You can view comments on your contributions and track their status through the same page.
            </p>
          </q-expansion-item>

          <q-expansion-item
            group="faq"
            header-class="text-weight-medium"
            expand-separator
            label="Add a question or report an issue"
            icon="chat_bubble_outline"
          >
            <p>
              If your question is not covered, please open an <a href="https://github.com/EPFL-ENAC/eesd-mmsdb/issues" target="_blank" rel="noopener">Issue</a>. We aim to keep this FAQ updated based on user feedback.
            </p>
          </q-expansion-item>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import CitationItem from 'src/components/CitationItem.vue';
import EssentialLink from 'src/components/EssentialLink.vue';
import citationItems from 'src/assets/citation_items.json';

const router = useRouter();
// const { t } = useI18n();
</script>

<style scoped>
.faq-section p {
  margin-bottom: 0.5rem;
}

.faq-section code {
  background-color: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
}
</style>
