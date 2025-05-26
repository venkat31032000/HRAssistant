# backend/scripts/process_resumes_with_email.py
import os
import sys
import json
import smtplib
import random
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path to import agents
sys.path.append('..')
from agents.resume import ResumeAgent
from agents.Interview import InterviewPlannerAgent
from agents.assessment import AssessmentAgent


class EmailSender:
    def __init__(self):
        self.email_address = os.getenv('EMAIL_ADDRESS')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.smtp_host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('EMAIL_PORT', '587'))
        
        if not self.email_address or not self.email_password:
            print("⚠️  Email credentials not found in .env file!")
            self.enabled = False
        else:
            self.enabled = True
            print(f"✅ Email configured: {self.email_address}")
    
    def send_email(self, to_email: str, subject: str, body_text: str, body_html: str = None):
        """Send email using Gmail SMTP"""
        if not self.enabled:
            print(f"📧 [TEST MODE] Would send email to: {to_email}")
            print(f"   Subject: {subject}")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_address
            msg['To'] = to_email
            msg['Subject'] = subject
            
            part1 = MIMEText(body_text, 'plain')
            msg.attach(part1)
            
            if body_html:
                part2 = MIMEText(body_html, 'html')
                msg.attach(part2)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully to: {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email to {to_email}: {str(e)}")
            return False

# ===== EMAIL TEMPLATES =====

def create_selection_email_with_assessment_notice(candidate_name: str, score: int, job_title: str = "Data Scientist"):
    """Create selection email that mentions assessment will follow"""
    
    text = f"""Dear {candidate_name},

Congratulations! We are pleased to inform you that your application for the {job_title} position has been reviewed, and we would like to move forward with your candidacy.

Your profile scored {score}/100 in our initial screening, demonstrating strong alignment with our requirements.

Next Steps:
1. Technical Assessment: You will receive a separate email with your coding assessment link shortly
2. Interview Process: Upon successful completion of the assessment, we will schedule interviews

We're excited about the possibility of you joining our team!

Best regards,
HireMate Talent Acquisition Team
"""
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 5px;">
                <h1>Congratulations, {candidate_name}!</h1>
            </div>
            
            <div style="padding: 20px; background-color: #f9f9f9; margin-top: 20px; border-radius: 5px;">
                <p>We are pleased to inform you that your application for the <strong>{job_title}</strong> position has been reviewed, and we would like to move forward with your candidacy.</p>
                
                <p>Your profile scored <strong>{score}/100</strong> in our initial screening, demonstrating strong alignment with our requirements.</p>
                
                <h2 style="color: #4CAF50;">Next Steps:</h2>
                <ol>
                    <li><strong>Technical Assessment</strong>: You will receive a separate email with your coding assessment link shortly</li>
                    <li><strong>Interview Process</strong>: Upon successful completion of the assessment, we will schedule interviews</li>
                </ol>
                
                <p>We're excited about the possibility of you joining our team!</p>
            </div>
            
            <div style="text-align: center; padding: 20px; color: #666;">
                <p>Best regards,<br><strong>HireMate Talent Acquisition Team</strong></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return text, html

def create_rejection_email(candidate_name: str, score: int, reason: str, job_title: str = "Data Scientist"):
    """Create rejection email content"""
    
    text = f"""Dear {candidate_name},

Thank you for your interest in the {job_title} position at HireMate.

After careful review of your application, we have decided to move forward with other candidates whose qualifications more closely match our current requirements.

Feedback:
- ATS Score: {score}/100
- {reason}

Suggestions for improvement:
- Ensure your resume includes specific keywords from the job description
- Highlight relevant technical skills (Python, SQL, Machine Learning, TensorFlow)
- Quantify your achievements with metrics and impact
- Include relevant data science projects

We encourage you to apply for future positions that match your skills and experience.

Best regards,
HireMate Talent Acquisition Team
"""
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f44336; color: white; padding: 20px; text-align: center; border-radius: 5px;">
                <h1>Application Update</h1>
            </div>
            
            <div style="padding: 20px; background-color: #f9f9f9; margin-top: 20px; border-radius: 5px;">
                <p>Dear {candidate_name},</p>
                
                <p>Thank you for your interest in the <strong>{job_title}</strong> position at HireMate.</p>
                
                <p>After careful review of your application, we have decided to move forward with other candidates whose qualifications more closely match our current requirements.</p>
                
                <div style="background-color: #fff; padding: 15px; margin: 15px 0; border-left: 4px solid #ff9800;">
                    <h3>Feedback:</h3>
                    <ul>
                        <li>ATS Score: {score}/100</li>
                        <li>{reason}</li>
                    </ul>
                </div>
                
                <div style="background-color: #e3f2fd; padding: 15px; margin: 15px 0; border-radius: 5px;">
                    <h3>Suggestions for improvement:</h3>
                    <ul>
                        <li>Ensure your resume includes specific keywords from the job description</li>
                        <li>Highlight relevant technical skills</li>
                        <li>Quantify your achievements with metrics</li>
                        <li>Include relevant projects</li>
                    </ul>
                </div>
            </div>
            
            <div style="text-align: center; padding: 20px; color: #666;">
                <p>Best regards,<br><strong>HireMate Talent Acquisition Team</strong></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return text, html

# ===== ASSESSMENT FUNCTIONS =====

def generate_realistic_assessment_score(candidate_ats_score):
    """Generate realistic assessment score based on ATS score"""
    if candidate_ats_score >= 85:
        base_range = (75, 95)
    elif candidate_ats_score >= 75:
        base_range = (65, 85)
    elif candidate_ats_score >= 65:
        base_range = (55, 75)
    else:
        base_range = (50, 70)
    
    score = random.randint(base_range[0], base_range[1])
    variation = random.randint(-5, 5)
    final_score = max(0, min(100, score + variation))
    
    return final_score

# ===== INTERVIEW SCHEDULING FUNCTIONS =====

def generate_interview_slots(num_days=10):
    """Generate available interview slots"""
    slots = []
    current_date = datetime.now()
    daily_slots = ["9:00 AM", "10:30 AM", "2:00 PM", "3:30 PM"]
    
    days_added = 0
    date = current_date
    
    while days_added < num_days:
        date += timedelta(days=1)
        if date.weekday() >= 5:  # Skip weekends
            continue
            
        for time_slot in daily_slots:
            slots.append({
                "date": date.strftime("%A, %B %d, %Y"),
                "time": time_slot,
                "datetime": date.strftime("%Y-%m-%d") + " " + time_slot,
                "available": True,
                "slot_id": f"slot_{days_added}_{time_slot.replace(':', '').replace(' ', '')}"
            })
        days_added += 1
    
    return slots

def send_interview_invitation_with_slots(candidate, round_number, round_name, email_sender):
    """Send interview invitation with time slots"""
    available_slots = generate_interview_slots()
    offered_slots = random.sample(available_slots, 6)
    
    slots_html = ""
    for i, slot in enumerate(offered_slots, 1):
        slots_html += f"""
        <div style="margin: 10px 0; padding: 15px; background: #f0f0f0; border-radius: 5px;">
            <strong>Option {i}:</strong> {slot['date']} at {slot['time']}<br>
            <small style="color: #666;">Reply with "SLOT {i}" to select this time</small>
        </div>
        """
    
    subject = f"Interview Round {round_number}: {round_name} - Schedule Your Interview"
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1>Interview Scheduling</h1>
                <p>Round {round_number}: {round_name}</p>
            </div>
            
            <div style="padding: 30px; background-color: #f9f9f9;">
                <p>Dear {candidate['name']},</p>
                
                <p>Congratulations on advancing to <strong>Round {round_number}: {round_name}</strong>!</p>
                
                <div style="background: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h3>📅 Available Time Slots</h3>
                    <p>Please select one of the following times:</p>
                    {slots_html}
                </div>
                
                <div style="background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h4>How to confirm:</h4>
                    <p>Simply reply to this email with your preferred slot number (e.g., "SLOT 1")</p>
                </div>
                
                <p>Looking forward to meeting you!</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text = f"""Dear {candidate['name']},

Congratulations on advancing to Round {round_number}: {round_name}!

Please select one of the following interview slots:
"""
    for i, slot in enumerate(offered_slots, 1):
        text += f"Option {i}: {slot['date']} at {slot['time']}\n"
    
    text += "\nReply with your preferred slot number (e.g., 'SLOT 1')"
    
    email_sender.send_email(candidate['email'], subject, text, html)
    return offered_slots

def send_interview_confirmation(candidate, slot, round_name, email_sender):
    """Send interview confirmation"""
    meeting_link = f"https://meet.hiremate.ai/interview/{random.randint(1000, 9999)}"
    
    subject = f"Interview Confirmed - {round_name}"
    
    text = f"""Dear {candidate['name']},

Your interview has been confirmed!

Interview Details:
- Date: {slot['date']}
- Time: {slot['time']}
- Round: {round_name}
- Meeting Link: {meeting_link}

Best regards,
HireMate Talent Acquisition Team"""
    
    email_sender.send_email(candidate['email'], subject, text)

# ===== MULTI-STEP INTERVIEW FUNCTIONS =====

def get_interview_rounds(experience_years):
    """Get interview rounds based on experience"""
    if experience_years >= 7:  # Senior
        return [
            {"name": "Technical Screen", "type": "technical", "pass_rate": 0.75},
            {"name": "Coding Interview", "type": "coding", "pass_rate": 0.70},
            {"name": "System Design", "type": "design", "pass_rate": 0.65},
            {"name": "Leadership & Behavioral", "type": "behavioral", "pass_rate": 0.85},
            {"name": "Final HR", "type": "hr", "pass_rate": 0.95}
        ]
    elif experience_years >= 3:  # Mid
        return [
            {"name": "Technical Screen", "type": "technical", "pass_rate": 0.75},
            {"name": "Coding Interview", "type": "coding", "pass_rate": 0.70},
            {"name": "System Design", "type": "design", "pass_rate": 0.60},
            {"name": "HR & Cultural Fit", "type": "hr", "pass_rate": 0.90}
        ]
    else:  # Entry
        return [
            {"name": "Technical Screen", "type": "technical", "pass_rate": 0.70},
            {"name": "Coding Interview", "type": "coding", "pass_rate": 0.65},
            {"name": "HR Discussion", "type": "hr", "pass_rate": 0.90}
        ]

def send_interview_rejection_email(candidate, round_name, score, email_sender):
    """Send rejection after failed interview"""
    subject = "Interview Update - HireMate"
    
    text = f"""Dear {candidate['name']},

Thank you for participating in the {round_name} interview round.

After careful consideration, we have decided not to move forward with your application at this time.

Your interview performance score: {score}/100

We appreciate the time you invested in our interview process.

Best regards,
HireMate Talent Acquisition Team"""
    
    email_sender.send_email(candidate['email'], subject, text)

def send_final_selection_email(candidate, email_sender):
    """Send final selection email"""
    subject = "Congratulations! Job Offer Discussion - HireMate"
    
    text = f"""Dear {candidate['name']},

Congratulations! You have successfully completed all interview rounds for the Data Scientist position.

We are impressed with your performance throughout the process and would like to extend a job offer.

Next steps:
- HR will contact you within 24 hours to discuss compensation and benefits
- Background verification process will be initiated
- Tentative start date discussion

We look forward to welcoming you to the team!

Best regards,
HireMate Talent Acquisition Team"""
    
    email_sender.send_email(candidate['email'], subject, text)

# ===== MAIN WORKFLOW =====

def process_resumes_with_complete_workflow():
    """Process resumes with complete HR workflow including assessments and multi-step interviews"""
    
    # Initialize all agents
    resume_agent = ResumeAgent()
    assessment_agent = AssessmentAgent()
    
    email_sender = EmailSender()
    
    # Define job requirements
    job_requirements = {
        "title": "Data Scientist",
        "skills": ["Python", "SQL", "Machine Learning", "TensorFlow", "Statistics"],
        "experience": "4+ years"
    }
    
    # Ask for confirmation
    if email_sender.enabled:
        print("\n⚠️  COMPLETE HR WORKFLOW ENABLED!")
        print("This will:")
        print("1. Process 30 resumes")
        print("2. Send selection/rejection emails")
        print("3. Send assessments to selected candidates")
        print("4. Score assessments (75% pass rate)")
        print("5. Conduct multi-step interviews with scheduling")
        print("6. Send final offers")
        confirm = input("\nDo you want to continue? (yes/no): ").lower()
        if confirm != 'yes':
            print("Aborted.")
            return
    
    # Paths
    pending_dir = "../../data/resumes/pending"
    selected_dir = "../../data/resumes/selected"
    rejected_dir = "../../data/resumes/rejected"
    assessments_dir = "../../data/assessments"
    interviews_dir = "../../data/interviews"
    
    # Create directories
    for dir_path in [selected_dir, rejected_dir, assessments_dir, interviews_dir]:
        os.makedirs(dir_path, exist_ok=True)
    
    # Load job description
    with open("../../automation/latest_jd.txt", "r") as f:
        job_description = f.read()
    
    print("\n🚀 Starting Complete HR Workflow...")
    print("=" * 50)
    
    # Get all resumes
    resumes = [f for f in os.listdir(pending_dir) if f.endswith('.txt') and not f.endswith('_metadata.json')]
    
    if not resumes:
        print("❌ No resumes found in pending folder!")
        return
    
    print(f"📁 Found {len(resumes)} resumes to process\n")
    
    results = []
    selected_candidates = []
    
    # ===== PHASE 1: Resume Processing =====
    print("\nPHASE 1: Resume Screening")
    print("-" * 30)
    
    for resume_file in resumes:
        print(f"\n📋 Processing: {resume_file}")
        
        # Read resume and metadata
        resume_path = os.path.join(pending_dir, resume_file)
        with open(resume_path, 'r', encoding='utf-8') as f:
            resume_text = f.read()
        
        # Get metadata
        metadata_file = resume_file.replace('.txt', '_metadata.json')
        metadata_path = os.path.join(pending_dir, metadata_file)
        
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        else:
            metadata = {
                "name": resume_file.replace('.txt', '').replace('_', ' ').title(),
                "email": "venkat.posanipalle3103@gmail.com",
                "experience_years": 3
            }
        
        print(f"👤 Candidate: {metadata['name']}")
        print(f"📧 Email: {metadata['email']}")
        
        # Score the resume
        try:
            result = resume_agent.score_resume(
                resume_text=resume_text,
                job_description=job_description,
                referred=False
            )
            
            print(f"📊 Score: {result['score']}/100")
            print(f"📋 Decision: {result['decision']}")
            print(f"💭 Reason: {result['reason']}")
            
            # Send appropriate email
            if result['decision'] == 'shortlist':
                print("✅ SELECTED - Sending selection email...")
                subject = "Congratulations! Next Steps for Your Application - HireMate"
                text, html = create_selection_email_with_assessment_notice(
                    metadata['name'], 
                    result['score']
                )
                email_sender.send_email(metadata['email'], subject, text, html)
                
                # Add to selected candidates
                selected_candidates.append({
                    "name": metadata['name'],
                    "email": metadata['email'],
                    "score": result['score'],
                    "experience_years": metadata.get('experience_years', 3),
                    "file": resume_file
                })
                
                # Move to selected folder
                destination = os.path.join(selected_dir, resume_file)
            else:
                print("❌ REJECTED - Sending rejection email...")
                subject = "Update on Your Application - HireMate"
                text, html = create_rejection_email(
                    metadata['name'], 
                    result['score'], 
                    result['reason']
                )
                email_sender.send_email(metadata['email'], subject, text, html)
                
                # Move to rejected folder
                destination = os.path.join(rejected_dir, resume_file)
            
            # Move files
            os.rename(resume_path, destination)
            if os.path.exists(metadata_path):
                os.rename(metadata_path, os.path.join(os.path.dirname(destination), metadata_file))
            
            # Store result
            results.append({
                "file": resume_file,
                "name": metadata['name'],
                "email": metadata['email'],
                "score": result['score'],
                "decision": result['decision'],
                "reason": result['reason'],
                "processed_at": datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"❌ Error processing {resume_file}: {str(e)}")
    
    # ===== PHASE 2: Send Assessments =====
    if selected_candidates:
        print("\n\nPHASE 2: Sending Assessments")
        print("-" * 30)
        print(f"📝 Sending assessments to {len(selected_candidates)} selected candidates\n")
        
        for candidate in selected_candidates:
            print(f"\n🎯 Sending assessment to: {candidate['name']}")
            
            try:
                candidate_info = {
                    "name": candidate['name'],
                    "email": candidate['email']
                }
                
                assessment_data = assessment_agent.generate_assessment_link(
                    candidate_info, 
                    job_requirements
                )
                
                print(f"📝 Test Type: {assessment_data['test_type']}")
                print(f"🔗 Link: {assessment_data['link']}")
                
                email_data = assessment_agent.generate_assessment_email(assessment_data)
                
                if email_sender.send_email(
                    candidate['email'],
                    email_data['subject'],
                    email_data['body'],
                    email_data['html_body']
                ):
                    print("✅ Assessment sent successfully!")
                    
                    assessment_file = os.path.join(assessments_dir, f"{assessment_data['assessment_id']}.json")
                    with open(assessment_file, 'w') as f:
                        json.dump(assessment_data, f, indent=2)
                
            except Exception as e:
                print(f"❌ Error sending assessment: {str(e)}")
    
    # ===== PHASE 2.5: Process Assessment Results =====
    if selected_candidates:
        print("\n\nPHASE 2.5: Processing Assessment Results")
        print("-" * 30)
        print("⏳ Simulating assessment completion...")
        time.sleep(2)
        
        candidates_who_passed = []
        
        for candidate in selected_candidates:
            assessment_score = generate_realistic_assessment_score(candidate['score'])
            
            print(f"\n📝 {candidate['name']} - Assessment Results:")
            print(f"   Score: {assessment_score}/100")
            
            if assessment_score >= 70:
                print(f"   ✅ PASSED - Proceeding to interviews")
                candidate['assessment_score'] = assessment_score
                candidates_who_passed.append(candidate)
            else:
                print(f"   ❌ FAILED - Sending rejection email")
                
                subject = "Assessment Results - HireMate"
                text = f"""Dear {candidate['name']},

Thank you for completing the technical assessment.

Your assessment score: {assessment_score}/100
Required score: 70/100

Unfortunately, this did not meet our minimum threshold. We encourage you to continue building your technical skills.

Best regards,
HireMate Talent Acquisition Team"""
                
                email_sender.send_email(candidate['email'], subject, text)
        
        print(f"\n📊 Assessment Results Summary:")
        print(f"   Total Assessed: {len(selected_candidates)}")
        print(f"   Passed: {len(candidates_who_passed)} ({len(candidates_who_passed)/len(selected_candidates)*100:.0f}%)")
        print(f"   Failed: {len(selected_candidates) - len(candidates_who_passed)}")
    
    # ===== PHASE 3: Multi-Step Interviews =====
    if candidates_who_passed:
        print("\n\nPHASE 3: Multi-Step Interview Process")
        print("=" * 50)
        
        candidates_in_process = candidates_who_passed.copy()
        final_selected = []
        interview_results = []
        
        # Process each round
        max_rounds = 5  # Maximum possible rounds
        
        for round_num in range(max_rounds):
            if not candidates_in_process:
                break
                
            print(f"\n📍 INTERVIEW ROUND {round_num + 1}")
            print("-" * 30)
            
            candidates_for_next_round = []
            
            for candidate in candidates_in_process:
                exp_years = candidate.get('experience_years', 3)
                rounds = get_interview_rounds(exp_years)
                
                if round_num >= len(rounds):
                    final_selected.append(candidate)
                    continue
                
                current_round = rounds[round_num]
                
                # Send interview invitation with slots
                print(f"\n👤 {candidate['name']}")
                print(f"   Sending invitation for: {current_round['name']}")
                
                offered_slots = send_interview_invitation_with_slots(
                    candidate,
                    round_num + 1,
                    current_round['name'],
                    email_sender
                )
                
                # Simulate slot selection
                selected_slot = random.choice(offered_slots[:3])  # Usually pick early slots
                print(f"   📅 Selected slot: {selected_slot['date']} at {selected_slot['time']}")
                
                # Send confirmation
                send_interview_confirmation(candidate, selected_slot, current_round['name'], email_sender)
                
                # Simulate interview performance
                base_score = candidate.get('assessment_score', 75)
                performance_modifier = random.uniform(0.8, 1.2)
                interview_score = min(100, int(base_score * performance_modifier))
                
                threshold = int(100 * (1 - current_round['pass_rate']))
                passed = interview_score >= threshold
                
                print(f"   Performance: {interview_score}/100")
                print(f"   Result: {'✅ PASSED' if passed else '❌ FAILED'}")
                
                interview_results.append({
                    "candidate": candidate['name'],
                    "round": round_num + 1,
                    "round_name": current_round['name'],
                    "score": interview_score,
                    "passed": passed
                })
                
                if passed:
                    candidates_for_next_round.append(candidate)
                else:
                    send_interview_rejection_email(
                        candidate,
                        current_round['name'],
                        interview_score,
                        email_sender
                    )
            
            candidates_in_process = candidates_for_next_round
            
            print(f"\n📊 Round {round_num + 1} Summary:")
            print(f"   Candidates interviewed: {len([r for r in interview_results if r['round'] == round_num + 1])}")
            print(f"   Passed: {len(candidates_for_next_round)}")
        
        # Send final selection emails
        for candidate in final_selected:
            send_final_selection_email(candidate, email_sender)
        
        print("\n" + "="*50)
        print("📊 FINAL RESULTS")
        print("="*50)
        print(f"Total Resumes: {len(results)}")
        print(f"Selected for Assessment: {len(selected_candidates)}")
        print(f"Passed Assessment: {len(candidates_who_passed)}")
        print(f"Final Offers: {len(final_selected)}")
        print(f"\nConversion Rate: {len(final_selected)/len(results)*100:.1f}%")
    
    # Save complete results
    complete_results = {
        "processing_date": datetime.now().isoformat(),
        "resume_results": results,
        "assessments_sent": len(selected_candidates),
        "assessment_pass": len(candidates_who_passed) if 'candidates_who_passed' in locals() else 0,
        "final_selections": len(final_selected) if 'final_selected' in locals() else 0,
        "interview_results": interview_results if 'interview_results' in locals() else []
    }
    
    results_path = "../../data/complete_workflow_results.json"
    with open(results_path, 'w') as f:
        json.dump(complete_results, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_path}")
    print("\n✅ Complete HR workflow finished!")

if __name__ == "__main__":
    process_resumes_with_complete_workflow()