<template>
  <div class="ply-viewer">
    <div
      ref="container"
      class="viewer-container"
      :style="`width:${props.width}px;height:${props.height}px;position:relative;`"
    >
      <!-- Move loading overlay outside or ensure it's rendered after canvas -->
      <div
        v-if="!props.plyData || isLoading"
        class="loading-overlay"
      >
        <q-spinner color="primary" size="60px" />
      </div>
    </div>
    <div class="controls">
      <q-btn @click="resetCamera" color="primary" size="sm">Reset View</q-btn>
      <q-btn @click="toggleWireframe" color="secondary" size="sm">
        {{ wireframe ? 'Solid' : 'Wireframe' }}
      </q-btn>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as THREE from 'three'
import { PLYLoader } from 'three/examples/jsm/loaders/PLYLoader.js'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

interface Props {
  plyData?: ArrayBuffer | null
  width?: number
  height?: number
  backgroundColor?: string
}

const props = withDefaults(defineProps<Props>(), {
  width: 800,
  height: 600,
  backgroundColor: '#f0f0f0'
})

const container = ref<HTMLDivElement>()
const wireframe = ref(false)
const isLoading = ref(false) // Add loading state

let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let controls: OrbitControls
let mesh: THREE.Mesh
let animationId: number

const initThreeJS = () => {
  if (!container.value) return

  // Remove previous renderer if any
  const canvasElements = container.value.querySelectorAll('canvas')
  canvasElements.forEach(canvas => canvas.remove())

  scene = new THREE.Scene()
  scene.background = new THREE.Color(props.backgroundColor)

  camera = new THREE.PerspectiveCamera(
    75,
    props.width / props.height,
    0.1,
    1000
  )

  renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true
  })
  renderer.setSize(props.width, props.height)
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFSoftShadowMap

  // Insert canvas before loading overlay to maintain z-index order
  const loadingOverlay = container.value.querySelector('.loading-overlay')
  if (loadingOverlay) {
    container.value.insertBefore(renderer.domElement, loadingOverlay)
  } else {
    container.value.appendChild(renderer.domElement)
  }

  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05

  const ambientLight = new THREE.AmbientLight(0x404040, 0.6)
  scene.add(ambientLight)

  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
  directionalLight.position.set(10, 10, 5)
  directionalLight.castShadow = true
  directionalLight.shadow.mapSize.width = 1024
  directionalLight.shadow.mapSize.height = 1024
  scene.add(directionalLight)

  const pointLight = new THREE.PointLight(0xffffff, 0.5)
  pointLight.position.set(-10, 10, 10)
  scene.add(pointLight)
}

const loadPlyFromBuffer = async () => {
  if (!props.plyData) return

  isLoading.value = true // Set loading state
  const loader = new PLYLoader()

  try {
    // Add a small delay to ensure the spinner shows
    await new Promise(resolve => setTimeout(resolve, 100))

    const geometry = loader.parse(props.plyData)

    if (!geometry.attributes.normal) {
      geometry.computeVertexNormals()
    }

    // Center and scale the geometry
    geometry.computeBoundingBox()
    const boundingBox = geometry.boundingBox!
    const center = boundingBox.getCenter(new THREE.Vector3())
    const size = boundingBox.getSize(new THREE.Vector3())
    const maxDim = Math.max(size.x, size.y, size.z)
    const scale = 5 / maxDim // Scale to fit in a 5-unit cube

    geometry.translate(-center.x, -center.y, -center.z)
    geometry.scale(scale, scale, scale)

    const material = new THREE.MeshPhongMaterial({
      color: 0x888888,
      side: THREE.DoubleSide,
      flatShading: false
    })

    mesh = new THREE.Mesh(geometry, material)
    mesh.castShadow = true
    mesh.receiveShadow = true

    scene.add(mesh)

    camera.position.set(8, 8, 8)
    camera.lookAt(0, 0, 0)
    controls.update()

    console.log('PLY loaded successfully')
    console.log('Vertices:', geometry.attributes.position.count)

  } catch (error) {
    console.error('Error loading PLY:', error)
  } finally {
    isLoading.value = false // Clear loading state
  }
}

const animate = () => {
  animationId = requestAnimationFrame(animate)

  controls.update()
  renderer.render(scene, camera)
}

const resetCamera = () => {
  camera.position.set(8, 8, 8)
  camera.lookAt(0, 0, 0)
  controls.reset()
}

const toggleWireframe = () => {
  wireframe.value = !wireframe.value
  if (mesh && mesh.material instanceof THREE.MeshPhongMaterial) {
    mesh.material.wireframe = wireframe.value
  }
}

const handleResize = () => {
  if (!camera || !renderer) return

  camera.aspect = props.width / props.height
  camera.updateProjectionMatrix()
  renderer.setSize(props.width, props.height)
}

onMounted(() => {
  initThreeJS()
  if (props.plyData) {
    loadPlyFromBuffer()
  }
  animate()

  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)

  if (animationId) {
    cancelAnimationFrame(animationId)
  }

  if (renderer) {
    const canvas = container.value?.querySelector('canvas')
    if (canvas) {
      container.value?.removeChild(canvas)
    }
    renderer.dispose()
  }

  if (controls) {
    controls.dispose()
  }
})

watch(() => props.plyData, () => {
  if (scene && mesh) {
    scene.remove(mesh)
    mesh.geometry.dispose()
    // @ts-ignore
    mesh.material.dispose()
    mesh = undefined as any
  }
  if (props.plyData) {
    loadPlyFromBuffer()
  }
})
</script>

<style scoped>
.ply-viewer {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.viewer-container {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1000; /* Increased z-index */
  display: flex;
  justify-content: center;
  align-items: center;
  background: rgba(255, 255, 255, 0.8); /* More opaque background */
  pointer-events: none;
  backdrop-filter: blur(2px); /* Optional: adds a blur effect */
}

.controls {
  display: flex;
  gap: 8px;
}

.viewer-container canvas {
  display: block;
  position: relative;
  z-index: 1; /* Lower z-index than overlay */
}
</style>
