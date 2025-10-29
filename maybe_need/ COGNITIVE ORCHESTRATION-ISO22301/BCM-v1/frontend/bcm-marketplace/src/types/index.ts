// Base types
export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role: 'client' | 'specialist' | 'admin';
}

// Specialist types
export interface Specialist {
  id: string;
  userId: string;
  name: string;
  title: string;
  bio: string;
  yearsExperience: number;
  hourlyRate: number;
  currency: string;
  avatar?: string;
  rating: number;
  reviewCount: number;
  completedProjects: number;
  isVerified: boolean;
  availabilityStatus: 'available' | 'busy' | 'unavailable';
  location: {
    country: string;
    city: string;
    timezone: string;
  };
  remoteAvailable: boolean;
  onsiteAvailable: boolean;
  specializations: Specialization[];
  industries: Industry[];
  certifications: Certification[];
  services: SpecialistService[];
  portfolioItems: PortfolioItem[];
  languages: Language[];
  profileCompletion: number;
  createdAt: string;
  updatedAt: string;
}

export interface Specialization {
  id: string;
  name: string;
  code: string;
  icon?: string;
}

export interface Industry {
  id: string;
  name: string;
  code: string;
}

export interface Certification {
  id: string;
  name: string;
  issuingOrganization: string;
  issueDate: string;
  expiryDate?: string;
  credentialId?: string;
  credentialUrl?: string;
  isVerified: boolean;
}

export interface SpecialistService {
  id: string;
  name: string;
  description: string;
  serviceType: 'consulting' | 'assessment' | 'planning' | 'training' | 'audit' | 'implementation' | 'crisis_support' | 'other';
  pricingModel: 'hourly' | 'fixed' | 'retainer' | 'project';
  basePrice: number;
  currency: string;
  durationEstimate?: number;
  minEngagement?: number;
  deliveryMode: 'remote' | 'onsite' | 'hybrid';
}

export interface PortfolioItem {
  id: string;
  name: string;
  description: string;
  clientIndustry: string;
  projectType: string;
  date: string;
  duration?: string;
  teamSize?: number;
  role: string;
  keyAchievements: string;
  technologiesUsed?: string;
  isFeatured: boolean;
  attachments?: string[];
}

export interface Language {
  code: string;
  name: string;
  level: 'basic' | 'conversational' | 'fluent' | 'native';
}

// Service Request types
export interface ServiceRequest {
  id: string;
  name: string;
  description: string;
  clientId: string;
  clientName: string;
  companyName?: string;
  industryId?: string;
  companySize?: 'small' | 'medium' | 'large' | 'enterprise';
  serviceType: 'consulting' | 'assessment' | 'bia' | 'planning' | 'training' | 'audit' | 'implementation' | 'crisis_support' | 'other';
  urgency: 'low' | 'medium' | 'high' | 'urgent';
  scopeOfWork?: string;
  deliverables?: string;
  startDate?: string;
  endDate?: string;
  durationEstimate?: number;
  budgetType: 'hourly' | 'fixed' | 'negotiable';
  budgetMin?: number;
  budgetMax?: number;
  currency: string;
  requiredCertifications?: string;
  requiredExperience?: number;
  requiredSkills: Specialization[];
  workLocation: 'remote' | 'onsite' | 'hybrid';
  locationCountry?: string;
  locationState?: string;
  locationCity?: string;
  state: 'draft' | 'posted' | 'in_review' | 'assigned' | 'in_progress' | 'completed' | 'cancelled';
  proposalIds: string[];
  proposalCount: number;
  selectedProposalId?: string;
  selectedSpecialistId?: string;
  isPublic: boolean;
  invitedSpecialistIds?: string[];
  postedDate?: string;
  deadline?: string;
  completionDate?: string;
  createdAt: string;
  updatedAt: string;
}

// Proposal types
export interface ServiceProposal {
  id: string;
  requestId: string;
  specialistId: string;
  coverLetter: string;
  proposedApproach?: string;
  proposedStartDate?: string;
  proposedDuration?: number;
  proposedEndDate?: string;
  pricingType: 'hourly' | 'fixed' | 'milestone';
  proposedRate?: number;
  totalCost?: number;
  currency: string;
  relevantExperience?: string;
  portfolioItemIds: string[];
  attachments?: string[];
  state: 'draft' | 'submitted' | 'under_review' | 'accepted' | 'rejected' | 'withdrawn';
  submissionDate?: string;
  reviewDate?: string;
  clientNotes?: string;
  rejectionReason?: string;
  createdAt: string;
  updatedAt: string;
}

// Project types
export interface Project {
  id: string;
  name: string;
  code: string;
  requestId?: string;
  proposalId?: string;
  specialistId: string;
  clientId: string;
  description?: string;
  objectives?: string;
  deliverables?: string;
  startDate: string;
  endDate?: string;
  actualStartDate?: string;
  actualEndDate?: string;
  budget: number;
  spentAmount: number;
  currency: string;
  paymentTerms?: string;
  progress: number;
  milestones: ProjectMilestone[];
  timesheets: ProjectTimesheet[];
  totalHours: number;
  state: 'new' | 'in_progress' | 'on_hold' | 'completed' | 'cancelled';
  specialistRating?: number;
  clientRating?: number;
  specialistReview?: string;
  clientReview?: string;
  createdAt: string;
  updatedAt: string;
}

export interface ProjectMilestone {
  id: string;
  projectId: string;
  name: string;
  description?: string;
  sequence: number;
  deadline?: string;
  completionDate?: string;
  deliverables?: string;
  acceptanceCriteria?: string;
  amount: number;
  currency: string;
  state: 'pending' | 'in_progress' | 'review' | 'approved' | 'rejected';
  attachments?: string[];
  approvedBy?: string;
  approvalDate?: string;
  rejectionReason?: string;
}

export interface ProjectTimesheet {
  id: string;
  projectId: string;
  specialistId: string;
  date: string;
  hours: number;
  description: string;
  taskType: 'analysis' | 'documentation' | 'meeting' | 'implementation' | 'review' | 'training' | 'other';
  hourlyRate: number;
  amount: number;
  currency: string;
  isBillable: boolean;
  isInvoiced: boolean;
  state: 'draft' | 'submitted' | 'approved' | 'rejected';
  approvedBy?: string;
  approvalDate?: string;
}

// Review types
export interface SpecialistReview {
  id: string;
  specialistId: string;
  projectId: string;
  reviewerId: string;
  overallRating: number;
  expertiseRating?: number;
  communicationRating?: number;
  timelinessRating?: number;
  valueRating?: number;
  reviewTitle?: string;
  reviewText: string;
  wouldRecommend: boolean;
  wouldHireAgain: boolean;
  isVerified: boolean;
  verificationNotes?: string;
  specialistResponse?: string;
  responseDate?: string;
  helpfulCount: number;
  unhelpfulCount: number;
  createdAt: string;
  updatedAt: string;
}

// Search and filter types
export interface SearchFilters {
  query?: string;
  serviceTypes?: string[];
  specializations?: string[];
  industries?: string[];
  rating?: {
    min: number;
    max: number;
  };
  experience?: {
    min: number;
    max: number;
  };
  hourlyRate?: {
    min: number;
    max: number;
  };
  location?: {
    country?: string;
    city?: string;
    remote?: boolean;
  };
  availability?: 'available' | 'busy' | 'all';
  verifiedOnly?: boolean;
  languages?: string[];
  sortBy?: 'relevance' | 'rating' | 'price_low' | 'price_high' | 'experience';
}

export interface SearchResults<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

export interface ApiError {
  success: false;
  error: string;
  details?: string;
  code?: string;
}