'use client'

import React, { useState } from 'react'
import { AppLayout } from '@/components/layout/AppLayout'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Star,
  Search,
  Filter,
  ThumbsUp,
  ThumbsDown,
  Calendar,
  Building,
  User,
  MessageCircle,
  Flag,
  CheckCircle,
  Award,
  TrendingUp,
  BarChart3,
  Users
} from 'lucide-react'

interface Review {
  id: string
  rating: number
  title: string
  comment: string
  reviewer: {
    name: string
    avatar?: string
    company: string
    title: string
    verified: boolean
  }
  reviewee: {
    name: string
    avatar?: string
    type: 'specialist' | 'client'
  }
  project: {
    id: string
    title: string
    type: string
    completionDate: string
    budget: string
  }
  aspects: {
    communication: number
    quality: number
    timeliness: number
    professionalism: number
    valueForMoney?: number
  }
  pros: string[]
  cons: string[]
  wouldRecommend: boolean
  isVerifiedPurchase: boolean
  helpfulVotes: number
  date: string
  response?: {
    content: string
    date: string
    author: string
  }
}

const mockReviews: Review[] = [
  {
    id: '1',
    rating: 5,
    title: 'Outstanding BCM expertise and professionalism',
    comment: 'Dr. Martinez exceeded our expectations in every way. Her deep knowledge of ISO 22301 and financial services BCM was evident from day one. The gap analysis was thorough, the recommendations were actionable, and the implementation roadmap was realistic and well-structured. She worked seamlessly with our team and delivered everything on time and within budget.',
    reviewer: {
      name: 'Sarah Johnson',
      company: 'FinTech Solutions Inc.',
      title: 'Risk Manager',
      verified: true
    },
    reviewee: {
      name: 'Dr. Sarah Martinez',
      type: 'specialist'
    },
    project: {
      id: 'proj_1',
      title: 'Financial Services BCM Gap Analysis',
      type: 'BCM Assessment',
      completionDate: '2024-01-15',
      budget: '$25,000'
    },
    aspects: {
      communication: 5,
      quality: 5,
      timeliness: 5,
      professionalism: 5,
      valueForMoney: 5
    },
    pros: [
      'Deep expertise in ISO 22301 and financial services',
      'Excellent communication and project management',
      'Delivered comprehensive and actionable recommendations',
      'Worked well with our internal team',
      'Completed project ahead of schedule'
    ],
    cons: [
      'Initial proposal could have been more detailed',
      'Minor formatting issues in first draft report'
    ],
    wouldRecommend: true,
    isVerifiedPurchase: true,
    helpfulVotes: 23,
    date: '2024-01-16',
    response: {
      content: 'Thank you Sarah for the wonderful review! It was a pleasure working with your team. The FinTech industry presents unique BCM challenges and I\'m glad we could develop a solution that fits your specific needs. Best of luck with the implementation!',
      date: '2024-01-17',
      author: 'Dr. Sarah Martinez'
    }
  },
  {
    id: '2',
    rating: 4,
    title: 'Great healthcare crisis training, some room for improvement',
    comment: 'Michael delivered excellent crisis management training for our healthcare network. The content was relevant and practical, and the delivery was engaging. The scenario-based exercises were particularly valuable. However, some of the materials could have been more specific to healthcare environments.',
    reviewer: {
      name: 'Dr. Emily Rodriguez',
      company: 'Regional Medical Center',
      title: 'COO',
      verified: true
    },
    reviewee: {
      name: 'Michael Thompson',
      type: 'specialist'
    },
    project: {
      id: 'proj_2',
      title: 'Healthcare Crisis Management Training',
      type: 'Training Program',
      completionDate: '2023-12-20',
      budget: '$12,000'
    },
    aspects: {
      communication: 4,
      quality: 4,
      timeliness: 5,
      professionalism: 5,
      valueForMoney: 4
    },
    pros: [
      'Engaging and interactive training delivery',
      'Practical scenario-based exercises',
      'Good understanding of healthcare operations',
      'Flexible with scheduling changes'
    ],
    cons: [
      'Some generic content not specific to healthcare',
      'Could have included more regulatory compliance aspects',
      'Limited follow-up resources provided'
    ],
    wouldRecommend: true,
    isVerifiedPurchase: true,
    helpfulVotes: 15,
    date: '2023-12-22'
  },
  {
    id: '3',
    rating: 5,
    title: 'Exceptional supply chain resilience assessment',
    comment: 'Jennifer\'s work on our manufacturing supply chain resilience was nothing short of exceptional. She identified critical vulnerabilities we hadn\'t considered and provided a comprehensive framework for improving our BCM posture. Her expertise in both manufacturing and supply chain risk management is impressive.',
    reviewer: {
      name: 'Robert Chen',
      company: 'AutoCorp Manufacturing',
      title: 'VP Operations',
      verified: true
    },
    reviewee: {
      name: 'Jennifer Liu',
      type: 'specialist'
    },
    project: {
      id: 'proj_3',
      title: 'Manufacturing Supply Chain Resilience Assessment',
      type: 'Risk Assessment',
      completionDate: '2023-11-30',
      budget: '$35,000'
    },
    aspects: {
      communication: 5,
      quality: 5,
      timeliness: 4,
      professionalism: 5,
      valueForMoney: 5
    },
    pros: [
      'Deep understanding of manufacturing operations',
      'Comprehensive risk identification and analysis',
      'Practical and implementable recommendations',
      'Excellent stakeholder management',
      'Strong analytical and reporting skills'
    ],
    cons: [
      'Project timeline extended by 2 weeks due to scope expansion'
    ],
    wouldRecommend: true,
    isVerifiedPurchase: true,
    helpfulVotes: 18,
    date: '2023-12-03'
  }
]

const ratingStats = {
  overall: 4.7,
  totalReviews: 156,
  distribution: {
    5: 78,
    4: 45,
    3: 23,
    2: 7,
    1: 3
  },
  aspects: {
    communication: 4.8,
    quality: 4.6,
    timeliness: 4.5,
    professionalism: 4.9,
    valueForMoney: 4.4
  },
  recommendationRate: 94
}

export default function ReviewsPage() {
  const [activeTab, setActiveTab] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [ratingFilter, setRatingFilter] = useState('all')
  const [showWriteReview, setShowWriteReview] = useState(false)

  const [newReview, setNewReview] = useState({
    rating: 0,
    title: '',
    comment: '',
    communication: 0,
    quality: 0,
    timeliness: 0,
    professionalism: 0,
    valueForMoney: 0,
    pros: [''],
    cons: [''],
    wouldRecommend: true
  })

  const renderStars = (rating: number, size = 'w-4 h-4') => {
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map(star => (
          <Star
            key={star}
            className={`${size} ${
              star <= rating
                ? 'text-yellow-400 fill-yellow-400'
                : 'text-gray-300'
            }`}
          />
        ))}
      </div>
    )
  }

  const renderInteractiveStars = (rating: number, onRatingChange: (rating: number) => void, size = 'w-5 h-5') => {
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map(star => (
          <Star
            key={star}
            className={`${size} cursor-pointer ${
              star <= rating
                ? 'text-yellow-400 fill-yellow-400'
                : 'text-gray-300 hover:text-yellow-200'
            }`}
            onClick={() => onRatingChange(star)}
          />
        ))}
      </div>
    )
  }

  const filteredReviews = mockReviews.filter(review => {
    const matchesSearch = review.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         review.comment.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         review.reviewer.name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesRating = ratingFilter === 'all' || review.rating.toString() === ratingFilter
    return matchesSearch && matchesRating
  })

  if (showWriteReview) {
    return (
      <AppLayout>
        <div className="max-w-4xl mx-auto space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">Write a Review</h1>
              <p className="text-gray-600">Share your experience with the BCM community</p>
            </div>
            <Button variant="outline" onClick={() => setShowWriteReview(false)}>
              Cancel
            </Button>
          </div>

          <Card>
            <CardContent className="p-6">
              <div className="space-y-6">
                {/* Overall Rating */}
                <div>
                  <label className="block text-sm font-medium mb-2">Overall Rating *</label>
                  <div className="flex items-center gap-4">
                    {renderInteractiveStars(newReview.rating, (rating) =>
                      setNewReview(prev => ({ ...prev, rating }))
                    , 'w-8 h-8')}
                    <span className="text-lg font-semibold">
                      {newReview.rating > 0 ? `${newReview.rating}/5` : 'Select rating'}
                    </span>
                  </div>
                </div>

                {/* Review Title */}
                <div>
                  <label className="block text-sm font-medium mb-2">Review Title *</label>
                  <Input
                    value={newReview.title}
                    onChange={(e) => setNewReview(prev => ({ ...prev, title: e.target.value }))}
                    placeholder="Summarize your experience in one line"
                  />
                </div>

                {/* Review Comment */}
                <div>
                  <label className="block text-sm font-medium mb-2">Review Comment *</label>
                  <Textarea
                    value={newReview.comment}
                    onChange={(e) => setNewReview(prev => ({ ...prev, comment: e.target.value }))}
                    placeholder="Share details about your experience..."
                    rows={6}
                  />
                </div>

                {/* Aspect Ratings */}
                <div>
                  <label className="block text-sm font-medium mb-4">Rate Specific Aspects</label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries({
                      communication: 'Communication',
                      quality: 'Quality of Work',
                      timeliness: 'Timeliness',
                      professionalism: 'Professionalism',
                      valueForMoney: 'Value for Money'
                    }).map(([key, label]) => (
                      <div key={key} className="flex items-center justify-between">
                        <span className="text-sm">{label}</span>
                        {renderInteractiveStars(
                          newReview[key as keyof typeof newReview] as number,
                          (rating) => setNewReview(prev => ({ ...prev, [key]: rating }))
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recommendation */}
                <div>
                  <label className="block text-sm font-medium mb-2">Would you recommend this specialist?</label>
                  <div className="flex gap-4">
                    <label className="flex items-center gap-2">
                      <input
                        type="radio"
                        checked={newReview.wouldRecommend === true}
                        onChange={() => setNewReview(prev => ({ ...prev, wouldRecommend: true }))}
                      />
                      <span>Yes, I would recommend</span>
                    </label>
                    <label className="flex items-center gap-2">
                      <input
                        type="radio"
                        checked={newReview.wouldRecommend === false}
                        onChange={() => setNewReview(prev => ({ ...prev, wouldRecommend: false }))}
                      />
                      <span>No, I would not recommend</span>
                    </label>
                  </div>
                </div>

                <div className="flex justify-end gap-4">
                  <Button variant="outline" onClick={() => setShowWriteReview(false)}>
                    Cancel
                  </Button>
                  <Button disabled={!newReview.rating || !newReview.title || !newReview.comment}>
                    Submit Review
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold">Reviews & Ratings</h1>
            <p className="text-gray-600">Community feedback and specialist ratings</p>
          </div>
          <Button onClick={() => setShowWriteReview(true)} className="flex items-center gap-2">
            <Star className="h-4 w-4" />
            Write Review
          </Button>
        </div>

        {/* Rating Overview */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Overall Rating */}
          <Card>
            <CardContent className="p-6 text-center">
              <div className="text-4xl font-bold text-gray-900 mb-2">{ratingStats.overall}</div>
              {renderStars(Math.round(ratingStats.overall), 'w-6 h-6')}
              <p className="text-sm text-gray-600 mt-2">
                Based on {ratingStats.totalReviews} reviews
              </p>
              <p className="text-sm text-green-600 font-medium mt-1">
                {ratingStats.recommendationRate}% recommend
              </p>
            </CardContent>
          </Card>

          {/* Rating Distribution */}
          <Card>
            <CardContent className="p-6">
              <h3 className="font-semibold mb-4">Rating Distribution</h3>
              <div className="space-y-2">
                {[5, 4, 3, 2, 1].map(rating => {
                  const count = ratingStats.distribution[rating as keyof typeof ratingStats.distribution]
                  const percentage = (count / ratingStats.totalReviews) * 100
                  return (
                    <div key={rating} className="flex items-center gap-2">
                      <span className="text-sm w-8">{rating}</span>
                      <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-yellow-400 h-2 rounded-full"
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                      <span className="text-sm text-gray-600 w-8">{count}</span>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          {/* Aspect Ratings */}
          <Card>
            <CardContent className="p-6">
              <h3 className="font-semibold mb-4">Aspect Ratings</h3>
              <div className="space-y-3">
                {Object.entries(ratingStats.aspects).map(([aspect, rating]) => (
                  <div key={aspect} className="flex items-center justify-between">
                    <span className="text-sm capitalize">
                      {aspect.replace(/([A-Z])/g, ' $1').trim()}
                    </span>
                    <div className="flex items-center gap-2">
                      {renderStars(Math.round(rating))}
                      <span className="text-sm font-medium">{rating}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <TabsList>
              <TabsTrigger value="all">All Reviews</TabsTrigger>
              <TabsTrigger value="recent">Recent</TabsTrigger>
              <TabsTrigger value="helpful">Most Helpful</TabsTrigger>
            </TabsList>

            {/* Filters */}
            <div className="flex gap-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search reviews..."
                  className="pl-10 w-64"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <select
                value={ratingFilter}
                onChange={(e) => setRatingFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm"
              >
                <option value="all">All Ratings</option>
                <option value="5">5 Stars</option>
                <option value="4">4 Stars</option>
                <option value="3">3 Stars</option>
                <option value="2">2 Stars</option>
                <option value="1">1 Star</option>
              </select>
            </div>
          </div>

          <TabsContent value="all" className="space-y-4">
            {filteredReviews.map(review => (
              <Card key={review.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  {/* Review Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-start gap-4">
                      <Avatar className="h-12 w-12">
                        <AvatarImage src={review.reviewer.avatar} />
                        <AvatarFallback>
                          {review.reviewer.name.split(' ').map(n => n[0]).join('')}
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-semibold">{review.reviewer.name}</h4>
                          {review.reviewer.verified && (
                            <Badge variant="outline" className="text-blue-600 border-blue-600 text-xs">
                              <CheckCircle className="h-3 w-3 mr-1" />
                              Verified
                            </Badge>
                          )}
                          {review.isVerifiedPurchase && (
                            <Badge variant="outline" className="text-green-600 border-green-600 text-xs">
                              <Award className="h-3 w-3 mr-1" />
                              Verified Project
                            </Badge>
                          )}
                        </div>
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <Building className="h-3 w-3" />
                          <span>{review.reviewer.title} at {review.reviewer.company}</span>
                        </div>
                        <div className="flex items-center gap-2 mt-1">
                          {renderStars(review.rating)}
                          <span className="text-sm font-medium">{review.rating}/5</span>
                          <span className="text-xs text-gray-500">•</span>
                          <span className="text-xs text-gray-500">{review.date}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Project Info */}
                  <div className="bg-blue-50 p-3 rounded-lg mb-4">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium">Project: {review.project.title}</span>
                      <div className="flex items-center gap-4 text-gray-600">
                        <span>{review.project.type}</span>
                        <span>•</span>
                        <span>{review.project.budget}</span>
                        <span>•</span>
                        <span>Completed {review.project.completionDate}</span>
                      </div>
                    </div>
                  </div>

                  {/* Review Content */}
                  <div className="mb-4">
                    <h5 className="font-semibold mb-2">{review.title}</h5>
                    <p className="text-gray-700 leading-relaxed">{review.comment}</p>
                  </div>

                  {/* Aspect Ratings */}
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4 p-4 bg-gray-50 rounded-lg">
                    {Object.entries(review.aspects).map(([aspect, rating]) => (
                      <div key={aspect} className="text-center">
                        <div className="text-xs text-gray-600 mb-1 capitalize">
                          {aspect.replace(/([A-Z])/g, ' $1').trim()}
                        </div>
                        <div className="flex items-center justify-center gap-1">
                          {renderStars(rating, 'w-3 h-3')}
                          <span className="text-xs font-medium">{rating}</span>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Pros and Cons */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <h6 className="font-semibold text-green-700 mb-2 flex items-center gap-1">
                        <ThumbsUp className="h-4 w-4" />
                        Pros
                      </h6>
                      <ul className="space-y-1">
                        {review.pros.map((pro, index) => (
                          <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                            <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0" />
                            {pro}
                          </li>
                        ))}
                      </ul>
                    </div>
                    {review.cons.length > 0 && (
                      <div>
                        <h6 className="font-semibold text-orange-700 mb-2 flex items-center gap-1">
                          <ThumbsDown className="h-4 w-4" />
                          Areas for Improvement
                        </h6>
                        <ul className="space-y-1">
                          {review.cons.map((con, index) => (
                            <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                              <div className="w-2 h-2 bg-orange-500 rounded-full mt-2 flex-shrink-0" />
                              {con}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>

                  {/* Recommendation */}
                  <div className="flex items-center justify-between mb-4 p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-2">
                      {review.wouldRecommend ? (
                        <>
                          <ThumbsUp className="h-4 w-4 text-green-600" />
                          <span className="text-sm font-medium text-green-700">
                            Recommends this specialist
                          </span>
                        </>
                      ) : (
                        <>
                          <ThumbsDown className="h-4 w-4 text-red-600" />
                          <span className="text-sm font-medium text-red-700">
                            Does not recommend this specialist
                          </span>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Specialist Response */}
                  {review.response && (
                    <div className="border-l-4 border-blue-500 pl-4 mt-4 bg-blue-50 p-4 rounded-r-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <Avatar className="h-6 w-6">
                          <AvatarFallback className="text-xs">
                            {review.response.author.split(' ').map(n => n[0]).join('')}
                          </AvatarFallback>
                        </Avatar>
                        <span className="font-semibold text-sm">{review.response.author}</span>
                        <Badge variant="outline" className="text-xs">Specialist Response</Badge>
                        <span className="text-xs text-gray-500">{review.response.date}</span>
                      </div>
                      <p className="text-sm text-gray-700">{review.response.content}</p>
                    </div>
                  )}

                  {/* Review Actions */}
                  <div className="flex items-center justify-between pt-4 border-t">
                    <div className="flex items-center gap-4">
                      <Button variant="ghost" size="sm" className="flex items-center gap-1">
                        <ThumbsUp className="h-3 w-3" />
                        Helpful ({review.helpfulVotes})
                      </Button>
                      <Button variant="ghost" size="sm" className="flex items-center gap-1">
                        <MessageCircle className="h-3 w-3" />
                        Comment
                      </Button>
                    </div>
                    <Button variant="ghost" size="sm" className="flex items-center gap-1 text-gray-500">
                      <Flag className="h-3 w-3" />
                      Report
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          <TabsContent value="recent">
            <div className="text-center py-12">
              <Calendar className="h-12 w-12 mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Recent Reviews</h3>
              <p className="text-gray-600">Most recently submitted reviews will appear here</p>
            </div>
          </TabsContent>

          <TabsContent value="helpful">
            <div className="text-center py-12">
              <ThumbsUp className="h-12 w-12 mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Most Helpful Reviews</h3>
              <p className="text-gray-600">Reviews rated as most helpful by the community</p>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </AppLayout>
  )
}