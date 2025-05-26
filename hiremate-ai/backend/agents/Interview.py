from langchain_openai import ChatOpenAI

class InterviewPlannerAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

    def generate_rounds(self, job_description: str, experience_level: str, num_rounds: int = 3) -> dict:
        prompt = f"""
You are an expert technical recruiter at a startup.

Design a {num_rounds}-round interview plan based on this job description and candidate experience level.

Job Description:
{job_description}

Candidate Experience Level: {experience_level}

For each round, return:
- **Round Name**
- **Purpose** (1 line)
- **3–5 questions**, tailored to the candidate's level.

Make sure the rounds reflect the depth and expectations of the experience level.
Return the plan in clear bullet-point or markdown format.
"""

        response = self.llm.invoke(prompt)
        return {
            "interview_plan": response.content
        }

def get_interview_invite(job_title: str, experience_level: str, jd: str, interview_link: str) -> str:
    agent = InterviewPlannerAgent()
    plan = agent.generate_rounds(jd, experience_level)["interview_plan"]

    message = f"""
📩 Interview Invitation

Role: {job_title}
Experience Level: {experience_level}

You’ve been shortlisted! Please prepare for the following interview rounds:

{plan}

🔗 Interview Link: {interview_link}

If you have any questions, reply to this message.

Best regards,  
HireMate HR Team
"""
    return message
