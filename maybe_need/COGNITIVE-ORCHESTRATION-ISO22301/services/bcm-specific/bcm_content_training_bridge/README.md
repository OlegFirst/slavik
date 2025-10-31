# BCM Content & Training Bridge Module

## Overview
This is a **Bridge Module** that connects BCM content (templates & scenarios) with Odoo's native gamification, e-learning, calendar, and event systems.

## Architecture

### Bridge Pattern Implementation
```
BCM Modules          Bridge Module              Odoo Native Modules
-----------          -------------              -------------------
bcm_templates    →   Content Bridge      →      gamification
bcm_scenario_hub →   Learning Bridge     →      website_slides
bcm_training     →   Calendar Bridge     →      calendar
                 →   Achievement System  →      survey
```

## Features

### 🎮 Gamification Bridge
- **Points System**: Award points for content creation, review, usage, and ratings
- **Badges & Achievements**: Template Master, Scenario Expert, Quality Reviewer
- **Leaderboards**: Weekly, Monthly, and All-time rankings
- **Team Competitions**: Department vs Department challenges

### 📚 E-Learning Bridge
- **Auto-conversion**: Convert templates to e-learning slides
- **Scenario Exercises**: Interactive scenario-based learning
- **Learning Paths**: Beginner → Practitioner → Expert
- **Assessments**: Auto-generated quizzes from content
- **Certifications**: BCM competency certificates

### 📅 Calendar & Events Bridge
- **Template Reviews**: Schedule periodic template reviews
- **Scenario Exercises**: Plan and track scenario drills
- **Training Sessions**: Automated training scheduling
- **Deadline Tracking**: Content update reminders
- **Event Analytics**: Participation and completion tracking

## Models

### Core Bridge Models
1. **ContentGamificationBridge** (`bcm.content.gamification.bridge`)
   - Links content to gamification system
   - Manages points and achievements
   - Tracks user progress

2. **UserAchievement** (`bcm.user.achievement`)
   - Individual achievement tracking
   - Leaderboard rankings
   - Badge management

3. **ContentLearningBridge** (`bcm.content.learning.bridge`)
   - Content to course conversion
   - Learning path management
   - Quiz generation

4. **ContentCalendarBridge** (`bcm.content.calendar.bridge`)
   - Event scheduling automation
   - Review cycle management
   - Exercise planning

## Usage Examples

### Award Points for Content Creation
```python
bridge = env['bcm.content.gamification.bridge']
points = bridge.award_points(
    user_id=user.id,
    action_type='create',
    content_type='bcm.template',
    content_id=template.id
)
```

### Convert Template to E-Learning Course
```python
learning_bridge = env['bcm.content.learning.bridge']
slide = learning_bridge.convert_template_to_slide(template_id)
```

### Schedule Scenario Exercise
```python
calendar_bridge = env['bcm.content.calendar.bridge']
event = calendar_bridge.schedule_scenario_exercise(
    scenario_id=scenario.id,
    participant_ids=participant_ids
)
```

## Configuration

### Dependencies
- `bcm_templates`: Original template module
- `bcm_scenario_hub`: Original scenario module
- `bcm_training`: BCM training module
- `gamification`: Odoo gamification (native)
- `calendar`: Odoo calendar (native)
- `website_slides`: Odoo e-learning (native)
- `survey`: Odoo surveys (native)

### Installation
1. Ensure all dependencies are installed
2. Install this bridge module
3. Configure gamification rules
4. Set up learning paths
5. Configure calendar automation

## Benefits

### For Organizations
- **Increased Engagement**: Gamification drives participation
- **Better Training**: Interactive e-learning from real content
- **Automated Scheduling**: Never miss reviews or exercises
- **Performance Tracking**: Analytics on content usage and learning

### For Users
- **Recognition**: Badges and leaderboards for contributions
- **Learning Paths**: Clear progression from beginner to expert
- **Automated Reminders**: Never miss important BCM activities
- **Interactive Learning**: Practical exercises from real scenarios

### For BCM Platform
- **Seamless Integration**: Leverages existing Odoo modules
- **No Duplication**: Bridge pattern avoids recreating functionality
- **Extensible**: Easy to add new bridge connections
- **Maintainable**: Clear separation of concerns

## Future Enhancements
- Integration with external LMS platforms
- AI-powered learning recommendations
- Virtual reality scenario exercises
- Blockchain certificates for achievements
- Mobile app for on-the-go learning

## Support
For issues or questions about this bridge module, please contact the BCM Platform Team.