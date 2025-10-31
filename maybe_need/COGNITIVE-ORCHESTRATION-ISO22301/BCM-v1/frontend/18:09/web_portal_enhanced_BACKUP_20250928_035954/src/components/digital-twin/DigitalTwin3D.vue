<template>
  <div class="digital-twin-3d-container">
    <div ref="canvasContainer" class="canvas-container"></div>

    <!-- Controls Panel -->
    <div class="controls-panel">
      <div class="control-group">
        <button @click="toggleRotation" class="control-btn">
          <i :class="isRotating ? 'fas fa-pause' : 'fas fa-play'"></i>
          {{ isRotating ? 'Pause' : 'Rotate' }}
        </button>
        <button @click="resetCamera" class="control-btn">
          <i class="fas fa-undo"></i>
          Reset View
        </button>
      </div>

      <div class="control-group">
        <label>View Mode:</label>
        <select v-model="viewMode" @change="changeViewMode">
          <option value="organization">Organization Structure</option>
          <option value="dataflow">Data Flow</option>
          <option value="risk">Risk Heatmap</option>
          <option value="simulation">Simulation State</option>
        </select>
      </div>

      <div class="control-group">
        <label>Highlight:</label>
        <select v-model="highlightMode" @change="updateHighlight">
          <option value="none">None</option>
          <option value="critical">Critical Assets</option>
          <option value="active">Active Processes</option>
          <option value="risks">Risk Points</option>
        </select>
      </div>
    </div>

    <!-- Info Panel -->
    <div class="info-panel" v-if="selectedObject">
      <h3>{{ selectedObject.name }}</h3>
      <div class="info-content">
        <div class="info-row">
          <span>Type:</span>
          <span>{{ selectedObject.type }}</span>
        </div>
        <div class="info-row">
          <span>Status:</span>
          <span :class="`status-${selectedObject.status}`">{{ selectedObject.status }}</span>
        </div>
        <div class="info-row" v-if="selectedObject.metrics">
          <span>Health:</span>
          <span>{{ selectedObject.metrics.health }}%</span>
        </div>
        <div class="info-row" v-if="selectedObject.metrics">
          <span>Load:</span>
          <span>{{ selectedObject.metrics.load }}%</span>
        </div>
      </div>
      <button @click="selectedObject = null" class="close-btn">×</button>
    </div>

    <!-- Stats Overlay -->
    <div class="stats-overlay">
      <div class="stat-item">
        <span class="stat-label">Nodes:</span>
        <span class="stat-value">{{ nodeCount }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Connections:</span>
        <span class="stat-value">{{ connectionCount }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Active:</span>
        <span class="stat-value">{{ activeCount }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'
import { CSS2DRenderer, CSS2DObject } from 'three/examples/jsm/renderers/CSS2DRenderer'
import { digitalTwinService } from '@/services/digitalTwinService'

// Props
const props = defineProps({
  data: {
    type: Object,
    default: () => ({})
  },
  height: {
    type: String,
    default: '600px'
  }
})

// Refs
const canvasContainer = ref<HTMLElement>()
const selectedObject = ref<any>(null)
const isRotating = ref(true)
const viewMode = ref('organization')
const highlightMode = ref('none')
const nodeCount = ref(0)
const connectionCount = ref(0)
const activeCount = ref(0)

// Three.js objects
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let labelRenderer: CSS2DRenderer
let controls: OrbitControls
let organizationGroup: THREE.Group
let dataFlowGroup: THREE.Group
let riskGroup: THREE.Group
let animationId: number
let raycaster: THREE.Raycaster
let mouse: THREE.Vector2
let nodes: Map<string, THREE.Mesh> = new Map()
let connections: THREE.Line[] = []

// Initialize Three.js scene
const initScene = () => {
  if (!canvasContainer.value) return

  const width = canvasContainer.value.clientWidth
  const height = canvasContainer.value.clientHeight

  // Scene
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x0a0a0a)
  scene.fog = new THREE.Fog(0x0a0a0a, 10, 50)

  // Camera
  camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000)
  camera.position.set(15, 15, 15)
  camera.lookAt(0, 0, 0)

  // Renderer
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(window.devicePixelRatio)
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFSoftShadowMap
  canvasContainer.value.appendChild(renderer.domElement)

  // CSS2D Renderer for labels
  labelRenderer = new CSS2DRenderer()
  labelRenderer.setSize(width, height)
  labelRenderer.domElement.style.position = 'absolute'
  labelRenderer.domElement.style.top = '0px'
  labelRenderer.domElement.style.pointerEvents = 'none'
  canvasContainer.value.appendChild(labelRenderer.domElement)

  // Controls
  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05
  controls.minDistance = 5
  controls.maxDistance = 50
  controls.maxPolarAngle = Math.PI / 2

  // Lights
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.3)
  scene.add(ambientLight)

  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.7)
  directionalLight.position.set(10, 20, 10)
  directionalLight.castShadow = true
  directionalLight.shadow.camera.near = 0.1
  directionalLight.shadow.camera.far = 50
  directionalLight.shadow.camera.left = -20
  directionalLight.shadow.camera.right = 20
  directionalLight.shadow.camera.top = 20
  directionalLight.shadow.camera.bottom = -20
  scene.add(directionalLight)

  // Grid
  const gridHelper = new THREE.GridHelper(30, 30, 0x444444, 0x222222)
  scene.add(gridHelper)

  // Raycaster for mouse interaction
  raycaster = new THREE.Raycaster()
  mouse = new THREE.Vector2()

  // Groups for different views
  organizationGroup = new THREE.Group()
  dataFlowGroup = new THREE.Group()
  riskGroup = new THREE.Group()

  scene.add(organizationGroup)
  scene.add(dataFlowGroup)
  scene.add(riskGroup)

  // Initially hide non-active groups
  dataFlowGroup.visible = false
  riskGroup.visible = false

  // Create initial visualization
  createOrganizationStructure()
  createDataFlow()
  createRiskVisualization()

  // Event listeners
  renderer.domElement.addEventListener('click', onMouseClick)
  renderer.domElement.addEventListener('mousemove', onMouseMove)
  window.addEventListener('resize', onWindowResize)
}

// Create organization structure visualization
const createOrganizationStructure = () => {
  // Central core (Digital Twin Brain)
  const coreGeometry = new THREE.IcosahedronGeometry(2, 1)
  const coreMaterial = new THREE.MeshPhysicalMaterial({
    color: 0x6366f1,
    emissive: 0x6366f1,
    emissiveIntensity: 0.3,
    metalness: 0.7,
    roughness: 0.3,
    clearcoat: 1,
    clearcoatRoughness: 0.1
  })
  const coreMesh = new THREE.Mesh(coreGeometry, coreMaterial)
  coreMesh.position.set(0, 3, 0)
  coreMesh.castShadow = true
  coreMesh.receiveShadow = true
  coreMesh.userData = {
    name: 'Digital Twin Core',
    type: 'Core System',
    status: 'active',
    metrics: { health: 95, load: 67 }
  }
  organizationGroup.add(coreMesh)
  nodes.set('core', coreMesh)

  // Create label for core
  const coreLabel = createLabel('Digital Twin Core')
  coreMesh.add(coreLabel)

  // Department nodes
  const departments = [
    { name: 'IT Infrastructure', position: new THREE.Vector3(8, 2, 0), color: 0x10b981 },
    { name: 'Operations', position: new THREE.Vector3(-8, 2, 0), color: 0xf59e0b },
    { name: 'Risk Management', position: new THREE.Vector3(0, 2, 8), color: 0xef4444 },
    { name: 'Compliance', position: new THREE.Vector3(0, 2, -8), color: 0x8b5cf6 },
    { name: 'HR & Training', position: new THREE.Vector3(5.7, 2, 5.7), color: 0x06b6d4 },
    { name: 'Finance', position: new THREE.Vector3(-5.7, 2, 5.7), color: 0x84cc16 },
    { name: 'Communications', position: new THREE.Vector3(5.7, 2, -5.7), color: 0xf97316 },
    { name: 'Supply Chain', position: new THREE.Vector3(-5.7, 2, -5.7), color: 0xec4899 }
  ]

  departments.forEach((dept, index) => {
    const deptGeometry = new THREE.BoxGeometry(2, 2, 2)
    const deptMaterial = new THREE.MeshPhysicalMaterial({
      color: dept.color,
      emissive: dept.color,
      emissiveIntensity: 0.2,
      metalness: 0.5,
      roughness: 0.4
    })
    const deptMesh = new THREE.Mesh(deptGeometry, deptMaterial)
    deptMesh.position.copy(dept.position)
    deptMesh.castShadow = true
    deptMesh.receiveShadow = true
    deptMesh.userData = {
      name: dept.name,
      type: 'Department',
      status: Math.random() > 0.3 ? 'active' : 'idle',
      metrics: {
        health: Math.floor(70 + Math.random() * 30),
        load: Math.floor(Math.random() * 100)
      }
    }
    organizationGroup.add(deptMesh)
    nodes.set(`dept-${index}`, deptMesh)

    // Add label
    const deptLabel = createLabel(dept.name)
    deptMesh.add(deptLabel)

    // Create connection to core
    const connection = createConnection(coreMesh.position, deptMesh.position, dept.color)
    organizationGroup.add(connection)
    connections.push(connection)
  })

  // Add sub-nodes (processes)
  nodes.forEach((node, key) => {
    if (key.startsWith('dept-')) {
      for (let i = 0; i < 3; i++) {
        const angle = (i / 3) * Math.PI * 2
        const radius = 3
        const subNodePos = new THREE.Vector3(
          node.position.x + Math.cos(angle) * radius,
          0.5,
          node.position.z + Math.sin(angle) * radius
        )

        const subGeometry = new THREE.SphereGeometry(0.3, 16, 16)
        const subMaterial = new THREE.MeshPhysicalMaterial({
          color: 0xffffff,
          emissive: 0x6366f1,
          emissiveIntensity: 0.5,
          metalness: 0.8,
          roughness: 0.2
        })
        const subMesh = new THREE.Mesh(subGeometry, subMaterial)
        subMesh.position.copy(subNodePos)
        subMesh.castShadow = true
        subMesh.userData = {
          name: `Process ${key}-${i}`,
          type: 'Process',
          status: 'active',
          metrics: { health: 100, load: Math.floor(Math.random() * 100) }
        }
        organizationGroup.add(subMesh)

        // Connection to department
        const subConnection = createConnection(node.position, subNodePos, 0x444444, 0.5)
        organizationGroup.add(subConnection)
      }
    }
  })

  nodeCount.value = nodes.size
  connectionCount.value = connections.length
  activeCount.value = Array.from(nodes.values()).filter(n => n.userData.status === 'active').length
}

// Create data flow visualization
const createDataFlow = () => {
  // Create particle system for data flow
  const particleCount = 1000
  const geometry = new THREE.BufferGeometry()
  const positions = new Float32Array(particleCount * 3)
  const colors = new Float32Array(particleCount * 3)
  const sizes = new Float32Array(particleCount)

  for (let i = 0; i < particleCount; i++) {
    const i3 = i * 3
    positions[i3] = (Math.random() - 0.5) * 30
    positions[i3 + 1] = Math.random() * 10
    positions[i3 + 2] = (Math.random() - 0.5) * 30

    colors[i3] = Math.random()
    colors[i3 + 1] = Math.random()
    colors[i3 + 2] = Math.random()

    sizes[i] = Math.random() * 2
  }

  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))
  geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1))

  const material = new THREE.PointsMaterial({
    size: 0.1,
    vertexColors: true,
    transparent: true,
    opacity: 0.8,
    blending: THREE.AdditiveBlending
  })

  const particles = new THREE.Points(geometry, material)
  dataFlowGroup.add(particles)

  // Animate particles in render loop
  particles.userData.update = () => {
    const positions = particles.geometry.attributes.position.array as Float32Array
    for (let i = 0; i < particleCount; i++) {
      const i3 = i * 3
      positions[i3 + 1] -= 0.1
      if (positions[i3 + 1] < 0) {
        positions[i3 + 1] = 10
      }
    }
    particles.geometry.attributes.position.needsUpdate = true
  }
}

// Create risk heatmap visualization
const createRiskVisualization = () => {
  const riskZones = [
    { position: new THREE.Vector3(5, 0.1, 5), risk: 0.8, size: 4 },
    { position: new THREE.Vector3(-8, 0.1, -3), risk: 0.6, size: 3 },
    { position: new THREE.Vector3(0, 0.1, -8), risk: 0.9, size: 5 },
    { position: new THREE.Vector3(-5, 0.1, 7), risk: 0.4, size: 2.5 }
  ]

  riskZones.forEach(zone => {
    const geometry = new THREE.CylinderGeometry(zone.size, zone.size, 0.2, 32)
    const material = new THREE.MeshPhysicalMaterial({
      color: new THREE.Color(zone.risk, 1 - zone.risk, 0),
      transparent: true,
      opacity: 0.3 + zone.risk * 0.4,
      emissive: new THREE.Color(zone.risk, 0, 0),
      emissiveIntensity: zone.risk
    })
    const mesh = new THREE.Mesh(geometry, material)
    mesh.position.copy(zone.position)
    mesh.userData = {
      name: `Risk Zone`,
      type: 'Risk Area',
      status: zone.risk > 0.7 ? 'critical' : zone.risk > 0.4 ? 'warning' : 'normal',
      metrics: { risk: Math.floor(zone.risk * 100) }
    }
    riskGroup.add(mesh)
  })
}

// Create connection line between nodes
const createConnection = (start: THREE.Vector3, end: THREE.Vector3, color: number = 0x6366f1, opacity: number = 1) => {
  const points = []
  points.push(start)

  // Add curve to connection
  const mid = new THREE.Vector3()
  mid.lerpVectors(start, end, 0.5)
  mid.y += 2
  points.push(mid)

  points.push(end)

  const curve = new THREE.CatmullRomCurve3(points)
  const curvePoints = curve.getPoints(50)
  const geometry = new THREE.BufferGeometry().setFromPoints(curvePoints)

  const material = new THREE.LineBasicMaterial({
    color: color,
    transparent: true,
    opacity: opacity,
    linewidth: 2
  })

  return new THREE.Line(geometry, material)
}

// Create label for nodes
const createLabel = (text: string) => {
  const div = document.createElement('div')
  div.className = 'node-label'
  div.textContent = text
  div.style.color = 'white'
  div.style.fontSize = '12px'
  div.style.padding = '2px 6px'
  div.style.background = 'rgba(0,0,0,0.6)'
  div.style.borderRadius = '3px'
  div.style.pointerEvents = 'none'

  const label = new CSS2DObject(div)
  label.position.set(0, 1.5, 0)
  return label
}

// Animation loop
const animate = () => {
  animationId = requestAnimationFrame(animate)

  // Update controls
  controls.update()

  // Rotate organization structure
  if (isRotating.value && viewMode.value === 'organization') {
    organizationGroup.rotation.y += 0.002
  }

  // Animate data flow particles
  const particles = dataFlowGroup.children.find(child => child instanceof THREE.Points)
  if (particles && particles.userData.update) {
    particles.userData.update()
  }

  // Pulse effect for active nodes
  nodes.forEach(node => {
    if (node.userData.status === 'active') {
      const scale = 1 + Math.sin(Date.now() * 0.001) * 0.05
      node.scale.setScalar(scale)
    }
  })

  // Render
  renderer.render(scene, camera)
  labelRenderer.render(scene, camera)
}

// Mouse interaction
const onMouseClick = (event: MouseEvent) => {
  const rect = renderer.domElement.getBoundingClientRect()
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1

  raycaster.setFromCamera(mouse, camera)
  const intersects = raycaster.intersectObjects(Array.from(nodes.values()))

  if (intersects.length > 0) {
    selectedObject.value = intersects[0].object.userData
  }
}

const onMouseMove = (event: MouseEvent) => {
  const rect = renderer.domElement.getBoundingClientRect()
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1

  raycaster.setFromCamera(mouse, camera)
  const intersects = raycaster.intersectObjects(Array.from(nodes.values()))

  renderer.domElement.style.cursor = intersects.length > 0 ? 'pointer' : 'default'
}

// Window resize
const onWindowResize = () => {
  if (!canvasContainer.value) return

  const width = canvasContainer.value.clientWidth
  const height = canvasContainer.value.clientHeight

  camera.aspect = width / height
  camera.updateProjectionMatrix()

  renderer.setSize(width, height)
  labelRenderer.setSize(width, height)
}

// Control functions
const toggleRotation = () => {
  isRotating.value = !isRotating.value
}

const resetCamera = () => {
  camera.position.set(15, 15, 15)
  camera.lookAt(0, 0, 0)
  controls.target.set(0, 0, 0)
  controls.update()
}

const changeViewMode = () => {
  organizationGroup.visible = viewMode.value === 'organization'
  dataFlowGroup.visible = viewMode.value === 'dataflow'
  riskGroup.visible = viewMode.value === 'risk'

  // Reset camera for different views
  if (viewMode.value === 'dataflow') {
    camera.position.set(0, 20, 20)
  } else if (viewMode.value === 'risk') {
    camera.position.set(0, 25, 0)
  } else {
    resetCamera()
  }
}

const updateHighlight = () => {
  nodes.forEach(node => {
    const material = node.material as THREE.MeshPhysicalMaterial

    if (highlightMode.value === 'none') {
      material.emissiveIntensity = 0.2
    } else if (highlightMode.value === 'critical' && node.userData.type === 'Department') {
      material.emissiveIntensity = node.userData.metrics.health < 80 ? 0.8 : 0.2
    } else if (highlightMode.value === 'active' && node.userData.status === 'active') {
      material.emissiveIntensity = 0.8
    } else if (highlightMode.value === 'risks' && node.userData.metrics?.risk > 70) {
      material.emissiveIntensity = 0.9
    } else {
      material.emissiveIntensity = 0.1
    }
  })
}

// Lifecycle
onMounted(() => {
  initScene()
  animate()

  // Subscribe to Digital Twin updates
  const unsubscribe = digitalTwinService.subscribe((state) => {
    // Update visualization based on state changes
    activeCount.value = state.blocks.filter(b => b.status === 'active').length

    // Update node colors based on block status
    state.blocks.forEach((block, index) => {
      const nodeKey = `dept-${index}`
      const node = nodes.get(nodeKey)
      if (node) {
        const material = node.material as THREE.MeshPhysicalMaterial
        if (block.status === 'error') {
          material.emissive = new THREE.Color(0xff0000)
          material.emissiveIntensity = 0.8
        } else if (block.status === 'processing') {
          material.emissive = new THREE.Color(0xffff00)
          material.emissiveIntensity = 0.6
        } else if (block.status === 'active') {
          material.emissive = new THREE.Color(0x00ff00)
          material.emissiveIntensity = 0.4
        }
      }
    })
  })

  onUnmounted(() => {
    unsubscribe()
  })
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }

  // Clean up Three.js resources
  scene?.traverse((object) => {
    if (object instanceof THREE.Mesh) {
      object.geometry.dispose()
      if (object.material instanceof THREE.Material) {
        object.material.dispose()
      }
    }
  })

  renderer?.dispose()
  controls?.dispose()
})
</script>

<style scoped lang="scss">
.digital-twin-3d-container {
  position: relative;
  width: 100%;
  height: 600px;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
  border-radius: 12px;
  overflow: hidden;
}

.canvas-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.controls-panel {
  position: absolute;
  top: 20px;
  left: 20px;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  padding: 15px;
  border-radius: 8px;
  color: white;
  z-index: 10;

  .control-group {
    margin-bottom: 15px;

    &:last-child {
      margin-bottom: 0;
    }

    label {
      display: block;
      font-size: 0.85rem;
      margin-bottom: 5px;
      color: #888;
    }

    select {
      width: 100%;
      padding: 5px 10px;
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.2);
      border-radius: 4px;
      color: white;
      cursor: pointer;

      option {
        background: #1a1a2e;
      }
    }
  }

  .control-btn {
    padding: 8px 12px;
    margin-right: 10px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    border: none;
    border-radius: 6px;
    color: white;
    cursor: pointer;
    font-size: 0.85rem;
    transition: all 0.3s;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }

    i {
      margin-right: 5px;
    }
  }
}

.info-panel {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 280px;
  background: rgba(0, 0, 0, 0.9);
  backdrop-filter: blur(10px);
  padding: 20px;
  border-radius: 8px;
  color: white;
  z-index: 10;

  h3 {
    margin: 0 0 15px 0;
    font-size: 1.2rem;
    color: #667eea;
  }

  .info-content {
    .info-row {
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);

      &:last-child {
        border-bottom: none;
      }

      span:first-child {
        color: #888;
        font-size: 0.9rem;
      }

      span:last-child {
        font-weight: 500;
      }

      .status-active {
        color: #10b981;
      }

      .status-idle {
        color: #f59e0b;
      }

      .status-error {
        color: #ef4444;
      }

      .status-critical {
        color: #ff0000;
        font-weight: bold;
      }

      .status-warning {
        color: #ffaa00;
      }

      .status-normal {
        color: #00ff00;
      }
    }
  }

  .close-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    background: transparent;
    border: none;
    color: white;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s;

    &:hover {
      color: #ef4444;
      transform: rotate(90deg);
    }
  }
}

.stats-overlay {
  position: absolute;
  bottom: 20px;
  left: 20px;
  display: flex;
  gap: 20px;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  padding: 10px 15px;
  border-radius: 8px;
  z-index: 10;

  .stat-item {
    display: flex;
    align-items: center;
    gap: 8px;

    .stat-label {
      color: #888;
      font-size: 0.85rem;
    }

    .stat-value {
      color: #667eea;
      font-weight: bold;
      font-size: 1.1rem;
    }
  }
}

:deep(.node-label) {
  user-select: none;
  white-space: nowrap;
  font-family: 'Inter', sans-serif;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
}
</style>