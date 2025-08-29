<template>
  <div>
    <div
      ref="container"
      class="viewer-container"
      :style="`width:${props.width}px;height:${props.height}px;position:relative;`"
    >
      <div
        v-if="!props.plyData || isLoading"
        class="loading-overlay"
      >
        <q-spinner color="primary" size="60px" />
      </div>
    </div>

    <div
      class="controls"
    >
      <q-btn
        v-if="slicing"
        size=sm
        color=blue
      >
        Download slice
      </q-btn>

      <q-btn
        v-if="sliceable"
        size=sm
        :color="slicing ? undefined : 'blue'"
        @click="toggleSlicing"
      >
        {{ slicing ? "Cancel" : "Compute slice" }}
      </q-btn>

      <q-btn
        v-if="downloadUrl&&!slicing"
        size=sm
        color=red
      >
        Download (high resolution, xxxMB)
      </q-btn>

      <q-slider
        v-model=sliceX
        v-if=slicing
        :min=-0.3
        :max=0.3
        :step=0.01
      ></q-slider>
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
  sliceable?: boolean
  downloadUrl?: string
}

const props = withDefaults(defineProps<Props>(), {
  plyData: null,
  width: 300,
  height: 300,
  backgroundColor: '#ffffff'
})

const container = ref<HTMLDivElement>()
const isLoading = ref(false)
const slicing = ref(false)
const sliceX = ref(0)

let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let controls: OrbitControls
let mesh: THREE.Mesh
let slicePlane: THREE.Mesh
let sliceClipPlane: THREE.Plane | undefined = undefined
let animationId: number

const initThreeJS = () => {
  if (!container.value) return

  const canvasElements = container.value.querySelectorAll('canvas')
  canvasElements.forEach(canvas => canvas.remove())

  scene = new THREE.Scene()
  scene.background = new THREE.Color(props.backgroundColor)

  camera = new THREE.PerspectiveCamera(
    30,
    props.width / props.height,
    0.1,
    1000
  )

  renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
  })
  renderer.setSize(props.width, props.height)
  renderer.setPixelRatio(window.devicePixelRatio)
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.VSMShadowMap
  renderer.toneMapping = THREE.NeutralToneMapping
  renderer.toneMappingExposure = 2.5

  const loadingOverlay = container.value.querySelector('.loading-overlay')
  if (loadingOverlay) {
    container.value.insertBefore(renderer.domElement, loadingOverlay)
  } else {
    container.value.appendChild(renderer.domElement)
  }

  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.2
  controls.enablePan = false

  // Emulate ambient occlusion with multiple lights
  const lightPositions: [number, number, number][]  = [
    [1, 1, 1],
    [1, -1, -1],
    [-1, -1, 1],
    [-1, 1, -1],
  ]
  const lightIntensities = [1, 0.2, 0.2, 0.6]
  for (let i = 0; i < lightPositions.length; i++) {
    const lightPosition = lightPositions[i] as [number, number, number]
    const lightIntensity = lightIntensities[i]
    const directionalLight = new THREE.DirectionalLight(0xffffff, lightIntensity)
    directionalLight.position.set(...lightPosition)
    directionalLight.castShadow = true
    directionalLight.shadow.mapSize.width = 128
    directionalLight.shadow.mapSize.height = 128
    scene.add(directionalLight)
  }

  const slicePlaneGeometry = new THREE.PlaneGeometry(1.1, 1.1, 1, 1)
  const slicePlaneMaterial = new THREE.MeshBasicMaterial({
    color: 0xffaaaa,
    side: THREE.DoubleSide,
  })
  slicePlane = new THREE.Mesh(slicePlaneGeometry, slicePlaneMaterial)
  slicePlane.rotateY(Math.PI / 2)

  sliceClipPlane = new THREE.Plane(new THREE.Vector3(1, 0, 0), 1)
}

const loadPlyFromBuffer = () => {
  if (!props.plyData) return

  isLoading.value = true
  const loader = new PLYLoader()

  try {
    const geometry = loader.parse(props.plyData)

    if (!geometry.attributes.normal) {
      geometry.computeVertexNormals()
    }

    geometry.computeBoundingBox()
    const boundingBox = geometry.boundingBox!
    const center = boundingBox.getCenter(new THREE.Vector3())
    const size = boundingBox.getSize(new THREE.Vector3())
    const maxDim = Math.max(size.x, size.y, size.z)
    const scale = 1 / maxDim

    geometry.translate(-center.x, -center.y, -center.z)
    geometry.scale(scale, scale, scale)
    geometry.rotateX(-Math.PI / 2)
    if (size.x > size.y) {
      geometry.rotateY(Math.PI / 2)
    }
    if (size.x > size.z && size.y > size.z) {
      geometry.rotateZ(-Math.PI / 2)
    }

    const material = new THREE.MeshPhongMaterial({
      color: 0xefefee,
      specular: 0xaaaaaa,
      shininess: 5,
      flatShading: true,
    })

    mesh = new THREE.Mesh(geometry, material)
    mesh.castShadow = true
    mesh.receiveShadow = true

    scene.add(mesh)

    camera.position.set(2, 1, -1.3)
    camera.lookAt(0, 0, 0)
    controls.update()

    console.log(`PLY loaded successfully (${geometry.attributes.position?.count} vertices)`)

  } catch (error) {
    console.error('Error loading PLY:', error)
  } finally {
    isLoading.value = false
  }
}

const animate = () => {
  animationId = requestAnimationFrame(animate)

  controls.update()
  renderer.render(scene, camera)
}

const handleResize = () => {
  if (!camera || !renderer) return

  camera.aspect = props.width / props.height
  camera.updateProjectionMatrix()
  renderer.setSize(props.width, props.height)
}

const toggleSlicing = () => {
  if (!renderer || !sliceClipPlane) return
  slicing.value = !slicing.value

  if (slicing.value) {
    sliceX.value = 0
    scene.add(slicePlane)
    renderer.clippingPlanes = [sliceClipPlane]
  } else {
    scene.remove(slicePlane)
    renderer.clippingPlanes = []
  }
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
  }
  if (props.plyData) {
    loadPlyFromBuffer()
  }
})

watch(sliceX, () => {
  if (!slicePlane) return;
  slicePlane.position.x = sliceX.value
})
</script>

<style scoped>
.viewer-container {
  border: 1px solid #ccc;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 2;
  display: flex;
  justify-content: center;
  align-items: center;
  pointer-events: none;
}

.viewer-container canvas {
  display: block;
  position: relative;
  z-index: 1;
}

.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>
