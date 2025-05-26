import os
import re
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ─── Load your LinkedIn creds ───────────────────────────────────────────────
load_dotenv()
EMAIL    = os.getenv("LINKEDIN_EMAIL")
PASSWORD = os.getenv("LINKEDIN_PASSWORD")

# ─── Paths ───────────────────────────────────────────────────────────────────
AUTH_FILE = "automation/.linkedin_auth.json"
JD_FILE   = "automation/latest_jd.txt"

# ─── Helper to extract a clean title from the first line of your JD ─────────
def extract_title_from_jd(jd_text: str) -> str:
    lines = jd_text.strip().splitlines()
    if not lines:
        return "Software Engineer"
    first = lines[0].strip()
    m = re.search(r"seeking a[n]?\s+(.+?)[\.,]", first, re.IGNORECASE)
    return m.group(1).strip() if m else first

def main():
    # 1) Read your generated JD
    try:
        jd_text = open(JD_FILE, "r", encoding="utf-8").read()
    except FileNotFoundError:
        jd_text = ""
    job_title = extract_title_from_jd(jd_text)
    
    # Clean up job title - remove asterisks and "Job Title:" prefix if present
    if "Job Title:" in job_title:
        job_title = job_title.split("Job Title:")[-1].strip()
    job_title = job_title.strip("*").strip()

    # 2) Launch Playwright and login/reuse session
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        if os.path.exists(AUTH_FILE):
            context = browser.new_context(storage_state=AUTH_FILE)
        else:
            context = browser.new_context()
            page = context.new_page()
            page.goto("https://www.linkedin.com/login")
            page.fill("input#username", EMAIL)
            page.fill("input#password", PASSWORD)
            page.click("button[type=submit]")
            page.wait_for_timeout(5000)
            context.storage_state(path=AUTH_FILE)

        page = context.new_page()

        # 3) Go to the job post start page
        page.goto("https://www.linkedin.com/job-posting/v2/?trk=flagship3_job_home")
        page.wait_for_selector("input", timeout=10000)

        # 4) Fill the extracted title - FIXED: Now passing only the job title
        try:
            page.get_by_label("Job title").fill(job_title)
        except:
            page.locator("input").first.fill(job_title)

        # 5) Click "Start with my job description"
        page.get_by_role("button", name="Start with my job description").click()
        page.wait_for_timeout(4000)

        # 6) Inject your full JD into the rich-text editor
        page.wait_for_selector('div[role="textbox"]', timeout=8000)
        page.evaluate(
            """(desc) => {
                const box = document.querySelector('div[role="textbox"]');
                if (box) box.innerText = desc;
            }""",
            jd_text
        )
        page.wait_for_timeout(2000)

        # 7) Job Details screen
        #    Select department, seniority, employment type, workplace type
        try:
            page.select_option("select[name='department']", "engineering")
            page.select_option("select[name='seniorityLevel']", "MID_SENIORITY")
            page.select_option("select[name='employmentType']", "FULL_TIME")
            page.select_option("select[name='workplaceType']", "REMOTE")
        except Exception as e:
            print("⚠️ Could not fill Job Details selectors:", e)
        page.click("button:has-text('Continue')")
        page.wait_for_timeout(3000)

        # 8) Skills & Experience screen
        skills = ["Python", "FastAPI", "PostgreSQL"]
        for skill in skills:
            try:
                page.fill('input[aria-label="Add skill"]', skill)
                page.keyboard.press("Enter")
            except Exception:
                pass
        page.click("button:has-text('Continue')")
        page.wait_for_timeout(3000)

        # 9) Screening Questions screen (skip)
        page.click("button:has-text('Continue')")
        page.wait_for_timeout(3000)

        # 10) Confirm screening questions and job settings screen
        try:
            # This screen shows a summary of settings - just click Continue
            page.wait_for_selector("text=Confirm your screening questions and job settings", timeout=5000)
            page.click("button:has-text('Continue')")
            print("✅ Confirmed screening questions and job settings")
        except Exception as e:
            print("⚠️ Could not confirm screening settings:", e)
        page.wait_for_timeout(3000)

        # 11) Review ideal qualifications screen
        try:
            # This screen shows the AI-generated qualifications - just click Continue
            page.wait_for_selector("text=Review your ideal qualifications", timeout=5000)
            page.click("button:has-text('Continue')")
            print("✅ Reviewed ideal qualifications")
        except Exception as e:
            print("⚠️ Could not review qualifications:", e)
        page.wait_for_timeout(3000)

        # 12) Budget & Promotion screen: choose Free $0
        try:
            page.wait_for_selector("text=Promote your job post", timeout=5000)
            # Click on the Free option (which should already be selected)
            free_option = page.locator("div").filter(has_text="Free$0").first
            free_option.click()
            print("✅ Selected Free posting option")
        except Exception as e:
            print("⚠️ Could not select Free option:", e)
        
        # Click Post job button on the promotion screen
        try:
            page.click("button:has-text('Post job')")
            print("✅ 'Post job' clicked — your job is now live!")
        except Exception as e:
            print("⚠️ Could not click 'Post job':", e)
        page.wait_for_timeout(3000)

        browser.close()

if __name__ == "__main__":
    main()