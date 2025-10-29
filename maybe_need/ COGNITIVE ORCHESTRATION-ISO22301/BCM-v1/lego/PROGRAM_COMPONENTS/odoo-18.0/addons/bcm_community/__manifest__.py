# -*- coding: utf-8 -*-
{
    'name': 'BCM Community - Professional Marketplace & Knowledge Hub',
    'version': '18.0.2.0.0',
    'category': 'Business Continuity',
    'sequence': 25,
    'summary': 'BCM professional marketplace, community forum, and knowledge base - Uber for BCM specialists',
    'description': '''
BCM Community Module - Professional Marketplace & Knowledge Exchange
===================================================================

🚀 The Ultimate BCM Professional Platform - Like Uber for BCM Specialists!

This module transforms the BCM platform into a comprehensive marketplace where:
- Organizations can find and hire BCM specialists
- BCM professionals can offer their expertise and services
- Knowledge is shared through forums and community collaboration

MARKETPLACE FEATURES:
=====================
🎯 For Organizations (Clients):
-------------------------------
* Post BCM service requests (consulting, assessments, training, etc.)
* Browse verified BCM specialist profiles
* Review portfolios and certifications
* Compare proposals and pricing
* Track project progress and milestones
* Rate and review specialists

👨‍💼 For BCM Specialists:
-------------------------
* Create professional profiles showcasing expertise
* List services and set pricing (hourly, fixed, retainer)
* Submit proposals for projects
* Build portfolio with case studies
* Track time and billing
* Get verified status and badges
* Build reputation through reviews

📊 Marketplace Capabilities:
----------------------------
* Smart matching algorithm (skills, industry, location)
* Secure payment processing and escrow
* Dispute resolution system
* Time tracking and invoicing
* Project milestone management
* Multi-currency support
* Contract templates

COMMUNITY FEATURES:
===================
📚 Knowledge Hub:
----------------
* Community Forums with BCM-specific categories
* Knowledge base and best practices library
* Expert Q&A system
* Case study repository
* Template marketplace

🏆 Reputation System:
--------------------
* Expert badges and certifications
* Review and rating system
* Points and gamification
* Verified specialist status
* Industry recognition

🤝 Networking:
-------------
* BCM professional directory
* Direct messaging between professionals
* Group discussions and webinars
* Event calendar and meetups
* Mentorship programs

SERVICE CATEGORIES:
==================
* Business Impact Analysis (BIA)
* Risk Assessment & Management
* BCM Planning & Strategy
* Crisis Management
* Emergency Response Planning
* Training & Workshops
* Compliance & Audit
* Implementation Support
* Digital Transformation
* Pandemic Planning

INDUSTRIES SERVED:
=================
* Financial Services
* Healthcare
* Manufacturing
* Technology
* Government
* Critical Infrastructure
* Retail & E-commerce
* Education
* Non-Profit Organizations

KEY DIFFERENTIATORS:
===================
✅ Verified BCM specialists only
✅ ISO 22301 compliance focus
✅ End-to-end project management
✅ Secure and compliant platform
✅ Global reach, local expertise
✅ Transparent pricing
✅ Quality guarantee

TECHNICAL FEATURES:
==================
* Real-time notifications
* Advanced search and filtering
* AI-powered matching
* Mobile-responsive design
* API integration capabilities
* Multi-language support
* Automated workflows
* Analytics and reporting
    ''',
    'author': 'BCM Platform Team',
    'website': 'https://github.com/SEH-foundation/ISO-22301',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'bcm_core',
        'bcm_base',
    ],
    'data': [
        'security/bcm_community_security.xml',
        'security/ir.model.access.csv',
        'data/forum_categories_data.xml',
        'data/expert_badges_data.xml',
        'views/forum_category_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/knowledge_demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
