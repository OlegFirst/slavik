'use client'

import React from 'react'
import Link from 'next/link'
import { AppLayout } from '@/components/layout/AppLayout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Check,
  X,
  Users,
  Star,
  Shield,
  ArrowRight,
  Building,
  Crown,
  Zap
} from 'lucide-react'

export default function PricingPage() {
  const plans = [
    {
      name: 'Starter',
      price: 'Free',
      period: '',
      description: 'Perfect for new specialists getting started',
      icon: Users,
      color: 'blue',
      features: [
        'Create basic profile',
        'Browse up to 5 projects/month',
        'Submit up to 3 proposals/month',
        'Basic messaging',
        'Community access',
        'Email support'
      ],
      limitations: [
        'Featured listings',
        'Advanced analytics',
        'Priority support',
        'Custom portfolio themes'
      ],
      cta: 'Get Started',
      popular: false
    },
    {
      name: 'Professional',
      price: '$29',
      period: '/month',
      description: 'For active specialists who want more opportunities',
      icon: Star,
      color: 'green',
      features: [
        'Everything in Starter',
        'Unlimited project browsing',
        'Unlimited proposals',
        'Featured profile listings',
        'Advanced portfolio themes',
        'Project analytics',
        'Priority messaging',
        'Phone support'
      ],
      limitations: [
        'White-label solutions',
        'API access'
      ],
      cta: 'Start Professional',
      popular: true
    },
    {
      name: 'Enterprise',
      price: '$99',
      period: '/month',
      description: 'For established consultancies and agencies',
      icon: Crown,
      color: 'purple',
      features: [
        'Everything in Professional',
        'Team management (up to 10 specialists)',
        'White-label client portal',
        'API access',
        'Custom integrations',
        'Dedicated account manager',
        'Advanced reporting',
        '24/7 priority support'
      ],
      limitations: [],
      cta: 'Contact Sales',
      popular: false
    }
  ]

  const clientPlans = [
    {
      name: 'Pay Per Project',
      price: '5%',
      period: 'platform fee',
      description: 'Pay only when you hire',
      icon: Zap,
      color: 'blue',
      features: [
        'Post unlimited projects',
        'Access to all specialists',
        'Project management tools',
        'Secure payments',
        'Dispute resolution',
        'Basic support'
      ],
      cta: 'Start Hiring'
    },
    {
      name: 'Business',
      price: '$199',
      period: '/month',
      description: 'For companies with regular BCM needs',
      icon: Building,
      color: 'green',
      features: [
        'Everything in Pay Per Project',
        'Reduced 3% platform fee',
        'Priority specialist matching',
        'Dedicated project manager',
        'Advanced reporting',
        'Volume discounts',
        'Priority support'
      ],
      cta: 'Contact Sales'
    }
  ]

  return (
    <AppLayout>
      <div className="space-y-16">
        {/* Hero Section */}
        <section className="text-center space-y-8">
          <div className="space-y-4">
            <Badge variant="secondary" className="px-4 py-2">
              Simple, Transparent Pricing
            </Badge>
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
              Choose the{' '}
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                right plan
              </span>{' '}
              for you
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Whether you're a BCM specialist looking for opportunities or a client seeking expertise,
              we have flexible plans to match your needs.
            </p>
          </div>
        </section>

        {/* Specialist Pricing */}
        <section className="space-y-12">
          <div className="text-center">
            <h2 className="text-3xl font-bold mb-4">For BCM Specialists</h2>
            <p className="text-gray-600 text-lg">Find more projects and grow your business</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {plans.map((plan, index) => {
              const IconComponent = plan.icon
              return (
                <Card
                  key={plan.name}
                  className={`relative ${plan.popular ? 'border-green-500 border-2' : ''}`}
                >
                  {plan.popular && (
                    <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                      <Badge className="bg-green-500 text-white px-4 py-1">
                        Most Popular
                      </Badge>
                    </div>
                  )}

                  <CardHeader className="text-center pb-8">
                    <div className={`w-12 h-12 mx-auto mb-4 rounded-lg flex items-center justify-center ${
                      plan.color === 'blue' ? 'bg-blue-100' :
                      plan.color === 'green' ? 'bg-green-100' :
                      plan.color === 'purple' ? 'bg-purple-100' : 'bg-gray-100'
                    }`}>
                      <IconComponent className={`h-6 w-6 ${
                        plan.color === 'blue' ? 'text-blue-600' :
                        plan.color === 'green' ? 'text-green-600' :
                        plan.color === 'purple' ? 'text-purple-600' : 'text-gray-600'
                      }`} />
                    </div>
                    <CardTitle className="text-2xl">{plan.name}</CardTitle>
                    <div className="flex items-baseline justify-center gap-1">
                      <span className="text-4xl font-bold">{plan.price}</span>
                      <span className="text-gray-500">{plan.period}</span>
                    </div>
                    <p className="text-gray-600">{plan.description}</p>
                  </CardHeader>

                  <CardContent className="pt-0">
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium mb-3">What's included:</h4>
                        <ul className="space-y-2">
                          {plan.features.map((feature, idx) => (
                            <li key={idx} className="flex items-start gap-2">
                              <Check className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                              <span className="text-sm">{feature}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      {plan.limitations.length > 0 && (
                        <div>
                          <h4 className="font-medium mb-3 text-gray-600">Not included:</h4>
                          <ul className="space-y-2">
                            {plan.limitations.map((limitation, idx) => (
                              <li key={idx} className="flex items-start gap-2">
                                <X className="h-4 w-4 text-gray-400 mt-0.5 flex-shrink-0" />
                                <span className="text-sm text-gray-500">{limitation}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>

                    <Button
                      className={`w-full mt-6 ${plan.popular ? '' : 'variant-outline'}`}
                      variant={plan.popular ? 'default' : 'outline'}
                      asChild
                    >
                      <Link href="/register">
                        {plan.cta}
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </Link>
                    </Button>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </section>

        {/* Client Pricing */}
        <section className="bg-gray-50 rounded-2xl p-8 md:p-12 space-y-12">
          <div className="text-center">
            <h2 className="text-3xl font-bold mb-4">For Clients</h2>
            <p className="text-gray-600 text-lg">Hire BCM specialists with confidence</p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {clientPlans.map((plan, index) => {
              const IconComponent = plan.icon
              return (
                <Card key={plan.name} className="relative">
                  <CardHeader className="text-center pb-8">
                    <div className={`w-12 h-12 mx-auto mb-4 rounded-lg flex items-center justify-center ${
                      plan.color === 'blue' ? 'bg-blue-100' :
                      plan.color === 'green' ? 'bg-green-100' : 'bg-gray-100'
                    }`}>
                      <IconComponent className={`h-6 w-6 ${
                        plan.color === 'blue' ? 'text-blue-600' :
                        plan.color === 'green' ? 'text-green-600' : 'text-gray-600'
                      }`} />
                    </div>
                    <CardTitle className="text-2xl">{plan.name}</CardTitle>
                    <div className="flex items-baseline justify-center gap-1">
                      <span className="text-4xl font-bold">{plan.price}</span>
                      <span className="text-gray-500">{plan.period}</span>
                    </div>
                    <p className="text-gray-600">{plan.description}</p>
                  </CardHeader>

                  <CardContent className="pt-0">
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium mb-3">What's included:</h4>
                        <ul className="space-y-2">
                          {plan.features.map((feature, idx) => (
                            <li key={idx} className="flex items-start gap-2">
                              <Check className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                              <span className="text-sm">{feature}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    <Button
                      className="w-full mt-6"
                      variant={index === 0 ? 'outline' : 'default'}
                      asChild
                    >
                      <Link href="/register">
                        {plan.cta}
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </Link>
                    </Button>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </section>

        {/* Enterprise Features */}
        <section className="space-y-12">
          <div className="text-center">
            <h2 className="text-3xl font-bold mb-4">Enterprise Features</h2>
            <p className="text-gray-600 text-lg">Additional features for large organizations</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card>
              <CardHeader>
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                  <Shield className="h-6 w-6 text-blue-600" />
                </div>
                <CardTitle>Advanced Security</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  SOC 2 compliance, SSO integration, advanced user permissions,
                  and data encryption for enterprise-grade security.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                  <Building className="h-6 w-6 text-green-600" />
                </div>
                <CardTitle>White Label</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Custom branding, domain, and styling to create a
                  seamless experience for your clients and specialists.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                  <Zap className="h-6 w-6 text-purple-600" />
                </div>
                <CardTitle>API Integration</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  REST APIs for custom integrations with your existing
                  systems, HR platforms, and workflow tools.
                </p>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* FAQ */}
        <section className="space-y-12">
          <div className="text-center">
            <h2 className="text-3xl font-bold mb-4">Frequently Asked Questions</h2>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div className="space-y-6">
              <div>
                <h3 className="font-semibold mb-2">Can I upgrade or downgrade my plan?</h3>
                <p className="text-gray-600 text-sm">
                  Yes, you can change your plan at any time. Upgrades take effect immediately,
                  and downgrades take effect at the next billing cycle.
                </p>
              </div>

              <div>
                <h3 className="font-semibold mb-2">What payment methods do you accept?</h3>
                <p className="text-gray-600 text-sm">
                  We accept all major credit cards, PayPal, and wire transfers for
                  enterprise accounts. All payments are processed securely.
                </p>
              </div>

              <div>
                <h3 className="font-semibold mb-2">Is there a setup fee?</h3>
                <p className="text-gray-600 text-sm">
                  No setup fees for Starter and Professional plans. Enterprise plans
                  may include implementation support based on requirements.
                </p>
              </div>
            </div>

            <div className="space-y-6">
              <div>
                <h3 className="font-semibold mb-2">Do you offer refunds?</h3>
                <p className="text-gray-600 text-sm">
                  We offer a 30-day money-back guarantee for all paid plans.
                  If you're not satisfied, we'll refund your payment.
                </p>
              </div>

              <div>
                <h3 className="font-semibold mb-2">Can I cancel anytime?</h3>
                <p className="text-gray-600 text-sm">
                  Yes, you can cancel your subscription at any time. Your account
                  will remain active until the end of your current billing period.
                </p>
              </div>

              <div>
                <h3 className="font-semibold mb-2">What's included in support?</h3>
                <p className="text-gray-600 text-sm">
                  All plans include help center access. Professional includes email/phone support.
                  Enterprise includes dedicated account management.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 md:p-12 text-white text-center">
          <div className="max-w-3xl mx-auto space-y-6">
            <h2 className="text-3xl md:text-4xl font-bold">
              Ready to get started?
            </h2>
            <p className="text-lg opacity-90">
              Join thousands of BCM professionals who trust our platform
              to grow their business and find the right expertise.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" variant="secondary" asChild>
                <Link href="/register">
                  <Users className="mr-2 h-5 w-5" />
                  Start Free Trial
                </Link>
              </Button>
              <Button size="lg" variant="outline" className="text-white border-white hover:bg-white hover:text-blue-600" asChild>
                <Link href="/contact">
                  Contact Sales
                </Link>
              </Button>
            </div>
          </div>
        </section>
      </div>
    </AppLayout>
  )
}