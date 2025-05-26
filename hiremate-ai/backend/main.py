from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import subprocess
import asyncio

# Import your existing routers
from api import jd, resume, Interview

app = FastAPI(title="HireMate AI - HR Automation Platform")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(jd.router)
app.include_router(resume.router)
app.include_router(Interview.router)

# ─── LinkedIn Integration Models ────────────────────────────────────────────
class LinkedInPostRequest(BaseModel):
    job_description: str
    job_title: str
    employment_type: str = "FULL_TIME"
    workplace_type: str = "REMOTE"
    skills: list[str] = ["Python", "FastAPI", "PostgreSQL"]

# ─── LinkedIn API Endpoints ─────────────────────────────────────────────────
@app.post("/api/post-to-linkedin")
async def post_to_linkedin(request: LinkedInPostRequest, background_tasks: BackgroundTasks):
    """
    Post job description to LinkedIn automatically using your Playwright script
    """
    try:
        # Save the job description to the file that your Playwright script reads
        # Script is in parent directory, so go up one level from backend
        automation_dir = os.path.join("..", "automation")
        jd_file_path = os.path.join(automation_dir, "latest_jd.txt")
        
        # Create automation directory if it doesn't exist
        os.makedirs(automation_dir, exist_ok=True)
        
        # Write the job description
        with open(jd_file_path, "w", encoding="utf-8") as f:
            f.write(request.job_description)
        
        # Add the LinkedIn posting as a background task
        background_tasks.add_task(run_linkedin_automation)
        
        return {
            "status": "success",
            "message": "LinkedIn posting initiated! Your job will be posted automatically.",
            "job_title": request.job_title,
            "posting_status": "in_progress"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initiating LinkedIn post: {str(e)}")

@app.get("/api/linkedin-status")
async def get_linkedin_status():
    """
    Check if LinkedIn automation is ready
    """
    # Paths relative to the main project directory (parent of backend)
    auth_file = os.path.join("..", "automation", ".linkedin_auth.json")
    linkedin_script = os.path.join("..", "linkedin_post_simulator.py")  # Correct script name
    
    return {
        "status": "ready",
        "auth_file_exists": os.path.exists(auth_file),
        "script_exists": os.path.exists(linkedin_script),
        "message": "LinkedIn automation is ready to use"
    }

async def run_linkedin_automation():
    """
    Run the LinkedIn automation script in the background
    """
    try:
        print("🚀 Starting LinkedIn automation...")
        
        # Run your Playwright script from the main project directory
        # Change to parent directory first, then run the script
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        result = subprocess.run(
            ["python", "linkedin_post_simulator.py"],  # Correct script name
            cwd=project_root,  # Run from main project directory
            capture_output=True, 
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print("✅ LinkedIn posting completed successfully!")
            print("Output:", result.stdout)
        else:
            print(f"❌ LinkedIn posting failed with return code {result.returncode}")
            print(f"Error: {result.stderr}")
            print(f"Output: {result.stdout}")
            
    except subprocess.TimeoutExpired:
        print("⏰ LinkedIn posting timed out after 5 minutes")
    except Exception as e:
        print(f"💥 LinkedIn automation error: {e}")

# ─── Frontend Routes ────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def read_root():
    # Read the HTML file
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "index.html")
    
    # If frontend folder doesn't exist, create it and save the HTML
    if not os.path.exists(frontend_path):
        os.makedirs(os.path.dirname(frontend_path), exist_ok=True)
        # Return message to create the file
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Setup Required</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .container {
                    text-align: center;
                    background: rgba(255, 255, 255, 0.1);
                    padding: 3rem;
                    border-radius: 20px;
                    backdrop-filter: blur(10px);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 HireMate AI</h1>
                <p>Please save the frontend HTML to:</p>
                <code>backend/frontend/index.html</code>
                <p>The frontend folder has been created for you!</p>
            </div>
        </body>
        </html>
        """)
    
    # Fixed: Use frontend_path instead of "index.html"
    try:
        with open(frontend_path, encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>File Not Found</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .container {
                    text-align: center;
                    background: rgba(255, 255, 255, 0.1);
                    padding: 3rem;
                    border-radius: 20px;
                    backdrop-filter: blur(10px);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>⚠️ Frontend File Missing</h1>
                <p>Could not find: <code>backend/frontend/index.html</code></p>
                <p>Please create the file and try again.</p>
            </div>
        </body>
        </html>
        """)

# Enhanced Dashboard route
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    # Check if LinkedIn automation files exist
    auth_exists = os.path.exists("../automation/.linkedin_auth.json")
    script_exists = os.path.exists("../linkedin_post_simulator.py")  # Correct script name
    latest_jd_exists = os.path.exists("../automation/latest_jd.txt")
    
    status_items = []
    if script_exists:
        status_items.append("✅ LinkedIn automation script ready")
    if auth_exists:
        status_items.append("✅ LinkedIn authentication saved")
    if latest_jd_exists:
        status_items.append("✅ Latest job description available")
    
    if not status_items:
        status_items.append("⚠️ Set up LinkedIn automation script")
    
    status_html = "<br>".join(status_items)
    
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>HireMate Dashboard</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                text-align: center;
                background: rgba(255, 255, 255, 0.1);
                padding: 3rem;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                max-width: 600px;
                width: 100%;
            }}
            h1 {{ margin-bottom: 2rem; }}
            .status {{
                background: rgba(0, 255, 0, 0.2);
                padding: 1rem;
                border-radius: 10px;
                margin: 1rem 0;
                text-align: left;
            }}
            .btn {{
                background: rgba(255, 255, 255, 0.9);
                color: #667eea;
                border: none;
                padding: 12px 24px;
                border-radius: 25px;
                margin: 10px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                font-weight: 600;
            }}
            .btn:hover {{
                background: white;
                transform: translateY(-2px);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 HireMate AI Dashboard</h1>
            <div class="status">
                <strong>System Status:</strong><br>
                {status_html}
            </div>
            <p>Your AI-powered hiring automation platform is ready!</p>
            <div>
                <a href="/" class="btn">🏠 Back to Home</a>
                <a href="/docs" class="btn">📚 API Docs</a>
                <a href="/api/linkedin-status" class="btn">🔗 LinkedIn Status</a>
            </div>
        </div>
    </body>
    </html>
    """)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting HireMate AI Server...")
    print("📍 Frontend: http://localhost:8000")
    print("📍 API Docs: http://localhost:8000/docs")  
    print("📍 Dashboard: http://localhost:8000/dashboard")
    print("🤖 LinkedIn Automation: Ready")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)