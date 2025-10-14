# BCM Exercise Portal Implementation

## Overview
This implementation provides a comprehensive Exercise Portal for client exercise requests in the Odoo BCM platform. The portal allows clients to request, track, and manage business continuity exercises through a web interface.

## Features Implemented

### 1. Exercise Request Form (`/portal/exercise/request`)
- **Route**: `/portal/exercise/request`
- **Controller**: `BCMExercisePortal.portal_exercise_request_form()`
- **Template**: `portal_exercise_request_form`
- **Form Fields**:
  - Exercise type (tabletop/simulation/walkthrough/fullscale)
  - Scenario description
  - Participants selection (multi-select from company users)
  - Preferred date/time

### 2. Exercise Submission (`/portal/exercise/submit`)
- **Route**: `/portal/exercise/submit` (POST)
- **Controller**: `BCMExercisePortal.submit_exercise_request()`
- **Functionality**:
  - Creates exercise record in `bcm.exercise` model
  - Integrates with AI Orchestrator for scenario enhancement
  - Publishes `bcm.exercise.requested` event to EventBus
  - Redirects to status page with success message

### 3. Status Tracking Page (`/portal/exercise/status`)
- **Route**: `/portal/exercise/status`
- **Controller**: `BCMExercisePortal.portal_exercise_status()`
- **Template**: `portal_exercise_status`
- **Features**:
  - List of user's exercise requests
  - Status display: pending/scheduled/completed/cancelled
  - Display scheduled date/time and assigned facilitator
  - Admin view shows all company exercises
  - Action buttons for downloading materials and submitting feedback

### 4. Exercise Materials Download (`/portal/exercise/{id}/download`)
- **Route**: `/portal/exercise/<int:exercise_id>/download`
- **Controller**: `BCMExercisePortal.download_exercise_materials()`
- **Functionality**:
  - Generates exercise materials document
  - Includes exercise details, scenario, participants
  - Downloads as text file (placeholder for actual materials)

### 5. Post-Exercise Feedback (`/portal/exercise/{id}/feedback`)
- **Route**: `/portal/exercise/<int:exercise_id>/feedback`
- **Controller**: `BCMExercisePortal.exercise_feedback()`
- **Template**: `portal_exercise_feedback`
- **Features**:
  - Rating system for overall exercise, scenario realism, facilitator
  - Text feedback for learning objectives, improvements, comments
  - Publishes `bcm.exercise.feedback_submitted` event to EventBus

### 6. Exercise History (`/portal/exercise/history`)
- **Route**: `/portal/exercise/history`
- **Controller**: `BCMExercisePortal.exercise_history()`
- **Template**: `portal_exercise_history`
- **Features**:
  - Shows completed exercises
  - Links to materials download and feedback submission

## Backend Integration

### BCM Exercise Model (`bcm.exercise`)
**Location**: `core/odoo-18.0/addons/bcm_exercise/models/models.py`

**Fields**:
- `name`: Exercise name
- `exercise_type`: Selection (tabletop/walkthrough/simulation/fullscale)
- `scenario`: Text scenario description
- `ai_generated`: Boolean flag for AI-enhanced scenarios
- `state`: Status (requested/pending/scheduled/completed/cancelled)
- `planned_date`: Scheduled date/time
- `requested_by`: User who requested the exercise
- `assigned_facilitator`: Facilitator assigned to exercise
- `participant_ids`: Many2many relation to users
- `feedback_data`: JSON feedback from participants
- `feedback_submitted`: Boolean flag
- `company_id`: Multi-tenant company isolation

**Methods**:
- `action_schedule()`: Schedule exercise and send notifications
- `_send_status_notification()`: Send email notifications on status change

### EventBus Integration
**Location**: `core/odoo-18.0/addons/bcm_portal/models/bcm_exercise_eventbus.py`

**Events Published**:
- `bcm.exercise.requested`: When new exercise is requested
- `bcm.exercise.scheduled`: When exercise is scheduled
- `bcm.exercise.feedback_submitted`: When feedback is submitted
- `bcm.exercise.status_changed`: General status change notifications

**Event Listeners**:
- `handle_exercise_scheduled_event()`: Handle scheduling events
- `handle_exercise_completion_event()`: Handle completion events
- `action_notify_external_systems()`: Notify external integrations

### External System Integration
- **Moodle Integration**: Creates training courses for scheduled exercises
- **TheHive Integration**: Creates cases for post-exercise reviews

## Email Notification System

**Location**: `bcm.exercise._send_status_notification()`

**Notifications Sent**:
- Exercise request confirmation to requestor
- Status update notifications (pending, scheduled, completed)
- Participant notifications for scheduled exercises
- HTML email templates with exercise details

**Recipients**:
- Exercise requestor (always notified)
- Participants (for scheduled/in-progress exercises)

## Portal Navigation

### Main Portal Integration
**Template**: `portal_my_home_menu_exercise`
- Exercise request/status/history buttons
- Quick stats showing user's exercise count and pending requests

### Navigation Menu
**Template**: `exercise_portal_nav_extension`
- Dropdown menu for exercise-related pages
- Active state highlighting for current page

## File Structure

```
core/odoo-18.0/addons/bcm_portal/
├── controllers/
│   ├── __init__.py (updated)
│   └── exercise_portal.py (new)
├── models/
│   ├── __init__.py (updated)
│   ├── bcm_exercise_portal.py (existing, extended)
│   └── bcm_exercise_eventbus.py (new)
├── templates/
│   └── bcm_exercise_templates.xml (new)
└── __manifest__.py (updated)

core/odoo-18.0/addons/bcm_exercise/
└── models/
    └── models.py (extended)
```

## Usage Flow

1. **Request Exercise**: User visits `/portal/exercise/request` and fills out form
2. **AI Enhancement**: System enhances scenario using AI Orchestrator
3. **EventBus Notification**: `bcm.exercise.requested` event published
4. **Admin Review**: BCM admin reviews and schedules exercise
5. **Status Updates**: User tracks progress via `/portal/exercise/status`
6. **Exercise Execution**: Exercise is conducted by facilitator
7. **Materials Access**: Participants download materials via portal
8. **Feedback Collection**: Post-exercise feedback submitted via portal
9. **History Tracking**: Completed exercises visible in history

## Integration Points

### AI Orchestrator
- **Endpoint**: `/api/recommendations`
- **Purpose**: Enhance exercise scenarios with realistic elements
- **Data**: Exercise type, base scenario, participant count, company context

### EventBus
- **Service**: External EventBus service
- **Purpose**: Decouple exercise events from core system
- **Events**: Request, schedule, feedback, completion notifications

### Email System
- **Service**: Odoo mail system
- **Purpose**: Notify users of exercise status changes
- **Templates**: HTML emails with exercise details

## Security & Access Control

- **Multi-tenancy**: All records isolated by `company_id`
- **Portal Authentication**: Requires `auth='user'`
- **Access Validation**: Users can only access their company's exercises
- **Admin Features**: Enhanced view for system administrators

## Next Steps

1. **Email Templates**: Create proper Odoo email templates
2. **File Management**: Implement actual file storage for exercise materials
3. **Reporting**: Add exercise analytics and reporting features
4. **Mobile Optimization**: Enhance mobile responsiveness
5. **Calendar Integration**: Add calendar scheduling features
6. **Notifications**: Real-time browser notifications
7. **Approval Workflow**: Multi-step approval process for exercises

## Technical Requirements

- **Odoo Version**: 18.0
- **Dependencies**: 
  - `portal` (Odoo portal framework)
  - `mail` (Email functionality)
  - `bcm_intelligent_base` (AI integration)
  - `bcm_clients` (Client management)
- **External Services**:
  - AI Orchestrator service
  - EventBus service
  - Email SMTP server

## Testing

The implementation includes:
- Form validation (client and server-side)
- Error handling for external service failures
- Graceful degradation when AI/EventBus services unavailable
- Multi-tenant data isolation
- Email delivery error handling

This implementation provides a solid foundation for BCM exercise management through the portal interface, with room for future enhancements and integrations.
