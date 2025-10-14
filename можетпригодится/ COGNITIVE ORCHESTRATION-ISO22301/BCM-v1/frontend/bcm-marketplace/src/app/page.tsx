'use client'

import React from 'react'
import Link from 'next/link'
import { AppLayout } from '@/components/layout/AppLayout'
import { useAuthStore } from '@/store/auth'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Search,
  Shield,
  Users,
  Star,
  TrendingUp,
  CheckCircle,
  ArrowRight
} from 'lucide-react'

export default function HomePage() {
  const { isAuthenticated, user } = useAuthStore()

  if (isAuthenticated && user?.role === 'client') {
    // Redirect clients to their dashboard
    window.location.href = '/client/dashboard'
    return null
  }

  if (isAuthenticated && user?.role === 'specialist') {
    return (
      <AppLayout>
        <div className="space-y-8">
          {/* Hero Section for Specialists */}
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg p-8 text-white">
            <div className="max-w-3xl">
              <h1 className="text-3xl font-bold mb-4">
                Welcome to BCM Marketplace!
              </h1>
              <p className="text-blue-100 text-lg mb-6">
                Leading platform for Business Continuity Management projects
              </p>
              <div className="flex space-x-4">
                <Button size="lg" variant="secondary" asChild>
                  <Link href="/requests">
                    <Search className="mr-2 h-5 w-5" />
                    Find Projects
                  </Link>
                </Button>
                <Button size="lg" variant="outline" className="text-white border-white hover:bg-white hover:text-blue-600" asChild>
                  <Link href="/specialist/profile">
                    Update Profile
                  </Link>
                </Button>
              </div>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Users className="h-5 w-5 text-blue-600" />
                  <span className="text-2xl font-bold">1,247</span>
                </div>
                <p className="text-sm text-gray-600 mt-2">Active Specialists</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Search className="h-5 w-5 text-green-600" />
                  <span className="text-2xl font-bold">89</span>
                </div>
                <p className="text-sm text-gray-600 mt-2">Open Projects</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-purple-600" />
                  <span className="text-2xl font-bold">2,456</span>
                </div>
                <p className="text-sm text-gray-600 mt-2">Completed Projects</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5 text-yellow-600" />
                  <span className="text-2xl font-bold">$15K</span>
                </div>
                <p className="text-sm text-gray-600 mt-2">Average monthly income</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="space-y-16">
        {/* Hero Section */}
        <section className="text-center space-y-8">
          <div className="space-y-4">
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
              Find the best{' '}
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                BCM specialists
              </span>
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Platform for finding and hiring Business Continuity Management experts.
              Connect with the leading community of BCM professionals.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" asChild>
              <Link href="/specialists">
                <Search className="mr-2 h-5 w-5" />
                Find Specialists
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="/register">
                Become a Specialist
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
          </div>

          {/* Trust Indicators */}
          <div className="flex flex-wrap justify-center gap-8 text-sm text-gray-500">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>1,247+ verified specialists</span>
            </div>
            <div className="flex items-center space-x-2">
              <Star className="h-4 w-4 text-yellow-500" />
              <span>4.9/5 average rating</span>
            </div>
            <div className="flex items-center space-x-2">
              <Shield className="h-4 w-4 text-blue-500" />
              <span>Quality guarantee</span>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="grid md:grid-cols-3 gap-8">
          <Card className="text-center">
            <CardHeader>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Search className="h-6 w-6 text-blue-600" />
              </div>
              <CardTitle>Find Experts</CardTitle>
              <CardDescription>
                Over 1,000 verified BCM specialists with experience across various industries
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="text-center">
            <CardHeader>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Shield className="h-6 w-6 text-green-600" />
              </div>
              <CardTitle>Secure Payments</CardTitle>
              <CardDescription>
                Protected payment system with quality guarantee and refund options
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="text-center">
            <CardHeader>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Users className="h-6 w-6 text-purple-600" />
              </div>
              <CardTitle>24/7 Support</CardTitle>
              <CardDescription>
                Our support team helps at every stage of collaboration
              </CardDescription>
            </CardHeader>
          </Card>
        </section>

        {/* Marketplace Sections */}
        <section className="space-y-8">
          <div className="text-center space-y-4">
            <h2 className="text-3xl font-bold">Explore BCM Marketplace</h2>
            <p className="text-gray-600">Everything you need for Business Continuity Management</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer" asChild>
              <Link href="/specialists">
                <CardContent className="p-6 text-center">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <Users className="h-6 w-6 text-blue-600" />
                  </div>
                  <h3 className="font-semibold mb-2">Find Specialists</h3>
                  <p className="text-sm text-gray-600">Hire verified BCM experts</p>
                  <div className="mt-3 text-sm text-blue-600">1,200+ specialists</div>
                </CardContent>
              </Link>
            </Card>

            <Card className="hover:shadow-lg transition-shadow cursor-pointer" asChild>
              <Link href="/solutions">
                <CardContent className="p-6 text-center">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <Shield className="h-6 w-6 text-green-600" />
                  </div>
                  <h3 className="font-semibold mb-2">Solutions</h3>
                  <p className="text-sm text-gray-600">Templates, tools & frameworks</p>
                  <div className="mt-3 text-sm text-green-600">500+ solutions</div>
                </CardContent>
              </Link>
            </Card>

            <Card className="hover:shadow-lg transition-shadow cursor-pointer" asChild>
              <Link href="/knowledge">
                <CardContent className="p-6 text-center">
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <Search className="h-6 w-6 text-purple-600" />
                  </div>
                  <h3 className="font-semibold mb-2">Knowledge Base</h3>
                  <p className="text-sm text-gray-600">Expert insights & guides</p>
                  <div className="mt-3 text-sm text-purple-600">800+ articles</div>
                </CardContent>
              </Link>
            </Card>

            <Card className="hover:shadow-lg transition-shadow cursor-pointer" asChild>
              <Link href="/cases">
                <CardContent className="p-6 text-center">
                  <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <TrendingUp className="h-6 w-6 text-orange-600" />
                  </div>
                  <h3 className="font-semibold mb-2">Case Studies</h3>
                  <p className="text-sm text-gray-600">Real success stories</p>
                  <div className="mt-3 text-sm text-orange-600">300+ cases</div>
                </CardContent>
              </Link>
            </Card>
          </div>
        </section>

        {/* Popular Services */}
        <section className="space-y-8">
          <div className="text-center space-y-4">
            <h2 className="text-3xl font-bold">Popular Services</h2>
            <p className="text-gray-600">Most in-demand services from our specialists</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { name: 'BCM Audit', price: 'from $150/hr', badge: 'Top' },
              { name: 'Risk Analysis', price: 'from $120/hr', badge: null },
              { name: 'Continuity Planning', price: 'from $200/project', badge: 'Popular' },
              { name: 'Staff Training', price: 'from $80/hr', badge: null },
              { name: 'Plan Testing', price: 'from $100/hr', badge: null },
              { name: 'ISO 22301 Consulting', price: 'from $180/hr', badge: 'New' },
              { name: 'Crisis Management', price: 'from $250/hr', badge: null },
              { name: 'BCM Automation', price: 'from $300/project', badge: 'Trending' },
            ].map((service, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardContent className="p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-medium">{service.name}</h3>
                    {service.badge && (
                      <Badge variant={
                        service.badge === 'Top' ? 'destructive' :
                        service.badge === 'Popular' ? 'default' :
                        service.badge === 'New' ? 'secondary' :
                        'outline'
                      }>
                        {service.badge}
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-gray-500">{service.price}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* CTA Section */}
        <section className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 md:p-12 text-white text-center">
          <div className="max-w-3xl mx-auto space-y-6">
            <h2 className="text-3xl md:text-4xl font-bold">
              Ready to start your BCM project?
            </h2>
            <p className="text-lg opacity-90">
              Join thousands of companies who trust our platform
              to find the best BCM specialists
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" variant="secondary" asChild>
                <Link href="/specialists">
                  <Search className="mr-2 h-5 w-5" />
                  Find Specialist Now
                </Link>
              </Button>
              <Button size="lg" variant="outline" className="text-white border-white hover:bg-white hover:text-blue-600" asChild>
                <Link href="/how-it-works">
                  Learn More
                </Link>
              </Button>
            </div>
          </div>
        </section>
      </div>
    </AppLayout>
  )
}
