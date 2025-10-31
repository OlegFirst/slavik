'use client'

import { useState, useRef, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { SectionTabContent, SectionHeader } from '@/components/sections/SectionLayout'
import {
  Download,
  Upload,
  Save,
  Play,
  Square,
  Circle,
  ArrowRight,
  Zap,
  Users,
  MessageSquare,
  Clock,
  AlertTriangle,
  CheckCircle,
  Settings,
  Trash2,
  Copy,
  Eye,
  FileText
} from 'lucide-react'

interface BPMNElement {
  id: string
  type: 'start' | 'end' | 'task' | 'gateway' | 'event' | 'subprocess'
  label: string
  x: number
  y: number
  properties?: Record<string, any>
}

interface BPMNConnection {
  id: string
  source: string
  target: string
  label?: string
}

interface BPMNDiagram {
  id: string
  name: string
  description?: string
  elements: BPMNElement[]
  connections: BPMNConnection[]
  category: string
  lastModified: string
}

// Mock data
const mockDiagrams: BPMNDiagram[] = [
  {
    id: '1',
    name: 'Incident Response Workflow',
    description: 'Standard incident response process for BCM',
    category: 'incident',
    lastModified: '2024-01-15',
    elements: [
      { id: 'start1', type: 'start', label: 'Incident Detected', x: 50, y: 200 },
      { id: 'task1', type: 'task', label: 'Assess Severity', x: 200, y: 200 },
      { id: 'gateway1', type: 'gateway', label: 'Critical?', x: 350, y: 200 },
      { id: 'task2', type: 'task', label: 'Emergency Response', x: 500, y: 120 },
      { id: 'task3', type: 'task', label: 'Standard Response', x: 500, y: 280 },
      { id: 'end1', type: 'end', label: 'Response Complete', x: 650, y: 200 }
    ],
    connections: [
      { id: 'conn1', source: 'start1', target: 'task1' },
      { id: 'conn2', source: 'task1', target: 'gateway1' },
      { id: 'conn3', source: 'gateway1', target: 'task2', label: 'Yes' },
      { id: 'conn4', source: 'gateway1', target: 'task3', label: 'No' },
      { id: 'conn5', source: 'task2', target: 'end1' },
      { id: 'conn6', source: 'task3', target: 'end1' }
    ]
  },
  {
    id: '2',
    name: 'BCP Plan Approval',
    description: 'Business continuity plan approval workflow',
    category: 'planning',
    lastModified: '2024-01-12',
    elements: [
      { id: 'start2', type: 'start', label: 'Plan Submitted', x: 50, y: 200 },
      { id: 'task4', type: 'task', label: 'Initial Review', x: 200, y: 200 },
      { id: 'task5', type: 'task', label: 'Stakeholder Review', x: 350, y: 200 },
      { id: 'end2', type: 'end', label: 'Plan Approved', x: 500, y: 200 }
    ],
    connections: [
      { id: 'conn7', source: 'start2', target: 'task4' },
      { id: 'conn8', source: 'task4', target: 'task5' },
      { id: 'conn9', source: 'task5', target: 'end2' }
    ]
  }
]

const elementTypes = [
  { type: 'start', label: 'Start Event', icon: Circle, color: 'bg-green-100 border-green-300' },
  { type: 'end', label: 'End Event', icon: Circle, color: 'bg-red-100 border-red-300' },
  { type: 'task', label: 'Task', icon: Square, color: 'bg-blue-100 border-blue-300' },
  { type: 'gateway', label: 'Gateway', icon: Square, color: 'bg-yellow-100 border-yellow-300' },
  { type: 'event', label: 'Intermediate Event', icon: Circle, color: 'bg-orange-100 border-orange-300' },
  { type: 'subprocess', label: 'Sub Process', icon: Square, color: 'bg-purple-100 border-purple-300' }
]

export function BPMNDesigner() {
  const [selectedDiagram, setSelectedDiagram] = useState<BPMNDiagram | null>(mockDiagrams[0])
  const [selectedElement, setSelectedElement] = useState<BPMNElement | null>(null)
  const [isSimulating, setIsSimulating] = useState(false)
  const canvasRef = useRef<HTMLDivElement>(null)

  const handleElementClick = useCallback((element: BPMNElement) => {
    setSelectedElement(element)
  }, [])

  const handleSaveDiagram = () => {
    console.log('Saving diagram:', selectedDiagram)
    // Implement save logic
  }

  const handleExportDiagram = () => {
    console.log('Exporting diagram')
    // Implement export logic
  }

  const handleSimulateWorkflow = () => {
    setIsSimulating(!isSimulating)
    console.log('Simulating workflow:', isSimulating ? 'stopped' : 'started')
  }

  const renderBPMNElement = (element: BPMNElement) => {
    const elementType = elementTypes.find(t => t.type === element.type)
    if (!elementType) return null

    const Icon = elementType.icon

    return (
      <div
        key={element.id}
        className={`absolute cursor-pointer select-none transition-all duration-200 hover:scale-105 ${elementType.color} ${
          selectedElement?.id === element.id ? 'ring-2 ring-blue-500' : ''
        }`}
        style={{
          left: `${element.x}px`,
          top: `${element.y}px`,
          width: '120px',
          height: '60px'
        }}
        onClick={() => handleElementClick(element)}
      >
        <div className="w-full h-full border-2 rounded-lg p-2 flex flex-col items-center justify-center">
          <Icon className="h-4 w-4 mb-1" />
          <span className="text-xs font-medium text-center leading-tight">{element.label}</span>
        </div>
      </div>
    )
  }

  const renderConnections = () => {
    if (!selectedDiagram) return null

    return selectedDiagram.connections.map(connection => {
      const sourceElement = selectedDiagram.elements.find(e => e.id === connection.source)
      const targetElement = selectedDiagram.elements.find(e => e.id === connection.target)

      if (!sourceElement || !targetElement) return null

      const startX = sourceElement.x + 120
      const startY = sourceElement.y + 30
      const endX = targetElement.x
      const endY = targetElement.y + 30

      return (
        <svg
          key={connection.id}
          className="absolute pointer-events-none"
          style={{
            left: Math.min(startX, endX),
            top: Math.min(startY, endY) - 10,
            width: Math.abs(endX - startX) + 20,
            height: Math.abs(endY - startY) + 20
          }}
        >
          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="7"
              refX="9"
              refY="3.5"
              orient="auto"
            >
              <polygon points="0 0, 10 3.5, 0 7" fill="#374151" />
            </marker>
          </defs>
          <line
            x1={startX - Math.min(startX, endX)}
            y1={startY - Math.min(startY, endY) + 10}
            x2={endX - Math.min(startX, endX)}
            y2={endY - Math.min(startY, endY) + 10}
            stroke="#374151"
            strokeWidth="2"
            markerEnd="url(#arrowhead)"
          />
          {connection.label && (
            <text
              x={(startX + endX) / 2 - Math.min(startX, endX)}
              y={(startY + endY) / 2 - Math.min(startY, endY) + 15}
              textAnchor="middle"
              className="text-xs fill-gray-700"
            >
              {connection.label}
            </text>
          )}
        </svg>
      )
    })
  }

  return (
    <SectionTabContent>
      <SectionHeader
        title="BPMN Designer"
        description="Design and visualize business process workflows using BPMN notation"
      >
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleExportDiagram}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button variant="outline">
            <Upload className="h-4 w-4 mr-2" />
            Import
          </Button>
          <Button onClick={handleSaveDiagram}>
            <Save className="h-4 w-4 mr-2" />
            Save
          </Button>
        </div>
      </SectionHeader>

      <div className="grid grid-cols-12 gap-6 h-[800px]">
        {/* Left Sidebar - Element Palette & Diagrams */}
        <div className="col-span-3 space-y-4">
          {/* Element Palette */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Element Palette</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 gap-2">
                {elementTypes.map((elementType) => {
                  const Icon = elementType.icon
                  return (
                    <div
                      key={elementType.type}
                      className={`p-3 rounded-lg border-2 cursor-grab hover:scale-105 transition-transform ${elementType.color}`}
                      draggable
                    >
                      <div className="flex items-center space-x-2">
                        <Icon className="h-4 w-4" />
                        <span className="text-xs font-medium">{elementType.label}</span>
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          {/* Saved Diagrams */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Saved Diagrams</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {mockDiagrams.map((diagram) => (
                  <div
                    key={diagram.id}
                    className={`p-3 rounded-lg border cursor-pointer hover:bg-gray-50 ${
                      selectedDiagram?.id === diagram.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                    }`}
                    onClick={() => setSelectedDiagram(diagram)}
                  >
                    <div className="text-sm font-medium">{diagram.name}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {diagram.category} • {diagram.lastModified}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Canvas */}
        <div className="col-span-6">
          <Card className="h-full">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg">{selectedDiagram?.name || 'New Diagram'}</CardTitle>
                  <CardDescription>{selectedDiagram?.description}</CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant={isSimulating ? "destructive" : "default"}
                    size="sm"
                    onClick={handleSimulateWorkflow}
                  >
                    {isSimulating ? (
                      <>
                        <Square className="h-4 w-4 mr-2" />
                        Stop
                      </>
                    ) : (
                      <>
                        <Play className="h-4 w-4 mr-2" />
                        Simulate
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="h-[calc(100%-100px)]">
              <div
                ref={canvasRef}
                className="relative w-full h-full bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg overflow-hidden"
                style={{ minHeight: '600px' }}
              >
                {/* Grid Pattern */}
                <div
                  className="absolute inset-0 opacity-10"
                  style={{
                    backgroundImage: `
                      linear-gradient(to right, #000 1px, transparent 1px),
                      linear-gradient(to bottom, #000 1px, transparent 1px)
                    `,
                    backgroundSize: '20px 20px'
                  }}
                />

                {/* BPMN Elements */}
                {selectedDiagram?.elements.map(element => renderBPMNElement(element))}

                {/* Connections */}
                {renderConnections()}

                {/* Simulation Effects */}
                {isSimulating && (
                  <div className="absolute top-4 left-4 bg-green-100 border border-green-300 rounded-lg p-2">
                    <div className="flex items-center space-x-2">
                      <div className="animate-pulse h-2 w-2 bg-green-500 rounded-full"></div>
                      <span className="text-sm text-green-700">Simulation Running</span>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Sidebar - Properties */}
        <div className="col-span-3">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Properties</CardTitle>
            </CardHeader>
            <CardContent>
              {selectedElement ? (
                <Tabs defaultValue="general" className="w-full">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="general">General</TabsTrigger>
                    <TabsTrigger value="advanced">Advanced</TabsTrigger>
                  </TabsList>

                  <TabsContent value="general" className="space-y-4 mt-4">
                    <div>
                      <Label htmlFor="element-name">Name</Label>
                      <Input
                        id="element-name"
                        value={selectedElement.label}
                        onChange={(e) => {
                          if (selectedElement) {
                            setSelectedElement({
                              ...selectedElement,
                              label: e.target.value
                            })
                          }
                        }}
                      />
                    </div>

                    <div>
                      <Label htmlFor="element-type">Type</Label>
                      <Select value={selectedElement.type}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {elementTypes.map((type) => (
                            <SelectItem key={type.type} value={type.type}>
                              {type.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label htmlFor="element-description">Description</Label>
                      <Textarea
                        id="element-description"
                        placeholder="Element description..."
                        rows={3}
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <Label htmlFor="pos-x">X Position</Label>
                        <Input
                          id="pos-x"
                          type="number"
                          value={selectedElement.x}
                          readOnly
                        />
                      </div>
                      <div>
                        <Label htmlFor="pos-y">Y Position</Label>
                        <Input
                          id="pos-y"
                          type="number"
                          value={selectedElement.y}
                          readOnly
                        />
                      </div>
                    </div>
                  </TabsContent>

                  <TabsContent value="advanced" className="space-y-4 mt-4">
                    <div>
                      <Label htmlFor="assignee">Assignee</Label>
                      <Select>
                        <SelectTrigger>
                          <SelectValue placeholder="Select assignee" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="john">John Smith</SelectItem>
                          <SelectItem value="sarah">Sarah Johnson</SelectItem>
                          <SelectItem value="mike">Mike Davis</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label htmlFor="duration">Duration (hours)</Label>
                      <Input
                        id="duration"
                        type="number"
                        placeholder="2"
                      />
                    </div>

                    <div>
                      <Label htmlFor="priority">Priority</Label>
                      <Select>
                        <SelectTrigger>
                          <SelectValue placeholder="Select priority" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="low">Low</SelectItem>
                          <SelectItem value="medium">Medium</SelectItem>
                          <SelectItem value="high">High</SelectItem>
                          <SelectItem value="critical">Critical</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label>Actions</Label>
                      <div className="flex flex-col gap-2">
                        <Button variant="outline" size="sm">
                          <Copy className="h-4 w-4 mr-2" />
                          Duplicate
                        </Button>
                        <Button variant="outline" size="sm">
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete
                        </Button>
                      </div>
                    </div>
                  </TabsContent>
                </Tabs>
              ) : (
                <div className="text-center text-gray-500 py-8">
                  <FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">Select an element to view properties</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </SectionTabContent>
  )
}