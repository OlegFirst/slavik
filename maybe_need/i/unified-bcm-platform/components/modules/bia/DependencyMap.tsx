'use client'

import React, { useState, useEffect, useRef } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import { useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import {
  Download,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Filter,
  Search,
  AlertTriangle,
  Info,
  Settings,
  Eye,
  EyeOff
} from 'lucide-react'
import {
  biaAPI,
  biaQueryKeys,
  type DependencyMapping,
  type BIAResult
} from '@/services/bia-api'

// Types for the force graph
interface GraphNode {
  id: string
  name: string
  department: string
  criticalityLevel: 'critical' | 'high' | 'medium' | 'low'
  rto: number
  rpo: number
  financialImpactPerHour: number
  dependencies: string[]
  color: string
  size: number
  x?: number
  y?: number
  fx?: number
  fy?: number
}

interface GraphLink {
  source: string
  target: string
  dependencyType: 'critical' | 'important' | 'optional'
  description: string
  impactLevel: number
  color: string
  width: number
}

interface CascadingFailure {
  triggeredBy: string
  affectedFunctions: string[]
  totalImpact: number
  sequence: string[]
}

// Color mappings
const criticalityColors = {
  critical: '#dc2626', // red-600
  high: '#ea580c',     // orange-600
  medium: '#ca8a04',   // yellow-600
  low: '#16a34a'       // green-600
}

const dependencyColors = {
  critical: '#b91c1c',  // red-700
  important: '#d97706', // amber-600
  optional: '#6b7280'   // gray-500
}

export function DependencyMap() {
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null)
  const [filteredCriticality, setFilteredCriticality] = useState<string[]>(['critical', 'high', 'medium', 'low'])
  const [filteredDepartments, setFilteredDepartments] = useState<string[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [showCascadingFailures, setShowCascadingFailures] = useState(false)
  const [cascadingFailures, setCascadingFailures] = useState<CascadingFailure[]>([])
  const [graphData, setGraphData] = useState<{ nodes: GraphNode[], links: GraphLink[] }>({
    nodes: [],
    links: []
  })

  const forceGraphRef = useRef<any>(null)

  // Fetch BIA results and dependency mappings
  const { data: biaResults, isLoading: biaLoading } = useQuery({
    queryKey: biaQueryKeys.results(),
    queryFn: () => biaAPI.getBIAResults({})
  })

  const { data: dependencies, isLoading: depLoading } = useQuery({
    queryKey: biaQueryKeys.dependencies(),
    queryFn: () => biaAPI.getDependencyMappings(undefined)
  })

  // Convert BIA data to graph format
  useEffect(() => {
    if (!biaResults || !dependencies) return

    // Get all unique departments
    const departments = Array.from(new Set(biaResults.map(r => r.department)))
    if (filteredDepartments.length === 0) {
      setFilteredDepartments(departments as string[])
    }

    // Create nodes from BIA results
    const nodes: GraphNode[] = biaResults
      .filter(result =>
        filteredCriticality.includes(result.criticalityLevel) &&
        filteredDepartments.includes(result.department) &&
        (searchTerm === '' ||
         result.businessFunction.toLowerCase().includes(searchTerm.toLowerCase()) ||
         result.department.toLowerCase().includes(searchTerm.toLowerCase()))
      )
      .map(result => ({
        id: result.id,
        name: result.businessFunction,
        department: result.department,
        criticalityLevel: result.criticalityLevel,
        rto: result.rto,
        rpo: result.rpo,
        financialImpactPerHour: result.financialImpactPerHour,
        dependencies: result.dependencies,
        color: criticalityColors[result.criticalityLevel],
        size: calculateNodeSize(result)
      }))

    // Create links from dependency mappings
    const nodeIds = new Set(nodes.map(n => n.id))
    const links: GraphLink[] = dependencies
      .filter(dep => {
        // Find source and target nodes by name matching
        const sourceNode = nodes.find(n => n.name === dep.sourceFunction)
        const targetNode = nodes.find(n => n.name === dep.targetFunction)
        return sourceNode && targetNode
      })
      .map(dep => {
        const sourceNode = nodes.find(n => n.name === dep.sourceFunction)!
        const targetNode = nodes.find(n => n.name === dep.targetFunction)!
        return {
          source: sourceNode.id,
          target: targetNode.id,
          dependencyType: dep.dependencyType,
          description: dep.description,
          impactLevel: dep.impactLevel,
          color: dependencyColors[dep.dependencyType],
          width: dep.impactLevel / 2
        }
      })

    setGraphData({ nodes, links })

    // Calculate cascading failures
    if (showCascadingFailures) {
      calculateCascadingFailures(nodes, links)
    }
  }, [biaResults, dependencies, filteredCriticality, filteredDepartments, searchTerm, showCascadingFailures])

  // Calculate node size based on criticality and financial impact
  const calculateNodeSize = (result: BIAResult): number => {
    const baseSize = 8
    const criticalityMultiplier = {
      critical: 3,
      high: 2.5,
      medium: 2,
      low: 1.5
    }
    const impactMultiplier = Math.log10(result.financialImpactPerHour / 1000 + 1)
    return baseSize * criticalityMultiplier[result.criticalityLevel] * impactMultiplier
  }

  // Calculate potential cascading failures
  const calculateCascadingFailures = (nodes: GraphNode[], links: GraphLink[]) => {
    const failures: CascadingFailure[] = []

    nodes.forEach(node => {
      const affected = new Set<string>()
      const sequence: string[] = [node.name]
      let totalImpact = node.financialImpactPerHour

      // Find all functions that depend on this node
      const findDependents = (nodeId: string, visited: Set<string> = new Set()) => {
        if (visited.has(nodeId)) return
        visited.add(nodeId)

        links.forEach(link => {
          if (link.target === nodeId && !visited.has(link.source)) {
            const dependentNode = nodes.find(n => n.id === link.source)
            if (dependentNode && link.dependencyType === 'critical') {
              affected.add(dependentNode.name)
              sequence.push(dependentNode.name)
              totalImpact += dependentNode.financialImpactPerHour * 0.8 // Reduced impact
              findDependents(link.source, visited)
            }
          }
        })
      }

      findDependents(node.id)

      if (affected.size > 0) {
        failures.push({
          triggeredBy: node.name,
          affectedFunctions: Array.from(affected),
          totalImpact,
          sequence
        })
      }
    })

    // Sort by total impact
    failures.sort((a, b) => b.totalImpact - a.totalImpact)
    setCascadingFailures(failures.slice(0, 10)) // Top 10 most impactful
  }

  // Export graph as image
  const exportAsImage = () => {
    if (forceGraphRef.current) {
      const canvas = forceGraphRef.current.graph().canvas()
      const link = document.createElement('a')
      link.download = `dependency_map_${new Date().toISOString().split('T')[0]}.png`
      link.href = canvas.toDataURL()
      link.click()
    }
  }

  // Handle node click
  const handleNodeClick = (node: GraphNode) => {
    setSelectedNode(node)
  }

  // Handle node hover
  const handleNodeHover = (node: GraphNode | null) => {
    if (forceGraphRef.current) {
      forceGraphRef.current.graph().canvas().style.cursor = node ? 'pointer' : 'grab'
    }
  }

  // Reset graph position and zoom
  const resetView = () => {
    if (forceGraphRef.current) {
      forceGraphRef.current.graph().zoomToFit(400)
    }
  }

  // Filter handlers
  const toggleCriticality = (level: string) => {
    setFilteredCriticality(prev =>
      prev.includes(level)
        ? prev.filter(c => c !== level)
        : [...prev, level]
    )
  }

  const toggleDepartment = (department: string) => {
    setFilteredDepartments(prev =>
      prev.includes(department)
        ? prev.filter(d => d !== department)
        : [...prev, department]
    )
  }

  const allDepartments = Array.from(new Set(biaResults?.map(r => r.department) || []))

  if (biaLoading || depLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-96"></div>
          <div className="h-96 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Dependency Mapping</h2>
          <p className="text-gray-600 mt-1">
            Interactive visualization of business function dependencies and potential cascading failures
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowCascadingFailures(!showCascadingFailures)}
            className={cn(
              showCascadingFailures && "bg-red-50 border-red-200 text-red-700"
            )}
          >
            {showCascadingFailures ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            {showCascadingFailures ? 'Hide' : 'Show'} Cascading Failures
          </Button>
          <Button variant="outline" size="sm" onClick={resetView}>
            <RotateCcw className="w-4 h-4" />
            Reset View
          </Button>
          <Button variant="outline" size="sm" onClick={exportAsImage}>
            <Download className="w-4 h-4" />
            Export Image
          </Button>
        </div>
      </div>

      {/* Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
        {/* Search */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Search Functions</label>
          <div className="relative">
            <Search className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by function or department..."
              className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        {/* Criticality Filter */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Criticality Levels</label>
          <div className="flex flex-wrap gap-2">
            {['critical', 'high', 'medium', 'low'].map(level => (
              <button
                key={level}
                onClick={() => toggleCriticality(level)}
                className={cn(
                  "px-3 py-1 rounded-full text-xs font-medium border transition-colors",
                  filteredCriticality.includes(level)
                    ? "border-transparent text-white"
                    : "border-gray-300 text-gray-700 bg-white hover:bg-gray-50"
                )}
                style={{
                  backgroundColor: filteredCriticality.includes(level)
                    ? criticalityColors[level as keyof typeof criticalityColors]
                    : undefined
                }}
              >
                {level.charAt(0).toUpperCase() + level.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Department Filter */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Departments</label>
          <div className="flex flex-wrap gap-2">
            {allDepartments.map((dept: string) => (
              <button
                key={dept}
                onClick={() => toggleDepartment(dept)}
                className={cn(
                  "px-3 py-1 rounded-full text-xs font-medium border transition-colors",
                  filteredDepartments.includes(dept)
                    ? "border-blue-300 bg-blue-100 text-blue-700"
                    : "border-gray-300 text-gray-700 bg-white hover:bg-gray-50"
                )}
              >
                {dept}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Graph and Details */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        {/* Force Graph */}
        <div className="xl:col-span-3">
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <div className="h-96 lg:h-[600px] relative">
              <ForceGraph2D
                ref={forceGraphRef}
                graphData={graphData}
                nodeId="id"
                nodeLabel={(node: any) => `${node.name}\nDepartment: ${node.department}\nCriticality: ${node.criticalityLevel}\nRTO: ${node.rto}h\nFinancial Impact: $${node.financialImpactPerHour.toLocaleString()}/h`}
                nodeColor={(node: any) => node.color}
                nodeVal={(node: any) => node.size}
                linkColor={(link: any) => link.color}
                linkWidth={(link: any) => link.width}
                linkLabel={(link: any) => `${link.description}\nType: ${link.dependencyType}\nImpact Level: ${link.impactLevel}/10`}
                linkDirectionalArrowLength={6}
                linkDirectionalArrowRelPos={1}
                onNodeClick={handleNodeClick}
                onNodeHover={handleNodeHover}
                backgroundColor="#ffffff"
                linkDirectionalParticles={2}
                linkDirectionalParticleSpeed={0.01}
                cooldownTicks={100}
              />
            </div>
          </div>
        </div>

        {/* Side Panel */}
        <div className="space-y-4">
          {/* Legend */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-3">Legend</h3>

            <div className="space-y-3">
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Criticality Levels</h4>
                <div className="space-y-1">
                  {Object.entries(criticalityColors).map(([level, color]) => (
                    <div key={level} className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: color }}
                      />
                      <span className="text-xs text-gray-600 capitalize">{level}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Dependency Types</h4>
                <div className="space-y-1">
                  {Object.entries(dependencyColors).map(([type, color]) => (
                    <div key={type} className="flex items-center gap-2">
                      <div
                        className="w-8 h-0.5"
                        style={{ backgroundColor: color }}
                      />
                      <span className="text-xs text-gray-600 capitalize">{type}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-3 pt-3 border-t border-gray-200">
              <p className="text-xs text-gray-500">
                • Node size reflects criticality and financial impact<br/>
                • Arrow thickness indicates dependency strength<br/>
                • Click nodes for detailed information
              </p>
            </div>
          </div>

          {/* Selected Node Details */}
          {selectedNode && (
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-3">Function Details</h3>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="font-medium text-gray-700">Name:</span>
                  <p className="text-gray-600">{selectedNode.name}</p>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Department:</span>
                  <p className="text-gray-600">{selectedNode.department}</p>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Criticality:</span>
                  <span
                    className="inline-block px-2 py-1 rounded text-xs font-medium text-white ml-2"
                    style={{ backgroundColor: selectedNode.color }}
                  >
                    {selectedNode.criticalityLevel.toUpperCase()}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">RTO:</span>
                  <p className="text-gray-600">{selectedNode.rto} hours</p>
                </div>
                <div>
                  <span className="font-medium text-gray-700">RPO:</span>
                  <p className="text-gray-600">{selectedNode.rpo} hours</p>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Financial Impact:</span>
                  <p className="text-gray-600">${selectedNode.financialImpactPerHour.toLocaleString()}/hour</p>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Dependencies:</span>
                  <ul className="text-gray-600 ml-2 mt-1">
                    {selectedNode.dependencies.map((dep, index) => (
                      <li key={index} className="text-xs">• {dep}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Cascading Failures */}
          {showCascadingFailures && cascadingFailures.length > 0 && (
            <div className="bg-white border border-red-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-3">
                <AlertTriangle className="w-4 h-4 text-red-600" />
                <h3 className="font-semibold text-red-900">Cascading Failure Risks</h3>
              </div>
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {cascadingFailures.slice(0, 5).map((failure, index) => (
                  <div key={index} className="bg-red-50 p-3 rounded border border-red-200">
                    <div className="text-sm">
                      <p className="font-medium text-red-900">
                        Triggered by: {failure.triggeredBy}
                      </p>
                      <p className="text-red-700 text-xs mt-1">
                        Affects {failure.affectedFunctions.length} functions
                      </p>
                      <p className="text-red-600 text-xs">
                        Total Impact: ${failure.totalImpact.toLocaleString()}/hour
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Graph Stats */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-3">Graph Statistics</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-700">Functions:</span>
                <span className="font-medium">{graphData.nodes.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-700">Dependencies:</span>
                <span className="font-medium">{graphData.links.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-700">Critical Functions:</span>
                <span className="font-medium text-red-600">
                  {graphData.nodes.filter(n => n.criticalityLevel === 'critical').length}
                </span>
              </div>
              {showCascadingFailures && (
                <div className="flex justify-between">
                  <span className="text-gray-700">Failure Risks:</span>
                  <span className="font-medium text-orange-600">{cascadingFailures.length}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}