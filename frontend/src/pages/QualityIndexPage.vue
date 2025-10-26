<template>
  <q-page class="q-pa-md">
    <q-card class="q-pa-md">
      <div class="text-h4">Masonry Quality Index computation</div>

      <q-expansion-item
        class="q-mt-md"
        label="What is the Masonry Quality Index?"
        icon="info"
        expand-separator
      >
        <div class="q-pa-md">
          <p>
            The Masonry Quality Index (MQI), first proposed by Borri and De Maria in
            2002 and refined in later studies, is used to assess the quality of
            masonry in existing buildings and guide restoration efforts. The method
            evaluates seven key parameters:
          </p>

          <section>
            <div class="text-h5 q-mt-md q-mb-sm">Key Parameters</div>
            <ul>
              <li>
                <strong>Five related to microstructure:</strong> Stone shape, size,
                vertical joint staggering, horizontal bed joint characteristics, and
                wall leaf connections.
              </li>
              <li>
                <strong>Two related to mechanical properties:</strong> Mortar
                strength and stone strength.
              </li>
            </ul>
          </section>

          <section>
            <div class="text-h5 q-mt-md q-mb-sm">Classification</div>
            <p>Each parameter is classified as:</p>
            <ul>
              <li>Fulfilled (F)</li>
              <li>Partially Fulfilled (PF)</li>
              <li>Not Fulfilled (NF)</li>
            </ul>
            <p>
              Based on the classification, a numerical value is assigned to each
              parameter, considering different loading conditions (vertical,
              in-plane, or out-of-plane). The MQI score ranges from 0 to 10, with
              higher scores indicating better quality.
            </p>
          </section>

          <section>
            <div class="text-h5 q-mt-md q-mb-sm">Categories Based on MQI Score</div>
            <ul>
              <li>Category A: Good behavior</li>
              <li>Category B: Average quality</li>
              <li>Category C: Inadequate behavior</li>
            </ul>
          </section>

          <section class="references">
            <div class="text-h5 q-mt-md q-mb-sm">References</div>
            <ul>
              <li>
                Regione dell’Umbria (2003).
                <em
                  >Norme tecniche per la progettazione degli interventi e la
                  realizzazione delle opere di cui alla L.R. 23.10.2002 No. 18
                  finalizzate alla riduzione della vulnerabilità sismica</em
                >. Regione dell’Umbria, Italy.
              </li>
              <li>
                Borri, A. &amp; De Maria, A.D. (2009).
                <em>“L’indice di Qualità Muraria (IQM): Evoluzione ed Applicazione
                  nell’Ambito delle Norme Tecniche per le Costruzioni del 2008”</em>. In: Proceedings of the 13th Italian National Conference for
                Earthquake Engineering. Bologna, Italy.
              </li>
              <li>
                Borri, A., Corradi, M., Castori, G., &amp; De Maria, A.D. (2015).
                <em>“A method for the analysis and classification of historic masonry”</em>. In:
                <em>Bulletin of Earthquake Engineering</em>, 13(9), 2647–2665. ISSN:
                1570-761X.
              </li>
              <li>
                Borri, A., Corradi, M., De Maria, A., &amp; Sisti, R. (2018).
                <em>“Calibration of a visual method for the analysis of the mechanical properties of historic masonry”</em>. In:
                <em>Procedia Structural Integrity</em>, 11. XIV International
                Conference on Building Pathology and Construction Repair, Florence,
                Italy, June 20–22, 2018, 418–427. ISSN: 2452-3216.
              </li>
              <li>
                Borri, A., Corradi, M., &amp; De Maria, A.D. (2020).
                <em>“The Failure of Masonry Walls by Disaggregation and the Masonry Quality Index”</em>. In: <em>Heritage</em>, 3(4), 1162–1198. ISSN: 2571-9408.
              </li>
            </ul>
          </section>
        </div>
      </q-expansion-item>
      <quality-index-wizard />
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import QualityIndexWizard from '../components/qualityIndex/QualityIndexWizard.vue'
</script>
