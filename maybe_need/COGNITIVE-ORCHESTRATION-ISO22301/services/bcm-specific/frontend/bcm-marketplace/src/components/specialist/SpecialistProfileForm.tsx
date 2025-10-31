'use client'

import React from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { useUpdateSpecialist, useSpecializations, useIndustries, useLanguages } from '@/hooks/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Checkbox } from '@/components/ui/checkbox'
import { Switch } from '@/components/ui/switch'
import { Separator } from '@/components/ui/separator'
import {
  User,
  MapPin,
  DollarSign,
  Award,
  Briefcase,
  Languages,
  Plus,
  X
} from 'lucide-react'
import { Specialist } from '@/types'

const specialistSchema = z.object({
  name: z.string().min(2, 'Имя должно содержать минимум 2 символа'),
  title: z.string().min(5, 'Должность должна содержать минимум 5 символов'),
  bio: z.string().min(50, 'Биография должна содержать минимум 50 символов'),
  yearsExperience: z.number().min(1, 'Опыт работы должен быть больше 0'),
  hourlyRate: z.number().min(500, 'Ставка должна быть больше 500 рублей'),
  currency: z.string().default('RUB'),
  location: z.object({
    country: z.string().min(1, 'Страна обязательна'),
    city: z.string().min(1, 'Город обязателен'),
    timezone: z.string().min(1, 'Часовой пояс обязателен'),
  }),
  remoteAvailable: z.boolean().default(true),
  onsiteAvailable: z.boolean().default(false),
  availabilityStatus: z.enum(['available', 'busy', 'unavailable']),
})

interface SpecialistProfileFormProps {
  specialist: Specialist
  onSuccess?: () => void
}

export function SpecialistProfileForm({ specialist, onSuccess }: SpecialistProfileFormProps) {
  const { mutate: updateSpecialist, isPending } = useUpdateSpecialist()
  const { data: specializations } = useSpecializations()
  const { data: industries } = useIndustries()
  const { data: languages } = useLanguages()

  const form = useForm<any>({
    // resolver: zodResolver(specialistSchema),
    defaultValues: {
      name: specialist.name,
      title: specialist.title,
      bio: specialist.bio,
      yearsExperience: specialist.yearsExperience,
      hourlyRate: specialist.hourlyRate,
      currency: specialist.currency,
      location: specialist.location,
      remoteAvailable: specialist.remoteAvailable,
      onsiteAvailable: specialist.onsiteAvailable,
      availabilityStatus: specialist.availabilityStatus,
    },
  })

  const onSubmit = (values: any) => {
    updateSpecialist({
      id: specialist.id,
      data: values
    }, {
      onSuccess: () => {
        onSuccess?.()
      }
    })
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        {/* Basic Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <User className="h-5 w-5" />
              <span>Основная информация</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Полное имя</FormLabel>
                    <FormControl>
                      <Input placeholder="Иван Иванов" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="title"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Должность/Специализация</FormLabel>
                    <FormControl>
                      <Input placeholder="Ведущий консультант по BCM" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="bio"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Биография</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Расскажите о своем опыте, достижениях и подходе к работе..."
                      className="min-h-[120px]"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    Минимум 50 символов. Хорошая биография помогает клиентам понять ваш опыт.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="yearsExperience"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Опыт работы (лет)</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        min="1"
                        {...field}
                        onChange={(e) => field.onChange(parseInt(e.target.value))}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="availabilityStatus"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Статус доступности</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Выберите статус" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="available">Доступен</SelectItem>
                        <SelectItem value="busy">Занят</SelectItem>
                        <SelectItem value="unavailable">Недоступен</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
          </CardContent>
        </Card>

        {/* Location & Work Preferences */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <MapPin className="h-5 w-5" />
              <span>Локация и предпочтения по работе</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <FormField
                control={form.control}
                name="location.country"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Страна</FormLabel>
                    <FormControl>
                      <Input placeholder="Россия" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="location.city"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Город</FormLabel>
                    <FormControl>
                      <Input placeholder="Москва" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="location.timezone"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Часовой пояс</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Выберите часовой пояс" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="Europe/Moscow">GMT+3 (Москва)</SelectItem>
                        <SelectItem value="Europe/Samara">GMT+4 (Самара)</SelectItem>
                        <SelectItem value="Asia/Yekaterinburg">GMT+5 (Екатеринбург)</SelectItem>
                        <SelectItem value="Asia/Novosibirsk">GMT+7 (Новосибирск)</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="flex items-center space-x-8">
              <FormField
                control={form.control}
                name="remoteAvailable"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center space-x-3 space-y-0">
                    <FormControl>
                      <Switch
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                    <div className="space-y-1 leading-none">
                      <FormLabel>Удаленная работа</FormLabel>
                    </div>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="onsiteAvailable"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center space-x-3 space-y-0">
                    <FormControl>
                      <Switch
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                    <div className="space-y-1 leading-none">
                      <FormLabel>Работа на площадке клиента</FormLabel>
                    </div>
                  </FormItem>
                )}
              />
            </div>
          </CardContent>
        </Card>

        {/* Pricing */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <DollarSign className="h-5 w-5" />
              <span>Стоимость услуг</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="hourlyRate"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Почасовая ставка</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        min="500"
                        {...field}
                        onChange={(e) => field.onChange(parseInt(e.target.value))}
                      />
                    </FormControl>
                    <FormDescription>
                      Укажите вашу почасовую ставку в рублях
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="currency"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Валюта</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Выберите валюту" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="RUB">Рубль (₽)</SelectItem>
                        <SelectItem value="USD">Доллар ($)</SelectItem>
                        <SelectItem value="EUR">Евро (€)</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end space-x-4">
          <Button type="button" variant="outline">
            Отмена
          </Button>
          <Button type="submit" disabled={isPending}>
            {isPending ? 'Сохранение...' : 'Сохранить изменения'}
          </Button>
        </div>
      </form>
    </Form>
  )
}