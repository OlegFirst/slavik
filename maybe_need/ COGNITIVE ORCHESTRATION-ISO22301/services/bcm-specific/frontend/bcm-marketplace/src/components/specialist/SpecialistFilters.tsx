'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { Switch } from '@/components/ui/switch'
import { Slider } from '@/components/ui/slider'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import {
  MapPin,
  DollarSign,
  Star,
  Briefcase,
  Languages,
  Award,
  Clock,
  X
} from 'lucide-react'
import { SearchFilters, Specialization, Industry } from '@/types'

interface SpecialistFiltersProps {
  filters: SearchFilters
  onFiltersChange: (filters: Partial<SearchFilters>) => void
  specializations: Specialization[]
  industries: Industry[]
}

const serviceTypes = [
  { id: 'consulting', name: 'Консультирование', icon: '🤝' },
  { id: 'assessment', name: 'Оценка', icon: '📊' },
  { id: 'planning', name: 'Планирование', icon: '📋' },
  { id: 'training', name: 'Обучение', icon: '🎓' },
  { id: 'audit', name: 'Аудит', icon: '🔍' },
  { id: 'implementation', name: 'Внедрение', icon: '⚙️' },
  { id: 'crisis_support', name: 'Кризисная поддержка', icon: '🚨' },
  { id: 'other', name: 'Другое', icon: '📝' }
]

const countries = [
  'Россия',
  'Казахстан',
  'Беларусь',
  'Украина',
  'Армения',
  'Азербайджан',
  'Грузия',
  'Молдова',
  'Узбекистан',
  'Киргизия',
  'Таджикистан',
  'Туркменистан'
]

const languages = [
  { code: 'ru', name: 'Русский' },
  { code: 'en', name: 'Английский' },
  { code: 'de', name: 'Немецкий' },
  { code: 'fr', name: 'Французский' },
  { code: 'es', name: 'Испанский' },
  { code: 'zh', name: 'Китайский' },
  { code: 'kz', name: 'Казахский' },
  { code: 'by', name: 'Белорусский' },
  { code: 'uk', name: 'Украинский' }
]

export function SpecialistFilters({
  filters,
  onFiltersChange,
  specializations,
  industries
}: SpecialistFiltersProps) {

  const handleSpecializationToggle = (specializationId: string) => {
    const current = filters.specializations || []
    const updated = current.includes(specializationId)
      ? current.filter(id => id !== specializationId)
      : [...current, specializationId]

    onFiltersChange({ specializations: updated })
  }

  const handleIndustryToggle = (industryId: string) => {
    const current = filters.industries || []
    const updated = current.includes(industryId)
      ? current.filter(id => id !== industryId)
      : [...current, industryId]

    onFiltersChange({ industries: updated })
  }

  const handleServiceTypeToggle = (serviceType: string) => {
    const current = filters.serviceTypes || []
    const updated = current.includes(serviceType)
      ? current.filter(id => id !== serviceType)
      : [...current, serviceType]

    onFiltersChange({ serviceTypes: updated })
  }

  const handleLanguageToggle = (languageCode: string) => {
    const current = filters.languages || []
    const updated = current.includes(languageCode)
      ? current.filter(code => code !== languageCode)
      : [...current, languageCode]

    onFiltersChange({ languages: updated })
  }

  const handleRatingChange = (values: number[]) => {
    onFiltersChange({
      rating: values[0] > 0 ? { min: values[0], max: 5 } : undefined
    })
  }

  const handleExperienceChange = (values: number[]) => {
    onFiltersChange({
      experience: values[0] > 0 ? { min: values[0], max: 25 } : undefined
    })
  }

  const handleHourlyRateChange = (values: number[]) => {
    onFiltersChange({
      hourlyRate: values[0] > 1000 || values[1] < 50000
        ? { min: values[0], max: values[1] }
        : undefined
    })
  }

  const clearFilters = () => {
    onFiltersChange({
      serviceTypes: undefined,
      specializations: undefined,
      industries: undefined,
      rating: undefined,
      experience: undefined,
      hourlyRate: undefined,
      location: undefined,
      availability: undefined,
      verifiedOnly: undefined,
      languages: undefined,
    })
  }

  const activeFiltersCount = [
    filters.serviceTypes?.length,
    filters.specializations?.length,
    filters.industries?.length,
    filters.rating ? 1 : 0,
    filters.experience ? 1 : 0,
    filters.hourlyRate ? 1 : 0,
    filters.location?.country ? 1 : 0,
    filters.availability !== 'all' ? 1 : 0,
    filters.verifiedOnly ? 1 : 0,
    filters.languages?.length,
  ].reduce((sum, count) => (sum || 0) + (count || 0), 0)

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg flex items-center gap-2">
              <Star className="h-5 w-5" />
              Фильтры
            </CardTitle>
            {(activeFiltersCount || 0) > 0 && (
              <div className="flex items-center gap-2">
                <Badge variant="secondary">{activeFiltersCount}</Badge>
                <Button variant="ghost" size="sm" onClick={clearFilters}>
                  Сбросить
                </Button>
              </div>
            )}
          </div>
        </CardHeader>
      </Card>

      {/* Quick Filters */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <Clock className="h-4 w-4" />
            Быстрые фильтры
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <Label htmlFor="verified-only" className="text-sm font-normal">
              Только проверенные
            </Label>
            <Switch
              id="verified-only"
              checked={filters.verifiedOnly || false}
              onCheckedChange={(checked) => onFiltersChange({ verifiedOnly: checked })}
            />
          </div>

          <div className="space-y-2">
            <Label className="text-sm">Доступность</Label>
            <Select
              value={filters.availability || 'all'}
              onValueChange={(value) => onFiltersChange({ availability: value as any })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Все</SelectItem>
                <SelectItem value="available">Доступны сейчас</SelectItem>
                <SelectItem value="busy">Заняты</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Location */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <MapPin className="h-4 w-4" />
            Местоположение
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label className="text-sm">Страна</Label>
            <Select
              value={filters.location?.country || ''}
              onValueChange={(value) => onFiltersChange({
                location: { ...filters.location, country: value || undefined }
              })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Выберите страну" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">Все страны</SelectItem>
                {countries.map(country => (
                  <SelectItem key={country} value={country}>{country}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label className="text-sm">Город</Label>
            <Input
              placeholder="Введите город"
              value={filters.location?.city || ''}
              onChange={(e) => onFiltersChange({
                location: { ...filters.location, city: e.target.value || undefined }
              })}
            />
          </div>

          <div className="flex items-center justify-between">
            <Label htmlFor="remote-work" className="text-sm font-normal">
              Удаленная работа
            </Label>
            <Switch
              id="remote-work"
              checked={filters.location?.remote || false}
              onCheckedChange={(checked) => onFiltersChange({
                location: { ...filters.location, remote: checked }
              })}
            />
          </div>
        </CardContent>
      </Card>

      {/* Rating */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <Star className="h-4 w-4" />
            Минимальный рейтинг
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Slider
              value={[filters.rating?.min || 0]}
              onValueChange={handleRatingChange}
              max={5}
              min={0}
              step={0.1}
              className="w-full"
            />
            <div className="flex justify-between text-sm text-gray-500">
              <span>Любой</span>
              <span>{filters.rating?.min || 0}+ ⭐</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Experience */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <Briefcase className="h-4 w-4" />
            Опыт работы
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Slider
              value={[filters.experience?.min || 0]}
              onValueChange={handleExperienceChange}
              max={25}
              min={0}
              step={1}
              className="w-full"
            />
            <div className="flex justify-between text-sm text-gray-500">
              <span>Любой</span>
              <span>{filters.experience?.min || 0}+ лет</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Hourly Rate */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <DollarSign className="h-4 w-4" />
            Стоимость в час
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Slider
              value={[
                filters.hourlyRate?.min || 50,
                filters.hourlyRate?.max || 500
              ]}
              onValueChange={handleHourlyRateChange}
              max={500}
              min={50}
              step={10}
              className="w-full"
            />
            <div className="flex justify-between text-sm text-gray-500">
              <span>${filters.hourlyRate?.min?.toLocaleString() || '50'}</span>
              <span>${filters.hourlyRate?.max?.toLocaleString() || '500'}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Service Types */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm">Типы услуг</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {serviceTypes.map((type) => (
              <div key={type.id} className="flex items-center space-x-3">
                <Checkbox
                  id={`service-${type.id}`}
                  checked={filters.serviceTypes?.includes(type.id) || false}
                  onCheckedChange={() => handleServiceTypeToggle(type.id)}
                />
                <Label htmlFor={`service-${type.id}`} className="text-sm font-normal flex items-center gap-2">
                  <span>{type.icon}</span>
                  {type.name}
                </Label>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Specializations */}
      {specializations.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Award className="h-4 w-4" />
              Специализации
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-60 overflow-y-auto">
              {specializations.map((spec) => (
                <div key={spec.id} className="flex items-center space-x-3">
                  <Checkbox
                    id={`spec-${spec.id}`}
                    checked={filters.specializations?.includes(spec.id) || false}
                    onCheckedChange={() => handleSpecializationToggle(spec.id)}
                  />
                  <Label htmlFor={`spec-${spec.id}`} className="text-sm font-normal">
                    {spec.name}
                  </Label>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Industries */}
      {industries.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm">Отрасли</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-40 overflow-y-auto">
              {industries.map((industry) => (
                <div key={industry.id} className="flex items-center space-x-3">
                  <Checkbox
                    id={`industry-${industry.id}`}
                    checked={filters.industries?.includes(industry.id) || false}
                    onCheckedChange={() => handleIndustryToggle(industry.id)}
                  />
                  <Label htmlFor={`industry-${industry.id}`} className="text-sm font-normal">
                    {industry.name}
                  </Label>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Languages */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <Languages className="h-4 w-4" />
            Языки
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {languages.map((lang) => (
              <div key={lang.code} className="flex items-center space-x-3">
                <Checkbox
                  id={`lang-${lang.code}`}
                  checked={filters.languages?.includes(lang.code) || false}
                  onCheckedChange={() => handleLanguageToggle(lang.code)}
                />
                <Label htmlFor={`lang-${lang.code}`} className="text-sm font-normal">
                  {lang.name}
                </Label>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}