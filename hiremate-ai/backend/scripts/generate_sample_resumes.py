# backend/scripts/generate_sample_resumes.py
import os
import json
from datetime import datetime
import random

def generate_name():
    """Generate diverse names"""
    first_names = [
        "Sarah", "Alex", "Michael", "Priya", "Jennifer", "Raj", "Lisa", "James", 
        "Maria", "David", "Emily", "Kevin", "Robert", "John", "Nancy", "Wei",
        "Carlos", "Fatima", "Ahmed", "Olga", "Dmitri", "Yuki", "Hassan",
        "Isabella", "Marcus", "Aisha", "Victor", "Sophia", "Luis", "Anna"
    ]
    last_names = [
        "Chen", "Kumar", "Rodriguez", "Patel", "Williams", "Singh", "Wang", 
        "Wilson", "Garcia", "Thompson", "Zhang", "Brown", "Johnson", "Doe", 
        "Miller", "Li", "Martinez", "Ali", "Petrov", "Tanaka", "Ibrahim",
        "Rossi", "Smith", "Davis", "Jones", "Taylor", "Anderson", "Thomas", "Moore"
    ]
    return random.choice(first_names), random.choice(last_names)

def generate_education(level):
    """Generate education based on level"""
    universities = {
        "top": ["MIT", "Stanford", "Carnegie Mellon", "UC Berkeley", "Harvard", "Princeton"],
        "good": ["University of Texas", "UCSD", "University of Washington", "Georgia Tech", "UCLA"],
        "average": ["State University", "Regional University", "City College", "Community College"]
    }
    
    degrees = {
        "strong": "Master of Science in Data Science",
        "good": "Master of Science in Computer Science", 
        "average": "Bachelor of Science in Mathematics",
        "weak": "Bachelor of Arts in Business"
    }
    
    if level == "strong":
        return random.choice(universities["top"]), degrees["strong"], "3.8-4.0"
    elif level == "good":
        return random.choice(universities["good"]), degrees["good"], "3.5-3.8"
    elif level == "average":
        return random.choice(universities["average"]), degrees["average"], "3.0-3.5"
    else:
        return random.choice(universities["average"]), degrees["weak"], "2.5-3.0"

def generate_experience(years, level):
    """Generate work experience based on years and level"""
    companies = {
        "top": ["Google", "Meta", "Amazon", "Microsoft", "Netflix", "Apple", "Uber"],
        "good": ["IBM", "Oracle", "Salesforce", "Adobe", "Dell", "HP", "Cisco"],
        "average": ["Tech Startup", "Consulting Firm", "Local Company", "Agency"]
    }
    
    if level == "strong":
        company = random.choice(companies["top"])
        title = "Senior Data Scientist" if years > 5 else "Data Scientist"
    elif level == "good":
        company = random.choice(companies["good"])
        title = "Data Scientist" if years > 3 else "Junior Data Scientist"
    else:
        company = random.choice(companies["average"])
        title = "Data Analyst" if years > 1 else "Analyst Intern"
    
    return company, title

def generate_skills(level):
    """Generate skills based on level"""
    if level == "strong":
        return """Programming Languages: Python, SQL, R, Scala
ML/AI: TensorFlow, PyTorch, scikit-learn, XGBoost, Statistical Modeling, Deep Learning
Tools: Spark, Hadoop, Tableau, Git, Docker, AWS, Jupyter
Databases: PostgreSQL, MySQL, MongoDB, Redshift"""
    elif level == "good":
        return """Programming: Python, SQL, R
Machine Learning: scikit-learn, TensorFlow, Random Forests, Neural Networks
Tools: Tableau, Power BI, Git, Jupyter, Apache Spark (basics)
Databases: PostgreSQL, MySQL, MongoDB"""
    elif level == "average":
        return """Programming: Python (Basic), SQL, Excel
Data Analysis: pandas, numpy (learning), Basic Statistics
Tools: Jupyter Notebook, Tableau, Excel
Currently learning: Machine Learning, TensorFlow"""
    else:
        return """Tools: Excel, Basic SQL
Other: Data Entry, Report Creation, Google Analytics
Learning: Python basics, Statistics"""

def generate_resume_content(name, years, level):
    """Generate complete resume content"""
    first_name, last_name = name
    full_name = f"{first_name} {last_name}"
    email = f"{first_name.lower()}.{last_name.lower()}@email.com"
    
    university, degree, gpa = generate_education(level)
    company, title = generate_experience(years, level)
    skills = generate_skills(level)
    
    # Generate appropriate bullet points based on level
    if level == "strong":
        bullets = [
            f"• Developed machine learning models using Python and TensorFlow improving metrics by {random.randint(25,45)}%",
            f"• Analyzed complex datasets with {random.randint(50,200)}M+ records using SQL and Python",
            f"• Led cross-functional teams to implement data-driven solutions saving ${random.randint(1,5)}M annually",
            "• Published research papers and presented at industry conferences",
            "• Mentored junior data scientists and established ML best practices"
        ]
    elif level == "good":
        bullets = [
            "• Built predictive models using Python and machine learning techniques",
            f"• Created automated reporting pipelines processing {random.randint(1,10)}M+ records daily",
            f"• Improved key metrics by {random.randint(15,25)}% through data analysis",
            "• Collaborated with engineering teams to deploy models in production"
        ]
    elif level == "average":
        bullets = [
            "• Analyzed business data using SQL and Python",
            "• Created dashboards and reports for management",
            "• Assisted in data collection and cleaning processes",
            "• Learning machine learning techniques"
        ]
    else:
        bullets = [
            "• Created reports using Excel",
            "• Assisted with data entry tasks",
            "• Learning SQL and Python basics"
        ]
    
    content = f"""{full_name.upper()}
{email} | +1 {random.randint(200,999)}-555-{random.randint(1000,9999):04d} | LinkedIn

EDUCATION
{university.upper()}
{degree}
GPA: {gpa}

EXPERIENCE
{company.upper()}
{title.upper()}
{chr(10).join(bullets[:3])}

TECHNICAL SKILLS
{skills}

PROJECTS
• {random.choice(['Customer Analysis', 'Sales Forecasting', 'Churn Prediction', 'Recommendation System'])} using {random.choice(['Python', 'Machine Learning', 'SQL'])}
"""
    
    return content, full_name, email

# Generate 30 diverse resumes
resumes_data = {}

# Distribution: 
# 5 strong (85-95 score)
# 8 good (70-85 score)
# 8 average (55-70 score)
# 9 weak (below 55)

categories = [
    ("strong", 5, 5, 8),  # level, count, min_years, max_years
    ("good", 8, 3, 6),
    ("average", 8, 1, 3),
    ("weak", 9, 0, 2)
]

counter = 1
for level, count, min_years, max_years in categories:
    for i in range(count):
        name = generate_name()
        years = random.randint(min_years, max_years)
        content, full_name, email = generate_resume_content(name, years, level)
        
        filename = f"candidate_{counter:02d}_{level}"
        resumes_data[filename] = {
            "name": full_name,
            "email": "panugantivanisree@gmail.com",  # All emails to your address
            "phone": f"+1 {random.randint(200,999)}-555-{random.randint(1000,9999):04d}",
            "experience_years": years,
            "level": level,
            "content": content
        }
        counter += 1

def generate_diverse_resumes():
    """Generate 30 diverse sample resumes"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "..", "data", "resumes", "pending")
    
    # Clear existing resumes
    if os.path.exists(output_dir):
        print("🧹 Clearing existing resumes...")
        for file in os.listdir(output_dir):
            if file.endswith('.txt') or file.endswith('.json'):
                os.remove(os.path.join(output_dir, file))
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📁 Creating 30 resumes in: {output_dir}")
    print("-" * 50)
    
    # Generate each resume
    for filename, resume_data in resumes_data.items():
        # Save resume content
        txt_path = os.path.join(output_dir, f"{filename}.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(resume_data['content'])
        
        print(f"✅ Generated: {filename}.txt ({resume_data['name']} - {resume_data['level']})")
        
        # Save metadata
        metadata = {
            "name": resume_data['name'],
            "email": resume_data['email'],
            "phone": resume_data['phone'],
            "experience_years": resume_data['experience_years'],
            "level": resume_data['level'],
            "generated_at": datetime.now().isoformat()
        }
        
        meta_path = os.path.join(output_dir, f"{filename}_metadata.json")
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    print("\n" + "="*50)
    print("📊 RESUME DISTRIBUTION:")
    print("="*50)
    print(f"Strong candidates: 5 (expect ~5 selected)")
    print(f"Good candidates: 8 (expect ~6-7 selected)")
    print(f"Average candidates: 8 (expect ~3-4 selected)")
    print(f"Weak candidates: 9 (expect ~0-1 selected)")
    print(f"\nTotal: 30 resumes")
    print(f"Expected selections: ~14-17 candidates")
    print(f"Expected to pass assessment: ~10-13 candidates")
    print(f"Expected to complete all interviews: ~6-8 candidates")
    
    print(f"\n📧 All emails set to: venkat.posanipalle3103@gmail.com")
    print("\n✅ Ready to process with multi-step interviews!")

if __name__ == "__main__":
    generate_diverse_resumes()