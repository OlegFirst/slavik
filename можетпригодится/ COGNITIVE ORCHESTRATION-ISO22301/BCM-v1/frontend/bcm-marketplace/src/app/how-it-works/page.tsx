'use client'

import React from 'react'
import Link from 'next/link'
import { AppLayout } from '@/components/layout/AppLayout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Search,
  FileText,
  UserCheck,
  CreditCard,
  CheckCircle,
  Users,
  Shield,
  Clock,
  Star,
  MessageSquare,
  Briefcase,
  ArrowRight,
  Play
} from 'lucide-react'

export default function HowItWorksPage() {
  return (
    <AppLayout>
      <div className="space-y-16">
        {/* Hero Section */}
        <section className="text-center space-y-8">
          <div className="space-y-4">
            <Badge variant="secondary" className="px-4 py-2">
              How BCM Marketplace Works
            </Badge>
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
              Simple, secure, and{' '}
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                effective
              </span>
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Connect with BCM experts in just a few clicks. Our platform makes it easy to find,
              hire, and work with the best Business Continuity Management professionals.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" asChild>
              <Link href="/register">
                <Users className="mr-2 h-5 w-5" />
                Get Started
              </Link>
            </Button>
            <Button size="lg" variant="outline">
              <Play className="mr-2 h-5 w-5" />
              Watch Demo
            </Button>
          </div>
        </section>

        {/* For Clients - How it Works */}
        <section className="space-y-12">
          <div className="text-center">
            <h2 className="text-3xl font-bold mb-4">For Clients</h2>
            <p className="text-gray-600 text-lg">Find and hire BCM specialists in 4 simple steps</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <Card className="text-center relative">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                  1
                </div>
              </div>
              <CardHeader className="pt-8">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <FileText className="h-6 w-6 text-blue-600" />
                </div>
                <CardTitle className="text-lg">Post Your Project</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 text-sm">
                  Describe your BCM needs, set your budget, and specify your timeline.
                  Our smart matching system will find the right specialists for you.
                </p>
              </CardContent>
            </Card>

            <Card className="text-center relative">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                  2
                </div>
              </div>
              <CardHeader className="pt-8">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Search className="h-6 w-6 text-green-600" />
                </div>
                <CardTitle className="text-lg">Review Proposals</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 text-sm">
                  Receive proposals from qualified specialists within 24 hours.
                  Review portfolios, ratings, and previous work samples.
                </p>
              </CardContent>
            </Card>

            <Card className="text-center relative">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                  3
                </div>
              </div>
              <CardHeader className="pt-8">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <UserCheck className="h-6 w-6 text-purple-600" />
                </div>
                <CardTitle className="text-lg">Choose & Hire</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 text-sm">
                  Interview candidates, check references, and hire the best fit.
                  All specialists are pre-verified and background checked.
                </p>
              </CardContent>
            </Card>

            <Card className="text-center relative">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                  4
                </div>
              </div>
              <CardHeader className="pt-8">
                <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <CreditCard className="h-6 w-6 text-yellow-600" />
                </div>
                <CardTitle className="text-lg">Pay Securely</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 text-sm">
                  Work gets done, milestones are completed, and payments are released
                  automatically. 100% secure with money-back guarantee.
                </p>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* For Specialists - How it Works */}
        <section className="bg-gray-50 rounded-2xl p-8 md:p-12 space-y-12">
          <div className="text-center">
            <h2 className="text-3xl font-bold mb-4">For Specialists</h2>
            <p className="text-gray-600 text-lg">Start earning with BCM projects in 3 simple steps</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <Card className="text-center relative">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <div className="w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center font-bold">
                  1
                </div>
              </div>
              <CardHeader className="pt-8">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Users className="h-6 w-6 text-green-600" />
                </div>
                <CardTitle className="text-lg">Create Your Profile</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 text-sm">
                  Showcase your BCM expertise, certifications, and portfolio.
                  Get verified to build trust with potential clients.
                </p>
              </CardContent>
            </Card>

            <Card className="text-center relative">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <div className="w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center font-bold">
                  2
                </div>
              </div>
              <CardHeader className="pt-8">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Search className="h-6 w-6 text-blue-600" />
                </div>
                <CardTitle className="text-lg">Find Projects</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 text-sm">
                  Browse relevant projects, submit competitive proposals,
                  and win work that matches your skills and interests.
                </p>
              </CardContent>
            </Card>

            <Card className="text-center relative">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <div className="w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center font-bold">
                  3
                </div>
              </div>
              <CardHeader className="pt-8">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Briefcase className="h-6 w-6 text-purple-600" />
                </div>
                <CardTitle className="text-lg">Deliver & Get Paid</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 text-sm">
                  Complete projects, deliver quality work, and get paid on time.
                  Build your reputation with client reviews and ratings.
                </p>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Key Features */}
        <section className="space-y-12">
          <div className="text-center">
            <h2 className="text-3xl font-bold mb-4">Why Choose BCM Marketplace?</h2>
            <p className="text-gray-600 text-lg">Everything you need for successful BCM collaborations</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card>
              <CardHeader>
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                  <Shield className="h-6 w-6 text-blue-600" />
                </div>
                <CardTitle>Secure Payments</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Escrow protection, milestone payments, and dispute resolution.
                  Your money is safe until work is completed satisfactorily.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                  <UserCheck className="h-6 w-6 text-green-600" />
                </div>
                <CardTitle>Verified Experts</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  All specialists are background-checked, skill-tested, and certified.
                  Work with professionals you can trust.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                  <MessageSquare className="h-6 w-6 text-purple-600" />
                </div>
                <CardTitle>24/7 Support</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Get help when you need it. Our support team is available around
                  the clock to assist with any questions or issues.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mb-4">
                  <Clock className="h-6 w-6 text-yellow-600" />
                </div>
                <CardTitle>Fast Matching</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  AI-powered matching connects you with the right specialists quickly.
                  Get proposals within 24 hours of posting your project.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mb-4">
                  <Star className="h-6 w-6 text-red-600" />
                </div>
                <CardTitle>Quality Assurance</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Review system, quality checks, and continuous monitoring ensure
                  you get the best possible outcomes for your BCM projects.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-4">
                  <Briefcase className="h-6 w-6 text-indigo-600" />
                </div>
                <CardTitle>Project Management</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Built-in tools for communication, file sharing, milestone tracking,
                  and time management. Everything in one place.
                </p>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Stats */}
        <section className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 md:p-12 text-white">
          <div className="text-center space-y-8">
            <h2 className="text-3xl font-bold">Trusted by thousands</h2>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              <div className="text-center">
                <div className="text-4xl font-bold mb-2">1,247+</div>
                <div className="text-blue-200">Verified Specialists</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold mb-2">2,456+</div>
                <div className="text-blue-200">Projects Completed</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold mb-2">4.9/5</div>
                <div className="text-blue-200">Average Rating</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-bold mb-2">$2.5M+</div>
                <div className="text-blue-200">Total Earned</div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="text-center space-y-8">
          <div className="space-y-4">
            <h2 className="text-3xl font-bold">Ready to get started?</h2>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto">
              Join thousands of companies and specialists who trust BCM Marketplace
              for their Business Continuity Management needs.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" asChild>
              <Link href="/register">
                <Users className="mr-2 h-5 w-5" />
                Join as Client
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="/register">
                Become a Specialist
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
          </div>
        </section>
      </div>
    </AppLayout>
  )
}