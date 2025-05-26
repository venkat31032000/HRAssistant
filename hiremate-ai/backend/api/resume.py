from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from agents.jd import JDPlannerAgent
import subprocess
import os
import sys
import json

router = APIRouter()
jd_agent = JDPlannerAgent()

class JDRequest(BaseModel):
    role: str
    company: str = "HireMate AI"
    location: str = "Boston, Massachusetts, United States"
    workplace_type: str = "Remote"  # Remote, On-site, Hybrid
    job_type: str = "Full-time"  # Full-time, Part-time, Contract, Internship
    experience: str = ""
    skills: str = ""
    salary: str = ""

class JDResponse(BaseModel):
    job_description: str
    status: str
    linkedin_automation: str
    job_config: dict

@router.post("/jd/generate", response_model=JDResponse)
def generate_jd(req: JDRequest):
    try:
        print(f"🚀 Generating JD for: {req.role} at {req.company}")
        
        # Generate job description using JD agent with correct parameter order
        jd = jd_agent.generate_jd(
            role=req.role,
            location=req.location,
            experience=req.experience or "Mid-level",
            skills=req.skills or "Relevant technical skills",
            employment_type=req.job_type,
            salary=req.salary or "Competitive salary package",
            workplace_type=req.workplace_type,
            company=req.company
        )

        # Create job configuration for LinkedIn automation
        job_config = {
            "job_title": req.role,
            "company": req.company,
            "location": req.location,
            "workplace_type": req.workplace_type,
            "job_type": req.job_type,
            "experience": req.experience,
            "skills": req.skills,
            "salary": req.salary
        }

        # Create automation directory
        automation_dir = os.path.join(os.getcwd(), "automation")
        os.makedirs(automation_dir, exist_ok=True)
        
        # Save JD content for LinkedIn simulator
        jd_file = os.path.join(automation_dir, "latest_jd.txt")
        with open(jd_file, "w", encoding="utf-8") as f:
            f.write(jd)
        
        # Save job config for LinkedIn automation
        config_file = os.path.join(automation_dir, "job_config.json")
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(job_config, f, indent=2)
        
        print(f"📄 JD saved to: {jd_file}")
        print(f"⚙️ Config saved to: {config_file}")

        # Launch LinkedIn automation
        linkedin_result = launch_linkedin_automation()

        return JDResponse(
            job_description=jd,
            status="success",
            linkedin_automation=linkedin_result,
            job_config=job_config
        )

    except Exception as e:
        print(f"❌ JD Generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate job description: {str(e)}")

def launch_linkedin_automation():
    """Launch LinkedIn automation as subprocess"""
    try:
        # Determine Python executable path
        if sys.platform == "win32":
            venv_python = os.path.join(os.getcwd(), "venv", "Scripts", "python.exe")
        else:
            venv_python = os.path.join(os.getcwd(), "venv", "bin", "python")
        
        # Fallback to system python if venv python doesn't exist
        if not os.path.exists(venv_python):
            venv_python = sys.executable
            print(f"⚠️ Using system python: {venv_python}")

        # Path to LinkedIn simulator (one level up from backend)
        simulator_script = os.path.abspath(os.path.join("..", "linkedin_post_simulator.py"))

        if not os.path.exists(simulator_script):
            print(f"❌ Simulator not found at: {simulator_script}")
            return "LinkedIn simulator not found"

        # Launch the LinkedIn simulator as background process
        process = subprocess.Popen(
            [venv_python, simulator_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"🤖 LinkedIn automation started (PID: {process.pid})")
        return f"LinkedIn posting automation started successfully (PID: {process.pid})"
        
    except Exception as e:
        print(f"❌ Failed to start LinkedIn automation: {e}")
        return f"LinkedIn automation failed: {str(e)}"

@router.get("/jd/status")
def get_jd_status():
    """Check if JD generation and LinkedIn automation are ready"""
    automation_dir = os.path.join(os.getcwd(), "automation")
    jd_file = os.path.join(automation_dir, "latest_jd.txt")
    config_file = os.path.join(automation_dir, "job_config.json")
    simulator_script = os.path.abspath(os.path.join("..", "linkedin_post_simulator.py"))
    
    return {
        "jd_agent_ready": True,
        "latest_jd_exists": os.path.exists(jd_file),
        "job_config_exists": os.path.exists(config_file),
        "linkedin_simulator_exists": os.path.exists(simulator_script),
        "automation_dir": automation_dir,
        "simulator_path": simulator_script
    }

@router.get("/jd/test")
def test_jd_generation():
    """Test endpoint for JD generation"""
    test_request = JDRequest(
        role="Senior Software Engineer",
        company="HireMate AI",
        location="Remote / San Francisco, CA",
        workplace_type="Remote",
        job_type="Full-time",
        experience="Senior (5+ years)",
        skills="Python, FastAPI, React, PostgreSQL, AWS",
        salary="$120,000 - $180,000 + equity"
    )
    
    return generate_jd(test_request)