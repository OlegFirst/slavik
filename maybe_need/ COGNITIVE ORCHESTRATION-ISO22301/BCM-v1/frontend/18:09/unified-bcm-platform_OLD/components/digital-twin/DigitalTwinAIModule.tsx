'use client'

import React, { useState, useEffect, useRef } from 'react'
import * as THREE from 'three'
import { 
  Brain, 
  Shield, 
  Users, 
  Zap, 
  MessageSquare, 
  Settings, 
  Play, 
  BarChart3,
  AlertTriangle,
  CheckCircle,
  X,
  Send,
  Lightbulb,
  Activity,
  Cpu,
  Database
} from 'lucide-react'

// AI Digital Twin Combined Module
const DigitalTwinAIModule = () => {
  // State management
  const [activeTab, setActiveTab] = useState('3d-view')
  const [loading, setLoading] = useState({
    recommendations: false,
    riskAnalysis: false,
    chat: false,
    tools: false,
    simulation: false
  })

  // AI Metrics
  const [aiMetrics, setAiMetrics] = useState({
    analysisCount: 47,
    recommendations: 12,
    automationTasks: 8,
    riskScore: 73
  })

  // AI Recommendations
  const [recommendations, setRecommendations] = useState([
    {
      id: 1,
      type: 'risk_mitigation',
      priority: 'high',
      title: 'Update Incident Response Procedures',
      description: 'AI detected gaps in your current incident response procedures. Consider updating contact lists and escalation protocols.'
    },
    {
      id: 2,
      type: 'training',
      priority: 'medium',
      title: 'Schedule BCP Training',
      description: 'Based on staff turnover analysis, 23% of your team needs refresher training on business continuity procedures.'
    }
  ])

  // Risk Analysis
  const [riskAnalysis, setRiskAnalysis] = useState({
    overall_risk: 'Medium',
    critical_risks: 3,
    mitigation_actions: 8,
    categories: [
      { name: 'IT Infrastructure', level: 'High', score: 85, color: 'bg-red-500' },
      { name: 'Supply Chain', level: 'Medium', score: 60, color: 'bg-yellow-500' },
      { name: 'Human Resources', level: 'Low', score: 30, color: 'bg-green-500' }
    ]
  })

  // Chat System
  const [chatMessages, setChatMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      text: 'Hello! I\'m your AI assistant for Digital Twin management. How can I help you today?',
      timestamp: new Date()
    }
  ])
  const [newMessage, setNewMessage] = useState('')

  // 3D Scene
  const mountRef = useRef<HTMLDivElement>(null)
  const sceneRef = useRef<THREE.Scene>()
  const rendererRef = useRef<THREE.WebGLRenderer>()
  const cameraRef = useRef<THREE.PerspectiveCamera>()
  const animationRef = useRef<number>()

  // Digital Twin Nodes
  const [digitalTwinNodes, setDigitalTwinNodes] = useState([
    { id: 'node1', name: 'Main Server', status: 'healthy', x: 0, y: 0, z: 0, type: 'server' },
    { id: 'node2', name: 'Database', status: 'warning', x: 3, y: 0, z: 0, type: 'database' },
    { id: 'node3', name: 'Network Hub', status: 'healthy', x: -3, y: 0, z: 0, type: 'network' },
    { id: 'node4', name: 'Backup System', status: 'healthy', x: 0, y: 0, z: 3, type: 'backup' },
    { id: 'node5', name: 'Security Layer', status: 'critical', x: 0, y: 3, z: 0, type: 'security' }
  ])

  // Initialize 3D Scene
  useEffect(() => {
    if (!mountRef.current) return

    // Scene setup
    const scene = new THREE.Scene()
    scene.background = new THREE.Color(0x0a0a0a)
    sceneRef.current = scene

    // Camera
    const camera = new THREE.PerspectiveCamera(75, 1, 0.1, 1000)
    camera.position.set(8, 6, 8)
    camera.lookAt(0, 0, 0)
    cameraRef.current = camera

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    renderer.setSize(600, 400)
    renderer.shadowMap.enabled = true
    renderer.shadowMap.type = THREE.PCFSoftShadowMap
    rendererRef.current = renderer
    mountRef.current.appendChild(renderer.domElement)

    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 0.6)
    scene.add(ambientLight)

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1)
    directionalLight.position.set(10, 10, 5)
    directionalLight.castShadow = true
    scene.add(directionalLight)

    // Create Digital Twin Nodes
    digitalTwinNodes.forEach(node => {
      const geometry = new THREE.BoxGeometry(1, 1, 1)
      
      let color = 0x00ff00 // Green for healthy
      if (node.status === 'warning') color = 0xffff00 // Yellow
      if (node.status === 'critical') color = 0xff0000 // Red
      
      const material = new THREE.MeshPhongMaterial({ 
        color, 
        transparent: true, 
        opacity: 0.8 
      })
      
      const cube = new THREE.Mesh(geometry, material)
      cube.position.set(node.x, node.y, node.z)
      cube.castShadow = true
      cube.receiveShadow = true
      cube.userData = { nodeId: node.id, name: node.name }
      
      scene.add(cube)

      // Add node label
      const canvas = document.createElement('canvas')
      const context = canvas.getContext('2d')!
      context.font = '48px Arial'
      context.fillStyle = 'white'
      context.fillText(node.name, 0, 48)
      
      const texture = new THREE.CanvasTexture(canvas)
      const spriteMaterial = new THREE.SpriteMaterial({ map: texture })
      const sprite = new THREE.Sprite(spriteMaterial)
      sprite.position.set(node.x, node.y + 1.5, node.z)
      sprite.scale.set(2, 1, 1)
      scene.add(sprite)
    })

    // Grid
    const gridHelper = new THREE.GridHelper(20, 20, 0x444444, 0x444444)
    scene.add(gridHelper)

    // Animation loop
    const animate = () => {
      animationRef.current = requestAnimationFrame(animate)
      
      // Rotate nodes slightly
      scene.children.forEach(child => {
        if (child instanceof THREE.Mesh && child.userData.nodeId) {
          child.rotation.y += 0.005
        }
      })

      renderer.render(scene, camera)
    }
    animate()

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement)
      }
      renderer.dispose()
    }
  }, [digitalTwinNodes])

  // AI Functions
  const implementRecommendation = (id: number) => {
    setRecommendations(prev => prev.filter(r => r.id !== id))
    setAiMetrics(prev => ({ ...prev, recommendations: prev.recommendations - 1 }))
    
    setChatMessages(prev => [...prev, {
      id: Date.now(),
      type: 'system',
      text: 'Recommendation implemented successfully! System is updating...',
      timestamp: new Date()
    }])
  }

  const dismissRecommendation = (id: number) => {
    setRecommendations(prev => prev.filter(r => r.id !== id))
    setAiMetrics(prev => ({ ...prev, recommendations: prev.recommendations - 1 }))
  }

  const sendMessage = async () => {
    if (!newMessage.trim()) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      text: newMessage,
      timestamp: new Date()
    }
    setChatMessages(prev => [...prev, userMessage])
    
    const messageText = newMessage
    setNewMessage('')
    setLoading(prev => ({ ...prev, chat: true }))

    // Simulate AI response
    setTimeout(() => {
      const responses = [
        'Based on your Digital Twin analysis, I recommend checking the security layer status.',
        'I notice some anomalies in your infrastructure. Would you like me to run a diagnostic?',
        'Your system health looks good overall. The database warning needs attention.',
        'I can help optimize your Digital Twin configuration. Shall I suggest improvements?',
        'The 3D visualization shows potential bottlenecks. Let me analyze the data flow.'
      ]
      
      const aiResponse = {
        id: Date.now() + 1,
        type: 'assistant',
        text: responses[Math.floor(Math.random() * responses.length)],
        timestamp: new Date()
      }
      setChatMessages(prev => [...prev, aiResponse])
      setLoading(prev => ({ ...prev, chat: false }))
    }, 1500)
  }

  const runAITool = async (toolName: string) => {
    setLoading(prev => ({ ...prev, tools: true }))

    const toolResults = {
      'risk-assessment': 'Risk assessment completed. Found 3 high-priority risks in Digital Twin infrastructure.',
      'scenario-generator': 'Generated 5 new failure scenarios based on your Digital Twin topology.',
      'optimizer': 'Digital Twin optimization complete. Identified 12 performance improvements.',
      'compliance': 'Compliance check finished. Digital Twin meets 94% of BCM requirements.'
    }

    setTimeout(() => {
      setChatMessages(prev => [...prev, {
        id: Date.now(),
        type: 'system',
        text: toolResults[toolName] || 'Tool execution completed.',
        timestamp: new Date()
      }])
      setLoading(prev => ({ ...prev, tools: false }))
    }, 2000)
  }

  const startSimulation = async () => {
    setLoading(prev => ({ ...prev, simulation: true }))
    
    setChatMessages(prev => [...prev, {
      id: Date.now(),
      type: 'system',
      text: 'Starting Digital Twin simulation... Analyzing system behavior under stress conditions.',
      timestamp: new Date()
    }])

    // Simulate node status changes
    setTimeout(() => {
      setDigitalTwinNodes(prev => prev.map(node => ({
        ...node,
        status: Math.random() > 0.7 ? 'warning' : Math.random() > 0.9 ? 'critical' : 'healthy'
      })))
      
      setChatMessages(prev => [...prev, {
        id: Date.now(),
        type: 'system',
        text: 'Simulation completed. Digital Twin responded to stress test. Check 3D view for updates.',
        timestamp: new Date()
      }])
      
      setLoading(prev => ({ ...prev, simulation: false }))
    }, 3000)
  }

  const formatTime = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200'
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'low': return 'bg-green-100 text-green-800 border-green-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'High': return 'text-red-600'
      case 'Medium': return 'text-yellow-600'
      case 'Low': return 'text-green-600'
      default: return 'text-gray-600'
    }
  }

  return (
    <div className="digital-twin-ai-module min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 text-white">
      {/* Header */}
      <div className="border-b border-blue-800 bg-black/20 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Brain className="h-8 w-8 text-blue-400" />
              <div>
                <h1 className="text-2xl font-bold">Digital Twin AI Module</h1>
                <p className="text-blue-300 text-sm">AI-Powered 3D Organization Intelligence</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-6 text-sm">
                <div className="flex items-center space-x-2">
                  <Activity className="h-4 w-4 text-green-400" />
                  <span>System Active</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Cpu className="h-4 w-4 text-blue-400" />
                  <span>{aiMetrics.analysisCount} Analyses</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Lightbulb className="h-4 w-4 text-yellow-400" />
                  <span>{aiMetrics.recommendations} Recommendations</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-blue-800">
        <div className="container mx-auto px-6">
          <nav className="flex space-x-8">
            {[
              { id: '3d-view', label: '3D Digital Twin', icon: Cpu },
              { id: 'ai-insights', label: 'AI Insights', icon: Brain },
              { id: 'risk-analysis', label: 'Risk Analysis', icon: Shield },
              { id: 'simulation', label: 'Simulation', icon: Play }
            ].map(tab => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-2 border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-400 text-blue-400'
                      : 'border-transparent text-gray-400 hover:text-white'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.label}</span>
                </button>
              )
            })}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left Panel - Main Content */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* 3D Digital Twin View */}
            {activeTab === '3d-view' && (
              <div className="bg-black/40 backdrop-blur-sm rounded-xl border border-blue-800 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold flex items-center">
                    <Cpu className="h-5 w-5 mr-2 text-blue-400" />
                    3D Digital Twin Visualization
                  </h2>
                  <button
                    onClick={startSimulation}
                    disabled={loading.simulation}
                    className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50"
                  >
                    <Play className="h-4 w-4" />
                    <span>{loading.simulation ? 'Running...' : 'Start Simulation'}</span>
                  </button>
                </div>
                
                <div ref={mountRef} className="bg-black/60 rounded-lg overflow-hidden border border-blue-700" />
                
                <div className="mt-4 grid grid-cols-2 md:grid-cols-5 gap-4">
                  {digitalTwinNodes.map(node => (
                    <div key={node.id} className="bg-black/60 p-3 rounded-lg border border-blue-700">
                      <div className="flex items-center space-x-2 mb-1">
                        <div className={`w-2 h-2 rounded-full ${
                          node.status === 'healthy' ? 'bg-green-400' :
                          node.status === 'warning' ? 'bg-yellow-400' : 'bg-red-400'
                        }`} />
                        <span className="text-sm font-medium">{node.name}</span>
                      </div>
                      <p className="text-xs text-gray-400 capitalize">{node.status}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* AI Insights */}
            {activeTab === 'ai-insights' && (
              <div className="space-y-6">
                {/* AI Recommendations */}
                <div className="bg-black/40 backdrop-blur-sm rounded-xl border border-blue-800 p-6">
                  <h2 className="text-xl font-semibold mb-4 flex items-center">
                    <Lightbulb className="h-5 w-5 mr-2 text-yellow-400" />
                    AI Recommendations
                  </h2>
                  
                  {recommendations.length === 0 ? (
                    <div className="text-center py-8 text-gray-400">
                      <Lightbulb className="h-12 w-12 mx-auto mb-3 opacity-50" />
                      <p>No AI recommendations at this time</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {recommendations.map(rec => (
                        <div key={rec.id} className={`p-4 rounded-lg border-2 ${getPriorityColor(rec.priority)}`}>
                          <div className="flex items-start justify-between mb-2">
                            <div>
                              <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(rec.priority)}`}>
                                {rec.priority.toUpperCase()}
                              </span>
                            </div>
                          </div>
                          <h3 className="font-semibold text-gray-900 mb-2">{rec.title}</h3>
                          <p className="text-gray-600 text-sm mb-3">{rec.description}</p>
                          <div className="flex space-x-2">
                            <button
                              onClick={() => implementRecommendation(rec.id)}
                              className="flex items-center space-x-1 px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                            >
                              <CheckCircle className="h-3 w-3" />
                              <span>Implement</span>
                            </button>
                            <button
                              onClick={() => dismissRecommendation(rec.id)}
                              className="flex items-center space-x-1 px-3 py-1 bg-gray-600 text-white rounded text-sm hover:bg-gray-700"
                            >
                              <X className="h-3 w-3" />
                              <span>Dismiss</span>
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Risk Analysis */}
            {activeTab === 'risk-analysis' && (
              <div className="bg-black/40 backdrop-blur-sm rounded-xl border border-blue-800 p-6">
                <h2 className="text-xl font-semibold mb-6 flex items-center">
                  <Shield className="h-5 w-5 mr-2 text-red-400" />
                  AI Risk Analysis
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                  <div className="bg-black/60 p-4 rounded-lg text-center">
                    <div className={`text-2xl font-bold ${getRiskColor(riskAnalysis.overall_risk)}`}>
                      {riskAnalysis.overall_risk}
                    </div>
                    <div className="text-sm text-gray-400">Overall Risk Level</div>
                  </div>
                  <div className="bg-black/60 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-red-400">{riskAnalysis.critical_risks}</div>
                    <div className="text-sm text-gray-400">Critical Risks</div>
                  </div>
                  <div className="bg-black/60 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-blue-400">{riskAnalysis.mitigation_actions}</div>
                    <div className="text-sm text-gray-400">Mitigation Actions</div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="font-semibold">Risk Categories</h3>
                  {riskAnalysis.categories.map(category => (
                    <div key={category.name} className="bg-black/60 p-4 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium">{category.name}</span>
                        <span className={`font-semibold ${getRiskColor(category.level)}`}>
                          {category.level}
                        </span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${category.color}`}
                          style={{ width: `${category.score}%` }}
                        />
                      </div>
                      <div className="text-xs text-gray-400 mt-1">{category.score}% risk level</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Simulation */}
            {activeTab === 'simulation' && (
              <div className="bg-black/40 backdrop-blur-sm rounded-xl border border-blue-800 p-6">
                <h2 className="text-xl font-semibold mb-6 flex items-center">
                  <Play className="h-5 w-5 mr-2 text-green-400" />
                  Digital Twin Simulation
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <button
                    onClick={() => startSimulation()}
                    disabled={loading.simulation}
                    className="bg-black/60 p-6 rounded-lg border border-blue-700 hover:border-blue-500 transition-colors disabled:opacity-50"
                  >
                    <Play className="h-8 w-8 text-green-400 mb-2" />
                    <h3 className="font-semibold mb-2">Stress Test</h3>
                    <p className="text-sm text-gray-400">Simulate high load conditions</p>
                  </button>
                  
                  <button
                    onClick={() => runAITool('scenario-generator')}
                    disabled={loading.tools}
                    className="bg-black/60 p-6 rounded-lg border border-blue-700 hover:border-blue-500 transition-colors disabled:opacity-50"
                  >
                    <BarChart3 className="h-8 w-8 text-blue-400 mb-2" />
                    <h3 className="font-semibold mb-2">Scenario Generator</h3>
                    <p className="text-sm text-gray-400">Generate failure scenarios</p>
                  </button>
                </div>

                <div className="mt-6 bg-black/60 p-4 rounded-lg">
                  <h3 className="font-semibold mb-2 flex items-center">
                    <Activity className="h-4 w-4 mr-2" />
                    Simulation Status
                  </h3>
                  <div className="text-sm text-gray-400">
                    {loading.simulation ? (
                      <div className="flex items-center">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-400 mr-2"></div>
                        Running simulation...
                      </div>
                    ) : (
                      'Ready to start simulation'
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right Panel - AI Assistant & Tools */}
          <div className="space-y-6">
            
            {/* AI Chat Assistant */}
            <div className="bg-black/40 backdrop-blur-sm rounded-xl border border-blue-800">
              <div className="p-4 border-b border-blue-800">
                <h3 className="font-semibold flex items-center">
                  <MessageSquare className="h-4 w-4 mr-2 text-green-400" />
                  AI Assistant
                </h3>
              </div>
              
              <div className="h-80 overflow-y-auto p-4 space-y-3">
                {chatMessages.map(message => (
                  <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-xs px-3 py-2 rounded-lg ${
                      message.type === 'user' 
                        ? 'bg-blue-600 text-white' 
                        : message.type === 'system'
                        ? 'bg-green-600 text-white'
                        : 'bg-gray-700 text-white'
                    }`}>
                      <p className="text-sm">{message.text}</p>
                      <p className="text-xs opacity-70 mt-1">{formatTime(message.timestamp)}</p>
                    </div>
                  </div>
                ))}
                {loading.chat && (
                  <div className="flex justify-start">
                    <div className="bg-gray-700 px-3 py-2 rounded-lg">
                      <div className="flex items-center space-x-1">
                        <div className="animate-pulse h-2 w-2 bg-blue-400 rounded-full"></div>
                        <div className="animate-pulse h-2 w-2 bg-blue-400 rounded-full delay-100"></div>
                        <div className="animate-pulse h-2 w-2 bg-blue-400 rounded-full delay-200"></div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="p-4 border-t border-blue-800">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Ask AI about your Digital Twin..."
                    className="flex-1 bg-black/60 border border-gray-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400"
                    disabled={loading.chat}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={loading.chat || !newMessage.trim()}
                    className="px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50"
                  >
                    <Send className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>

            {/* AI Tools */}
            <div className="bg-black/40 backdrop-blur-sm rounded-xl border border-blue-800 p-4">
              <h3 className="font-semibold mb-4 flex items-center">
                <Settings className="h-4 w-4 mr-2 text-gray-400" />
                AI Tools
              </h3>
              
              <div className="grid grid-cols-2 gap-3">
                {[
                  { id: 'risk-assessment', label: 'Risk Assessment', icon: Shield },
                  { id: 'optimizer', label: 'Optimizer', icon: Zap },
                  { id: 'compliance', label: 'Compliance', icon: CheckCircle },
                  { id: 'scenario-generator', label: 'Scenarios', icon: BarChart3 }
                ].map(tool => {
                  const Icon = tool.icon
                  return (
                    <button
                      key={tool.id}
                      onClick={() => runAITool(tool.id)}
                      disabled={loading.tools}
                      className="flex flex-col items-center space-y-2 p-3 bg-black/60 hover:bg-black/80 rounded-lg transition-colors disabled:opacity-50 border border-gray-700 hover:border-gray-600"
                    >
                      <Icon className="h-5 w-5 text-blue-400" />
                      <span className="text-xs text-center">{tool.label}</span>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* System Metrics */}
            <div className="bg-black/40 backdrop-blur-sm rounded-xl border border-blue-800 p-4">
              <h3 className="font-semibold mb-4 flex items-center">
                <BarChart3 className="h-4 w-4 mr-2 text-blue-400" />
                System Metrics
              </h3>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">AI Analyses</span>
                  <span className="text-sm font-semibold">{aiMetrics.analysisCount}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">Active Recommendations</span>
                  <span className="text-sm font-semibold">{aiMetrics.recommendations}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">Automation Tasks</span>
                  <span className="text-sm font-semibold">{aiMetrics.automationTasks}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">Risk Score</span>
                  <span className={`text-sm font-semibold ${getRiskColor('Medium')}`}>
                    {aiMetrics.riskScore}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DigitalTwinAIModule