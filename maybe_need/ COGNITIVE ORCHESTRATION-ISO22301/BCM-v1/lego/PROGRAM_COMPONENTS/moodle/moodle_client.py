# -*- coding: utf-8 -*-
"""
Moodle LMS Client for BCM Platform
Provides integration between Moodle LMS and BCM Platform for training and competency management
"""
import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)

@dataclass
class MoodleCourse:
    """Moodle course representation"""
    id: int
    fullname: str
    shortname: str
    categoryid: int
    summary: str = ""
    format: str = "topics"
    startdate: Optional[int] = None
    enddate: Optional[int] = None
    visible: bool = True
    numsections: int = 4
    
@dataclass
class MoodleUser:
    """Moodle user representation"""
    id: Optional[int] = None
    username: str = ""
    password: str = ""
    firstname: str = ""
    lastname: str = ""
    email: str = ""
    lang: str = "en"
    timezone: str = "Europe/Kiev"
    mailformat: int = 1
    description: str = ""
    city: str = ""
    country: str = "UA"

@dataclass
class MoodleEnrollment:
    """Moodle enrollment representation"""
    roleid: int
    userid: int
    courseid: int
    timestart: Optional[int] = None
    timeend: Optional[int] = None
    suspend: int = 0

@dataclass
class BCMCompetency:
    """BCM competency framework item"""
    shortname: str
    idnumber: str
    description: str
    parent: str = ""
    scalevalues: str = "Not competent,Competent"
    ruletype: int = 1
    ruleoutcome: int = 1

class MoodleClient:
    """Moodle Web Services API Client"""
    
    def __init__(self, url: str, token: str, verify_ssl: bool = True):
        self.base_url = url.rstrip('/')
        self.token = token
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'BCM-Platform-Moodle-Client/1.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        })
        
    def _make_request(self, wsfunction: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request to Moodle"""
        url = f"{self.base_url}/webservice/rest/server.php"
        
        data = {
            'wstoken': self.token,
            'wsfunction': wsfunction,
            'moodlewsrestformat': 'json',
            **params
        }
        
        try:
            response = self.session.post(url, data=data, verify=self.verify_ssl, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Check for Moodle errors
            if isinstance(result, dict) and 'exception' in result:
                logger.error(f"Moodle API error: {result}")
                raise Exception(f"Moodle error: {result.get('message', 'Unknown error')}")
                
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            raise Exception(f"Invalid response from Moodle: {e}")
    
    def get_site_info(self) -> Dict[str, Any]:
        """Get Moodle site information"""
        return self._make_request('core_webservice_get_site_info', {})
    
    def create_user(self, user: MoodleUser) -> Dict[str, Any]:
        """Create user in Moodle"""
        user_data = {
            'users[0][username]': user.username,
            'users[0][password]': user.password,
            'users[0][firstname]': user.firstname,
            'users[0][lastname]': user.lastname,
            'users[0][email]': user.email,
            'users[0][lang]': user.lang,
            'users[0][timezone]': user.timezone,
            'users[0][mailformat]': user.mailformat,
            'users[0][description]': user.description,
            'users[0][city]': user.city,
            'users[0][country]': user.country,
        }
        
        result = self._make_request('core_user_create_users', user_data)
        return result[0] if result else {}
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        params = {
            'criteria[0][key]': 'email',
            'criteria[0][value]': email
        }
        
        result = self._make_request('core_user_get_users', params)
        users = result.get('users', [])
        return users[0] if users else None
    
    def create_course(self, course: MoodleCourse) -> Dict[str, Any]:
        """Create course in Moodle"""
        course_data = {
            'courses[0][fullname]': course.fullname,
            'courses[0][shortname]': course.shortname,
            'courses[0][categoryid]': course.categoryid,
            'courses[0][summary]': course.summary,
            'courses[0][format]': course.format,
            'courses[0][visible]': 1 if course.visible else 0,
            'courses[0][numsections]': course.numsections,
        }
        
        if course.startdate:
            course_data['courses[0][startdate]'] = course.startdate
        if course.enddate:
            course_data['courses[0][enddate]'] = course.enddate
            
        result = self._make_request('core_course_create_courses', course_data)
        return result[0] if result else {}
    
    def get_course_by_shortname(self, shortname: str) -> Optional[Dict[str, Any]]:
        """Get course by shortname"""
        params = {
            'criteria[0][key]': 'shortname',
            'criteria[0][value]': shortname
        }
        
        result = self._make_request('core_course_get_courses_by_field', params)
        courses = result.get('courses', [])
        return courses[0] if courses else None
    
    def enroll_user(self, enrollment: MoodleEnrollment) -> bool:
        """Enroll user in course"""
        enroll_data = {
            'enrolments[0][roleid]': enrollment.roleid,
            'enrolments[0][userid]': enrollment.userid,
            'enrolments[0][courseid]': enrollment.courseid,
            'enrolments[0][suspend]': enrollment.suspend,
        }
        
        if enrollment.timestart:
            enroll_data['enrolments[0][timestart]'] = enrollment.timestart
        if enrollment.timeend:
            enroll_data['enrolments[0][timeend]'] = enrollment.timeend
            
        result = self._make_request('enrol_manual_enrol_users', enroll_data)
        return result is not None
    
    def get_course_completions(self, courseid: int) -> List[Dict[str, Any]]:
        """Get course completion data"""
        params = {'courseid': courseid}
        return self._make_request('core_completion_get_course_completion_status', params)
    
    def get_user_grades(self, courseid: int, userid: int) -> Dict[str, Any]:
        """Get user grades for course"""
        params = {
            'courseid': courseid,
            'userid': userid
        }
        return self._make_request('core_grades_get_grades', params)
    
    def create_competency_framework(self, shortname: str, description: str, 
                                  scaleid: int = 1) -> Dict[str, Any]:
        """Create competency framework"""
        framework_data = {
            'shortname': shortname,
            'description': description,
            'scaleid': scaleid,
            'visible': 1
        }
        
        return self._make_request('core_competency_create_competency_framework', framework_data)
    
    def create_competency(self, competency: BCMCompetency, frameworkid: int) -> Dict[str, Any]:
        """Create competency in framework"""
        comp_data = {
            'shortname': competency.shortname,
            'idnumber': competency.idnumber,
            'description': competency.description,
            'competencyframeworkid': frameworkid,
            'ruletype': competency.ruletype,
            'ruleoutcome': competency.ruleoutcome
        }
        
        if competency.parent:
            # Would need to resolve parent competency ID
            pass
            
        return self._make_request('core_competency_create_competency', comp_data)


class BCMMoodleIntegration:
    """BCM Platform integration with Moodle LMS"""
    
    def __init__(self, moodle_client: MoodleClient, bcm_webhook_url: Optional[str] = None):
        self.client = moodle_client
        self.bcm_webhook_url = bcm_webhook_url
        
        # BCM specific role mappings
        self.bcm_roles = {
            'bcm_student': 5,      # Student role
            'bcm_trainer': 3,      # Teacher role  
            'bcm_manager': 3,      # Teacher role
            'bcm_auditor': 2,      # Manager role
        }
        
        # BCM competency categories
        self.bcm_competencies = [
            "BCM Policy and Strategy",
            "Risk Assessment and BIA", 
            "Business Continuity Planning",
            "Incident Response Management",
            "Crisis Communications",
            "Exercise and Testing",
            "Program Management",
            "Regulatory Compliance"
        ]
    
    def create_bcm_user(self, bcm_user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create BCM user in Moodle"""
        # Map BCM user data to Moodle user
        moodle_user = MoodleUser(
            username=bcm_user_data.get('login', ''),
            password=bcm_user_data.get('password', ''),
            firstname=bcm_user_data.get('first_name', ''),
            lastname=bcm_user_data.get('last_name', ''),
            email=bcm_user_data.get('email', ''),
            description=f"BCM User - Company: {bcm_user_data.get('company_id', '')}",
            city=bcm_user_data.get('city', ''),
            country=bcm_user_data.get('country_code', 'UA')
        )
        
        return self.client.create_user(moodle_user)
    
    def create_bcm_training_course(self, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create BCM training course"""
        course = MoodleCourse(
            id=0,
            fullname=training_data.get('name', ''),
            shortname=f"BCM-{training_data.get('code', '')}",
            categoryid=training_data.get('category_id', 1),
            summary=training_data.get('description', ''),
            startdate=training_data.get('start_date'),
            enddate=training_data.get('end_date'),
            numsections=training_data.get('sections', 4)
        )
        
        return self.client.create_course(course)
    
    def enroll_bcm_user(self, user_id: int, course_id: int, role: str = 'bcm_student') -> bool:
        """Enroll BCM user in training course"""
        role_id = self.bcm_roles.get(role, 5)  # Default to student
        
        enrollment = MoodleEnrollment(
            roleid=role_id,
            userid=user_id,
            courseid=course_id
        )
        
        return self.client.enroll_user(enrollment)
    
    def sync_bcm_competencies(self) -> Dict[str, Any]:
        """Create BCM competency framework in Moodle"""
        results = {}
        
        # Create BCM competency framework
        framework = self.client.create_competency_framework(
            shortname="BCM_FRAMEWORK",
            description="Business Continuity Management Competency Framework based on ISO 22301"
        )
        
        framework_id = framework.get('id')
        results['framework'] = framework
        results['competencies'] = []
        
        if framework_id:
            # Create individual competencies
            for i, comp_name in enumerate(self.bcm_competencies):
                competency = BCMCompetency(
                    shortname=f"BCM_{i+1}",
                    idnumber=f"BCM-COMP-{i+1:03d}",
                    description=f"{comp_name} - Critical competency for BCM professionals"
                )
                
                comp_result = self.client.create_competency(competency, framework_id)
                results['competencies'].append(comp_result)
        
        return results
    
    def get_bcm_training_progress(self, company_id: str) -> Dict[str, Any]:
        """Get training progress for BCM company users"""
        # This would require additional API calls to get users by company
        # and then their course completions
        progress_data = {
            'company_id': company_id,
            'total_users': 0,
            'completed_trainings': 0,
            'in_progress_trainings': 0,
            'competency_achievements': 0,
            'training_hours': 0
        }
        
        return progress_data
    
    def sync_training_completion_to_bcm(self, course_id: int, user_id: int) -> bool:
        """Sync training completion back to BCM Platform"""
        if not self.bcm_webhook_url:
            return False
            
        try:
            completion_data = self.client.get_course_completions(course_id)
            grades_data = self.client.get_user_grades(course_id, user_id)
            
            # Prepare webhook payload
            webhook_data = {
                'event_type': 'training_completed',
                'user_id': user_id,
                'course_id': course_id,
                'completion_data': completion_data,
                'grades_data': grades_data,
                'timestamp': json.dumps({"$date": {"$numberLong": str(int(time.time() * 1000))}})
            }
            
            # Send to BCM Platform
            response = requests.post(
                self.bcm_webhook_url,
                json=webhook_data,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Failed to sync completion to BCM: {e}")
            return False
