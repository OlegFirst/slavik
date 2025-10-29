'use client'

import React, { useState } from 'react'
import { useSpecialists, useSpecializations, useIndustries } from '@/hooks/api'
import { AppLayout } from '@/components/layout/AppLayout'
import { SpecialistCard } from '@/components/specialist/SpecialistCard'
import { SpecialistFilters } from '@/components/specialist/SpecialistFilters'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Search,
  Filter,
  SortAsc,
  Users,
  MapPin,
  Star,
  Clock
} from 'lucide-react'
import { SearchFilters } from '@/types'

export default function SpecialistsPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [filters, setFilters] = useState<SearchFilters>({})
  const [showFilters, setShowFilters] = useState(false)

  const { data: specialistsData, isLoading } = useSpecialists(filters)
  const { data: specializations } = useSpecializations()
  const { data: industries } = useIndustries()

  const specialists = specialistsData?.data?.items || []
  const totalCount = specialistsData?.data?.total || 0

  const handleSearch = () => {
    setFilters(prev => ({ ...prev, query: searchQuery }))
  }

  const handleFiltersChange = (newFilters: Partial<SearchFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }))
  }

  const handleSortChange = (sortBy: string) => {
    setFilters(prev => ({ ...prev, sortBy: sortBy as any }))
  }

  const clearFilters = () => {
    setFilters({})
    setSearchQuery('')
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="space-y-2">
          <h1 className="text-3xl font-bold">BCM Specialists</h1>
          <p className="text-gray-600">
            Find and hire the best Business Continuity Management experts
          </p>
        </div>

        {/* Search and Sort Bar */}
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="Search by skills, title, or description..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>
            <Button onClick={handleSearch}>Search</Button>
          </div>

          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2"
            >
              <Filter className="h-4 w-4" />
              Filters
            </Button>

            <Select onValueChange={handleSortChange}>
              <SelectTrigger className="w-48">
                <SortAsc className="h-4 w-4 mr-2" />
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="relevance">By relevance</SelectItem>
                <SelectItem value="rating">By rating</SelectItem>
                <SelectItem value="price_low">Price: low to high</SelectItem>
                <SelectItem value="price_high">Price: high to low</SelectItem>
                <SelectItem value="experience">By experience</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Active Filters */}
        {(filters.query || filters.specializations?.length || filters.location?.country) && (
          <div className="flex flex-wrap gap-2 items-center">
            <span className="text-sm text-gray-500">Active filters:</span>

            {filters.query && (
              <Badge variant="secondary" className="flex items-center gap-1">
                Search: "{filters.query}"
                <button
                  onClick={() => handleFiltersChange({ query: undefined })}
                  className="ml-1 hover:bg-gray-300 rounded-full p-0.5"
                >
                  ×
                </button>
              </Badge>
            )}

            {filters.specializations?.map((spec) => (
              <Badge key={spec} variant="secondary" className="flex items-center gap-1">
                {spec}
                <button
                  onClick={() => handleFiltersChange({
                    specializations: filters.specializations?.filter(s => s !== spec)
                  })}
                  className="ml-1 hover:bg-gray-300 rounded-full p-0.5"
                >
                  ×
                </button>
              </Badge>
            ))}

            {filters.location?.country && (
              <Badge variant="secondary" className="flex items-center gap-1">
                <MapPin className="h-3 w-3" />
                {filters.location.country}
                <button
                  onClick={() => handleFiltersChange({ location: undefined })}
                  className="ml-1 hover:bg-gray-300 rounded-full p-0.5"
                >
                  ×
                </button>
              </Badge>
            )}

            <Button
              variant="ghost"
              size="sm"
              onClick={clearFilters}
              className="text-xs"
            >
              Clear all
            </Button>
          </div>
        )}

        <div className="flex gap-6">
          {/* Filters Sidebar */}
          {showFilters && (
            <div className="w-80 flex-shrink-0">
              <SpecialistFilters
                filters={filters}
                onFiltersChange={handleFiltersChange}
                specializations={specializations?.data || []}
                industries={industries?.data || []}
              />
            </div>
          )}

          {/* Results */}
          <div className="flex-1 space-y-6">
            {/* Results Header */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Users className="h-4 w-4" />
                <span>
                  {isLoading ? 'Searching...' : `${totalCount} specialists found`}
                </span>
              </div>

              {/* Quick Filters */}
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant={filters.verifiedOnly ? 'default' : 'outline'}
                  onClick={() => handleFiltersChange({ verifiedOnly: !filters.verifiedOnly })}
                >
                  <Star className="h-3 w-3 mr-1" />
                  Verified
                </Button>
                <Button
                  size="sm"
                  variant={filters.availability === 'available' ? 'default' : 'outline'}
                  onClick={() => handleFiltersChange({
                    availability: filters.availability === 'available' ? 'all' : 'available'
                  })}
                >
                  <Clock className="h-3 w-3 mr-1" />
                  Available now
                </Button>
              </div>
            </div>

            {/* Specialists Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {isLoading
                ? Array.from({ length: 6 }).map((_, i) => (
                    <div key={i} className="border rounded-lg p-6 space-y-4">
                      <div className="flex items-start space-x-4">
                        <Skeleton className="w-16 h-16 rounded-full" />
                        <div className="flex-1 space-y-2">
                          <Skeleton className="h-6 w-3/4" />
                          <Skeleton className="h-4 w-1/2" />
                          <Skeleton className="h-4 w-2/3" />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <Skeleton className="h-4 w-full" />
                        <Skeleton className="h-4 w-full" />
                        <Skeleton className="h-4 w-3/4" />
                      </div>
                      <div className="flex justify-between items-center">
                        <Skeleton className="h-4 w-24" />
                        <Skeleton className="h-9 w-24" />
                      </div>
                    </div>
                  ))
                : specialists.map((specialist: any) => (
                    <SpecialistCard key={specialist.id} specialist={specialist} />
                  ))
              }
            </div>

            {/* No Results */}
            {!isLoading && specialists.length === 0 && (
              <div className="text-center py-12">
                <Users className="h-12 w-12 mx-auto text-gray-300 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No specialists found
                </h3>
                <p className="text-gray-500 mb-4">
                  Try adjusting your search criteria or filters
                </p>
                <Button onClick={clearFilters} variant="outline">
                  Clear filters
                </Button>
              </div>
            )}

            {/* Load More / Pagination */}
            {!isLoading && specialists.length > 0 && specialists.length < totalCount && (
              <div className="text-center">
                <Button variant="outline" size="lg">
                  Show more specialists
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  )
}