from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

class JDPlannerAgent:
    def __init__(self):
        prompt = PromptTemplate.from_template("""
You are an AI HR assistant helping a startup write job descriptions.

Generate a clear, inclusive, and startup-appropriate job description using this info:

Role: {role}
Company: {company}
Location: {location}  
Workplace Type: {workplace_type}
Experience: {experience}
Skills: {skills}
Employment Type: {employment_type}
Salary Range: {salary}

Structure the job description with these sections:
- Job Title and Brief Company Overview
- Role Summary  
- Key Responsibilities (use bullet points)
- Required Qualifications (use bullet points)
- Preferred Qualifications (use bullet points)
- What We Offer (use bullet points)
- How to Apply

Use bullet points where needed. Be professional but friendly with startup energy.
Make it engaging and attractive to top talent.
Make sure to mention the workplace arrangement ({workplace_type}) in appropriate sections.
Include the company name ({company}) naturally throughout the job description.
""")

        model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        self.chain = prompt | model

    def generate_jd(self, role, location, experience, skills, employment_type, salary, workplace_type="Remote", company="HireMate AI"):
        """Generate job description using LangChain and GPT-4o-mini"""
        print(f"🤖 JD Agent called with: {role} at {company} in {location} ({workplace_type})")
        
        input_data = {
            "role": role,
            "company": company or "Our Company",
            "location": location or "Flexible Location",
            "workplace_type": workplace_type or "Remote",
            "experience": experience or "Mid-level",
            "skills": skills or "Relevant technical skills",
            "employment_type": employment_type or "Full-time",
            "salary": salary or "Competitive salary based on experience"
        }
        
        try:
            result = self.chain.invoke(input_data)
            print("✅ JD generated successfully")
            return result.content
        except Exception as e:
            print(f"❌ Error generating JD: {e}")
            return self._generate_fallback_jd(input_data)
    
    def _generate_fallback_jd(self, data):
        """Fallback job description template"""
        return f"""# {data['role']}

## Company Overview
Join {data['company']}, an innovative startup building the future of technology. We're looking for passionate individuals to help us scale and succeed.

## Role Summary
We are seeking a talented {data['role']} to join our dynamic team. This {data['workplace_type'].lower()} position offers an exciting opportunity to work with cutting-edge technologies and make a real impact.

## Key Responsibilities
• Develop and maintain high-quality solutions in your area of expertise
• Collaborate with cross-functional teams to deliver exceptional results
• Participate in technical discussions and contribute to strategic decisions
• Mentor team members and share knowledge across the organization
• Drive innovation and continuous improvement initiatives

## Required Qualifications
• {data['experience']} experience in relevant field
• Strong expertise in: {data['skills']}
• Excellent problem-solving and analytical thinking abilities
• Strong communication and collaboration skills
• Bachelor's degree or equivalent experience

## Preferred Qualifications
• Advanced degree in relevant field
• Experience with modern development tools and methodologies
• Leadership or mentoring experience
• Industry certifications
• Track record of successful project delivery

## What We Offer
• {data['salary']}
• Comprehensive health, dental, and vision insurance
• {data['workplace_type']} work flexibility
• Professional development opportunities
• Collaborative and inclusive work environment
• Opportunity for career growth and advancement

## How to Apply
Ready to join {data['company']}? We'd love to hear from you! Apply now and become part of our innovative team.

---
*{data['company']} is an equal opportunity employer committed to diversity and inclusion.*
"""