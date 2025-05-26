import re
from langchain_openai import ChatOpenAI

class ResumeAgent:
    def __init__(self):
        # Initialize the language model with desired settings
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    def score_resume(self, resume_text: str, job_description: str, referred: bool = False) -> dict:
        # Prompt to guide the LLM in evaluating the resume
        prompt = f"""
You are an ATS. Compare resume to JD.

Job Description:
{job_description}

Resume:
{resume_text}

Candidate referred: {referred}

1. Score from 0–100.
2. Add +5 if referred.
3. Decision: shortlist if score >= 60, else reject.
4. Give a short reason.

Output like:
Score: 68
Decision: shortlist
Reason: Good skill match, referred.
"""

        # Get response from the language model
        response = self.llm.invoke(prompt)
        raw = response.content

        # Use regex to extract structured data from the LLM response
        score_match = re.search(r"Score:\s*(\d+)", raw)
        decision_match = re.search(r"Decision:\s*(\w+)", raw)
        reason_match = re.search(r"Reason:\s*(.*)", raw)

        # Parse extracted values safely
        score = int(score_match.group(1)) if score_match else None
        decision = decision_match.group(1).lower() if decision_match else "undecided"
        reason = reason_match.group(1).strip() if reason_match else "No reason provided"

        # Return structured result
        return {
            "score": score,
            "decision": decision,
            "reason": reason,
            "raw_output": raw  # Optional: includes full LLM response for debugging
        }
