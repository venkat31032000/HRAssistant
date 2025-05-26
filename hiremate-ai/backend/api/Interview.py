from fastapi import APIRouter
from pydantic import BaseModel
from agents.Interview import InterviewPlannerAgent

router = APIRouter()
interview_agent = InterviewPlannerAgent()

class InterviewRequest(BaseModel):
    job_description: str
    experience_level: str  # e.g., "entry-level", "mid-level", "senior"
    num_rounds: int = 3

@router.post("/interview/plan")
def generate_interview_plan(req: InterviewRequest):
    plan = interview_agent.generate_rounds(
        job_description=req.job_description,
        experience_level=req.experience_level,
        num_rounds=req.num_rounds
    )
    return plan
