'use client'

import React from 'react'
import Link from 'next/link'
import { Specialist } from '@/types'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  Star,
  MapPin,
  Briefcase,
  DollarSign,
  CheckCircle,
  Clock,
  Users,
  Award
} from 'lucide-react'

interface SpecialistCardProps {
  specialist: Specialist
}

export function SpecialistCard({ specialist }: SpecialistCardProps) {
  const getAvailabilityColor = (status: string) => {
    switch (status) {
      case 'available': return 'bg-green-500'
      case 'busy': return 'bg-yellow-500'
      case 'unavailable': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  const getAvailabilityText = (status: string) => {
    switch (status) {
      case 'available': return 'Доступен'
      case 'busy': return 'Занят'
      case 'unavailable': return 'Недоступен'
      default: return 'Неизвестно'
    }
  }

  return (
    <Card className="hover:shadow-lg transition-shadow duration-200">
      <CardContent className="p-6">
        {/* Header */}
        <div className="flex items-start space-x-4 mb-4">
          <div className="relative">
            <Avatar className="w-16 h-16">
              <AvatarImage src={specialist.avatar} alt={specialist.name} />
              <AvatarFallback>
                {specialist.name.split(' ').map(n => n[0]).join('').toUpperCase()}
              </AvatarFallback>
            </Avatar>
            {/* Availability indicator */}
            <div
              className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-white ${getAvailabilityColor(specialist.availabilityStatus)}`}
              title={getAvailabilityText(specialist.availabilityStatus)}
            />
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <h3 className="text-lg font-semibold text-gray-900 truncate">
                  {specialist.name}
                  {specialist.isVerified && (
                    <CheckCircle className="inline-block w-4 h-4 ml-2 text-blue-500" />
                  )}
                </h3>
                <p className="text-sm text-gray-600 truncate">{specialist.title}</p>
              </div>

              <div className="flex items-center space-x-1 ml-2">
                <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                <span className="text-sm font-medium">{specialist.rating}</span>
                <span className="text-sm text-gray-500">({specialist.reviewCount})</span>
              </div>
            </div>

            {/* Quick stats */}
            <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
              <div className="flex items-center space-x-1">
                <Briefcase className="w-3 h-3" />
                <span>{specialist.yearsExperience} лет опыта</span>
              </div>
              <div className="flex items-center space-x-1">
                <Users className="w-3 h-3" />
                <span>{specialist.completedProjects} проектов</span>
              </div>
              {specialist.location && (
                <div className="flex items-center space-x-1">
                  <MapPin className="w-3 h-3" />
                  <span>{specialist.location.city}, {specialist.location.country}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Bio */}
        <div className="mb-4">
          <p className="text-sm text-gray-700 line-clamp-2">
            {specialist.bio}
          </p>
        </div>

        {/* Specializations */}
        <div className="mb-4">
          <div className="flex flex-wrap gap-1">
            {specialist.specializations?.slice(0, 3).map((spec) => (
              <Badge key={spec.id} variant="secondary" className="text-xs">
                {spec.name}
              </Badge>
            ))}
            {specialist.specializations && specialist.specializations.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{specialist.specializations.length - 3} еще
              </Badge>
            )}
          </div>
        </div>

        {/* Services Preview */}
        {specialist.services && specialist.services.length > 0 && (
          <div className="mb-4">
            <div className="text-xs text-gray-500 mb-2">Основные услуги:</div>
            <div className="space-y-1">
              {specialist.services.slice(0, 2).map((service) => (
                <div key={service.id} className="flex justify-between items-center text-sm">
                  <span className="text-gray-700 truncate">{service.name}</span>
                  <span className="text-gray-900 font-medium ml-2">
                    от ₽{service.basePrice.toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Pricing and Availability */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <DollarSign className="w-4 h-4 text-gray-400" />
            <span className="text-lg font-bold text-gray-900">
              ${specialist.hourlyRate.toLocaleString()}
            </span>
            <span className="text-sm text-gray-500">/hr</span>
          </div>

          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${getAvailabilityColor(specialist.availabilityStatus)}`} />
            <span className="text-sm text-gray-600">
              {getAvailabilityText(specialist.availabilityStatus)}
            </span>
          </div>
        </div>

        {/* Work preferences */}
        <div className="flex items-center space-x-4 mb-4 text-xs text-gray-500">
          {specialist.remoteAvailable && (
            <div className="flex items-center space-x-1">
              <Clock className="w-3 h-3" />
              <span>Удаленно</span>
            </div>
          )}
          {specialist.onsiteAvailable && (
            <div className="flex items-center space-x-1">
              <MapPin className="w-3 h-3" />
              <span>На площадке</span>
            </div>
          )}
          {specialist.certifications && specialist.certifications.length > 0 && (
            <div className="flex items-center space-x-1">
              <Award className="w-3 h-3" />
              <span>{specialist.certifications.length} сертификата</span>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex space-x-2">
          <Button asChild className="flex-1">
            <Link href={`/specialists/${specialist.id}`}>
              Подробнее
            </Link>
          </Button>
          <Button variant="outline" className="flex-1">
            Написать
          </Button>
        </div>

        {/* Quick hire option for available specialists */}
        {specialist.availabilityStatus === 'available' && (
          <div className="mt-3 p-3 bg-green-50 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full" />
                <span className="text-sm font-medium text-green-800">
                  Готов приступить сегодня
                </span>
              </div>
              <Button size="sm" className="bg-green-600 hover:bg-green-700">
                Пригласить
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}