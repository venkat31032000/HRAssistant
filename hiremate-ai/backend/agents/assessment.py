# backend/agents/assessment.py
from langchain_openai import ChatOpenAI
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class AssessmentAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        
        # In production, these would come from HackerRank API
        self.assessment_templates = {
            "python_basic": "https://www.hackerrank.com/test/python-basic",
            "python_intermediate": "https://www.hackerrank.com/test/python-intermediate", 
            "sql_basic": "https://www.hackerrank.com/test/sql-basic",
            "data_science": "https://www.hackerrank.com/test/data-science-test",
            "algorithms": "https://www.hackerrank.com/test/algorithms-test"
        }
    
    def generate_assessment_link(self, candidate_info: Dict, job_requirements: Dict) -> Dict:
        """Generate assessment link based on job requirements"""
        
        # Generate unique assessment ID
        assessment_id = str(uuid.uuid4())
        
        # Determine which test to use based on job requirements
        test_type = self._select_test_type(job_requirements)
        
        # In production, you'd use HackerRank API to create a unique test link
        # For demo, we'll simulate it
        base_url = self.assessment_templates.get(test_type, self.assessment_templates["python_basic"])
        unique_link = f"{base_url}?candidate={assessment_id}"
        
        # Calculate deadline (7 days from now)
        deadline = datetime.now() + timedelta(days=7)
        
        return {
            "assessment_id": assessment_id,
            "candidate_name": candidate_info['name'],
            "candidate_email": candidate_info['email'],
            "test_type": test_type,
            "link": unique_link,
            "created_at": datetime.now().isoformat(),
            "deadline": deadline.isoformat(),
            "duration": "90 minutes",
            "status": "sent",
            "topics": self._get_test_topics(test_type)
        }
    
    def _select_test_type(self, job_requirements: Dict) -> str:
        """Select appropriate test based on job requirements"""
        
        prompt = f"""
Based on these job requirements, select the most appropriate assessment type:

Job Title: {job_requirements.get('title', 'Software Engineer')}
Required Skills: {job_requirements.get('skills', [])}
Experience Level: {job_requirements.get('experience', 'Mid-level')}

Available test types:
- python_basic: Basic Python programming
- python_intermediate: Advanced Python, OOP, libraries
- sql_basic: SQL queries and database concepts
- data_science: ML, statistics, data analysis
- algorithms: Data structures and algorithms

Return only the test type name.
"""
        
        response = self.llm.invoke(prompt)
        test_type = response.content.strip().lower()
        
        # Validate response
        if test_type not in self.assessment_templates:
            test_type = "python_basic"  # Default
            
        return test_type
    
    def _get_test_topics(self, test_type: str) -> List[str]:
        """Get topics covered in the test"""
        topics_map = {
            "python_basic": ["Variables & Data Types", "Control Flow", "Functions", "Lists & Dictionaries"],
            "python_intermediate": ["OOP", "Decorators", "Generators", "Error Handling", "File I/O"],
            "sql_basic": ["SELECT Queries", "JOINs", "GROUP BY", "Aggregate Functions"],
            "data_science": ["NumPy", "Pandas", "Statistics", "Machine Learning Basics"],
            "algorithms": ["Arrays", "Sorting", "Trees", "Dynamic Programming", "Time Complexity"]
        }
        
        return topics_map.get(test_type, ["Programming Fundamentals"])
    
    def generate_assessment_email(self, assessment_data: Dict, company_name: str = "HireMate") -> Dict:
        """Generate email content for assessment invitation"""
        
        prompt = f"""
Create a professional and encouraging email for a coding assessment invitation.

Candidate: {assessment_data['candidate_name']}
Test Type: {assessment_data['test_type'].replace('_', ' ').title()}
Duration: {assessment_data['duration']}
Deadline: {assessment_data['deadline'][:10]}
Topics: {', '.join(assessment_data['topics'])}

The email should:
1. Congratulate them on passing initial screening
2. Explain the assessment clearly
3. Provide the link and deadline
4. Include preparation tips
5. Be encouraging and professional

Format the email with clear sections.
"""
        
        response = self.llm.invoke(prompt)
        email_content = response.content
        
        # Add the actual link
        email_content = email_content.replace("[ASSESSMENT_LINK]", assessment_data['link'])
        
        return {
            "subject": f"Next Step: Technical Assessment - {company_name}",
            "body": email_content,
            "html_body": self._convert_to_html(email_content, assessment_data)
        }
    
    def _convert_to_html(self, text_content: str, assessment_data: Dict) -> str:
        """Convert email to HTML format"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ padding: 30px; background-color: #f9f9f9; }}
        .assessment-box {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin: 20px 0; }}
        .button {{ display: inline-block; padding: 12px 30px; background-color: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .button:hover {{ background-color: #764ba2; }}
        .topics {{ background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 15px 0; }}
        .deadline {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #ffc107; }}
        .tips {{ background: #d4edda; padding: 15px; border-radius: 5px; margin: 15px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Technical Assessment Invitation</h1>
            <p>Congratulations on advancing to the next stage!</p>
        </div>
        
        <div class="content">
            <p>Dear {assessment_data['candidate_name']},</p>
            
            <p>Great news! You've successfully passed our initial screening, and we're excited to invite you to complete a technical assessment as the next step in our hiring process.</p>
            
            <div class="assessment-box">
                <h2>📝 Assessment Details</h2>
                <ul>
                    <li><strong>Type:</strong> {assessment_data['test_type'].replace('_', ' ').title()}</li>
                    <li><strong>Duration:</strong> {assessment_data['duration']}</li>
                    <li><strong>Language:</strong> Python/SQL (as applicable)</li>
                </ul>
                
                <center>
                    <a href="{assessment_data['link']}" class="button">Start Assessment</a>
                </center>
            </div>
            
            <div class="deadline">
                <strong>⏰ Deadline:</strong> Please complete by {assessment_data['deadline'][:10]}
            </div>
            
            <div class="topics">
                <h3>Topics Covered:</h3>
                <ul>
                    {"".join([f"<li>{topic}</li>" for topic in assessment_data['topics']])}
                </ul>
            </div>
            
            <div class="tips">
                <h3>💡 Tips for Success:</h3>
                <ul>
                    <li>Find a quiet environment with stable internet</li>
                    <li>Have your favorite IDE or text editor ready</li>
                    <li>Read each question carefully before coding</li>
                    <li>Test your code with the provided test cases</li>
                    <li>Focus on correctness first, then optimize</li>
                </ul>
            </div>
            
            <p><strong>Important Notes:</strong></p>
            <ul>
                <li>You can use online resources and documentation</li>
                <li>The assessment must be completed in one sitting</li>
                <li>Your code will be evaluated for correctness, efficiency, and style</li>
            </ul>
            
            <p>If you have any technical difficulties or questions, please don't hesitate to reach out.</p>
            
            <p>We're looking forward to seeing your problem-solving skills in action!</p>
            
            <p>Best of luck!<br>
            The HireMate Team</p>
        </div>
        
        <div class="footer">
            <p>This assessment is powered by HackerRank</p>
            <p style="font-size: 12px; color: #999;">
                If you're unable to click the button, copy this link: {assessment_data['link']}
            </p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def check_completion_status(self, assessment_id: str) -> Dict:
        """Check if candidate has completed the assessment"""
        # In production, this would call HackerRank API
        # For demo, we'll simulate different statuses
        
        import random
        statuses = ["completed", "in_progress", "not_started"]
        status = random.choice(statuses)
        
        result = {
            "assessment_id": assessment_id,
            "status": status,
            "checked_at": datetime.now().isoformat()
        }
        
        if status == "completed":
            result.update({
                "score": random.randint(60, 100),
                "completed_at": datetime.now().isoformat(),
                "time_taken": f"{random.randint(45, 90)} minutes",
                "passed": result.get("score", 0) >= 70
            })
            
        return result
    
    def generate_reminder_email(self, assessment_data: Dict) -> Dict:
        """Generate reminder email for pending assessments"""
        days_left = (datetime.fromisoformat(assessment_data['deadline']) - datetime.now()).days
        
        return {
            "subject": f"Reminder: {days_left} days left for your technical assessment",
            "body": f"""
Hi {assessment_data['candidate_name']},

This is a friendly reminder that you have {days_left} days remaining to complete your technical assessment.

Assessment Link: {assessment_data['link']}
Deadline: {assessment_data['deadline'][:10]}

If you've already completed it, please ignore this email.

If you need more time or have any questions, please let us know.

Best regards,
The HireMate Team
"""
        }


# backend/api/assessment.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from datetime import datetime

router = APIRouter()

# Import the assessment agent
import sys
sys.path.append('..')
from agents.assessment import AssessmentAgent
from scripts.process_resumes_with_email import EmailSender

assessment_agent = AssessmentAgent()
email_sender = EmailSender()

class AssessmentRequest(BaseModel):
    candidate_name: str
    candidate_email: str
    job_title: str
    required_skills: List[str]
    experience_level: str = "Mid-level"

class AssessmentStatusCheck(BaseModel):
    assessment_id: str

@router.post("/assessment/send")
async def send_assessment(req: AssessmentRequest, background_tasks: BackgroundTasks):
    """Send assessment to a candidate"""
    
    # Prepare candidate and job info
    candidate_info = {
        "name": req.candidate_name,
        "email": req.candidate_email
    }
    
    job_requirements = {
        "title": req.job_title,
        "skills": req.required_skills,
        "experience": req.experience_level
    }
    
    # Generate assessment link
    assessment_data = assessment_agent.generate_assessment_link(candidate_info, job_requirements)
    
    # Generate email content
    email_data = assessment_agent.generate_assessment_email(assessment_data)
    
    # Send email in background
    background_tasks.add_task(
        email_sender.send_email,
        req.candidate_email,
        email_data["subject"],
        email_data["body"],
        email_data["html_body"]
    )
    
    # Save assessment data
    save_assessment_data(assessment_data)
    
    return {
        "success": True,
        "assessment_id": assessment_data["assessment_id"],
        "message": f"Assessment sent to {req.candidate_email}",
        "details": {
            "test_type": assessment_data["test_type"],
            "deadline": assessment_data["deadline"],
            "link": assessment_data["link"]
        }
    }

@router.post("/assessment/check-status")
async def check_assessment_status(req: AssessmentStatusCheck):
    """Check the status of an assessment"""
    
    # Check completion status
    status = assessment_agent.check_completion_status(req.assessment_id)
    
    # Update stored data if completed
    if status["status"] == "completed":
        update_assessment_status(req.assessment_id, status)
    
    return status

@router.get("/assessment/pending")
async def get_pending_assessments():
    """Get all pending assessments"""
    
    assessments = load_all_assessments()
    pending = [a for a in assessments if a.get("status") != "completed"]
    
    return {
        "count": len(pending),
        "assessments": pending
    }

def save_assessment_data(assessment_data: dict):
    """Save assessment data to file"""
    
    assessments_dir = "../../data/assessments"
    os.makedirs(assessments_dir, exist_ok=True)
    
    filepath = os.path.join(assessments_dir, f"{assessment_data['assessment_id']}.json")
    with open(filepath, 'w') as f:
        json.dump(assessment_data, f, indent=2)

def update_assessment_status(assessment_id: str, status_data: dict):
    """Update assessment status"""
    
    filepath = f"../../data/assessments/{assessment_id}.json"
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        data.update(status_data)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

def load_all_assessments():
    """Load all assessments"""
    
    assessments_dir = "../../data/assessments"
    if not os.path.exists(assessments_dir):
        return []
    
    assessments = []
    for filename in os.listdir(assessments_dir):
        if filename.endswith('.json'):
            with open(os.path.join(assessments_dir, filename), 'r') as f:
                assessments.append(json.load(f))
    
    return assessments