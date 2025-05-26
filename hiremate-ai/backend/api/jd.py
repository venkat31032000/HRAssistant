from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from agents.jd import JDPlannerAgent
import subprocess
import os
import sys

router = APIRouter()
jd_agent = JDPlannerAgent()

class JDRequest(BaseModel):
    role: str
    company: str = "HireMate AI"  # Default company name
    location: str = "Boston, Massachusetts, United States"
    workplace_type: str = "On-site"  # On-site, Remote, Hybrid
    job_type: str = "Full-time"  # Full-time, Part-time, Contract, Internship
    experience: str = ""
    skills: str = ""
    salary: str = ""

class JDResponse(BaseModel):
    job_description: str
    status: str
    indeed_automation: str  # CHANGED: from linkedin_automation
    job_config: dict

@router.post("/jd/generate", response_model=JDResponse)
def generate_jd(req: JDRequest):
    try:
        print(f"🚀 Generating JD for: {req.role} at {req.company}")
        
        # Generate the job description using your agent
        jd = jd_agent.generate_jd(
            role=req.role,
            company=req.company,
            location=req.location,
            workplace_type=req.workplace_type,
            employment_type=req.job_type,
            experience=req.experience or "Mid-level",
            skills=req.skills or "Relevant technical skills",
            salary=req.salary or "Competitive salary package",
        )

        # Create job configuration for Indeed automation  # CHANGED: comment
        job_config = {
            "job_title": req.role,
            "company": req.company,
            "location": req.location,
            "workplace_type": req.workplace_type,  # CHANGED: removed .replace() - Indeed uses normal format
            "job_type": req.job_type,  # CHANGED: removed .replace() - Indeed uses normal format
            "experience": req.experience,
            "skills": req.skills,
            "salary": req.salary  # ADDED: salary field for Indeed
        }

        # Save the JD to a file that the simulator will read
        automation_dir = os.path.join(os.getcwd(), "automation")
        os.makedirs(automation_dir, exist_ok=True)
        
        # Save JD content
        jd_file = os.path.join(automation_dir, "latest_jd.txt")
        with open(jd_file, "w", encoding="utf-8") as f:
            f.write(jd)
        
        # Save job config for Indeed automation  # CHANGED: comment
        config_file = os.path.join(automation_dir, "job_config.json")
        import json
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(job_config, f, indent=2)
        
        print(f"📄 JD saved to: {jd_file}")
        print(f"⚙️ Config saved to: {config_file}")

        # Determine Python executable path
        if sys.platform == "win32":
            venv_python = os.path.join(os.getcwd(), "venv", "Scripts", "python.exe")
        else:
            venv_python = os.path.join(os.getcwd(), "venv", "bin", "python")
        
        # Fallback to system python if venv python doesn't exist
        if not os.path.exists(venv_python):
            venv_python = sys.executable
            print(f"⚠️ Using system python: {venv_python}")

        # Path to Indeed simulator  # CHANGED: comment (but keeping same filename)
        simulator_script = os.path.abspath(os.path.join("..", "linkedin_post_simulator.py"))

        if not os.path.exists(simulator_script):
            print(f"❌ Simulator not found at: {simulator_script}")
            raise HTTPException(status_code=404, detail=f"Indeed simulator not found")  # CHANGED: error message

        # Launch the Indeed post simulator as a subprocess  # CHANGED: comment
        try:
            process = subprocess.Popen(
                [venv_python, simulator_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print(f"🤖 Indeed automation started (PID: {process.pid})")  # CHANGED: message
            
            return JDResponse(
                job_description=jd,
                status="success",
                indeed_automation="Indeed posting automation started successfully",  # CHANGED: field name and message
                job_config=job_config
            )
            
        except Exception as e:
            print(f"❌ Failed to start Indeed automation: {e}")  # CHANGED: message
            return JDResponse(
                job_description=jd,
                status="partial_success", 
                indeed_automation=f"JD generated but Indeed automation failed: {str(e)}",  # CHANGED: field name and message
                job_config=job_config
            )

    except Exception as e:
        print(f"❌ JD Generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate job description: {str(e)}")

@router.get("/jd/status")
def get_jd_status():
    """Check if JD generation and Indeed automation are ready"""  # CHANGED: comment
    automation_dir = os.path.join(os.getcwd(), "automation")
    jd_file = os.path.join(automation_dir, "latest_jd.txt")
    config_file = os.path.join(automation_dir, "job_config.json")
    simulator_script = os.path.abspath(os.path.join("..", "linkedin_post_simulator.py"))
    
    return {
        "jd_agent_ready": True,
        "latest_jd_exists": os.path.exists(jd_file),
        "job_config_exists": os.path.exists(config_file),
        "indeed_simulator_exists": os.path.exists(simulator_script),  # CHANGED: field name
        "automation_dir": automation_dir
    }