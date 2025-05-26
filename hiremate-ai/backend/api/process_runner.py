from flask import Blueprint, jsonify, Response
import subprocess
import threading
import queue
import json
import os
import time
import sys  # Added this import

# Create Blueprint
process_runner_bp = Blueprint('process_runner', __name__)

# Global variables
process_queue = queue.Queue()
process_status = {
    "running": False,
    "completed": False,
    "error": None,
    "logs": [],
    "stats": {
        "total_resumes": 30,
        "processed": 0,
        "selected": 0,
        "rejected": 0,
        "emails_sent": 0,
        "assessments_sent": 0,
        "interviews_scheduled": 0,
        "offers_made": 0
    },
    "current_phase": "Not Started"
}

def parse_stats(line):
    """Parse statistics from log line"""
    stats = {}
    
    if "Total Resumes:" in line:
        match = line.split("Total Resumes: ")
        if len(match) > 1:
            stats['total'] = int(match[1].strip())
    
    if "Selected for Assessment:" in line:
        match = line.split("Selected for Assessment: ")
        if len(match) > 1:
            stats['selected'] = int(match[1].strip())
    
    if "Passed Assessment:" in line:
        match = line.split("Passed Assessment: ")
        if len(match) > 1:
            stats['interviews'] = int(match[1].strip())
    
    if "Final Offers:" in line:
        match = line.split("Final Offers: ")
        if len(match) > 1:
            stats['offers'] = int(match[1].strip())
    
    return stats

def parse_log_line(line):
    """Parse log line to extract statistics"""
    global process_status
    
    # Update phase
    if "RESUME SCREENING PHASE" in line or "=== RESUME SCREENING ===" in line:
        process_status["current_phase"] = "Resume Screening"
    elif "ASSESSMENT PHASE" in line or "=== ASSESSMENT PHASE ===" in line:
        process_status["current_phase"] = "Assessment Phase"
    elif "INTERVIEW PHASE" in line or "=== INTERVIEW PROCESS ===" in line:
        process_status["current_phase"] = "Interview Phase"
    elif "JOB OFFER PHASE" in line or "=== JOB OFFERS ===" in line:
        process_status["current_phase"] = "Final Offers"
    
    # Extract numbers from specific log patterns
    if "Processing resume" in line and "/" in line:
        try:
            parts = line.split("/")
            current = int(parts[0].split()[-1])
            process_status["stats"]["processed"] = current
        except:
            pass
    
    if "✓ Selected -" in line or "Selected:" in line:
        process_status["stats"]["selected"] += 1
    elif "✗ Rejected -" in line or "Rejected:" in line:
        process_status["stats"]["rejected"] += 1
    
    if "Sending selection email to" in line or "Sending rejection email to" in line:
        process_status["stats"]["emails_sent"] += 1
    
    if "Sending assessment to" in line:
        process_status["stats"]["assessments_sent"] += 1
    
    if "Scheduling" in line and "interview with" in line:
        process_status["stats"]["interviews_scheduled"] += 1
    
    if "Sending job offer to" in line or "Job offer sent to" in line:
        process_status["stats"]["offers_made"] += 1

def run_process():
    """Run the actual Python script"""
    global process_status
    
    try:
        # Get the scripts directory path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script_dir = os.path.join(base_dir, "scripts")
        
        # Run the script with the same Python interpreter (FIXED)
        # Set environment to handle Unicode properly on Windows
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        process = subprocess.Popen(
            [sys.executable, "process_resumes_with_email.py"],  # Changed from "python" to sys.executable
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            cwd=script_dir,
            stdin=subprocess.PIPE,
            env=env,
            encoding='utf-8'
        )
        
        # Auto-answer yes to the confirmation
        process.stdin.write("yes\n")
        process.stdin.flush()
        
        # Read output line by line
        for line in iter(process.stdout.readline, ''):
            if line:
                line = line.strip()
                timestamp = time.strftime("%I:%M:%S %p")
                log_entry = f"{timestamp} - {line}"
                
                # Add to queue for streaming
                process_queue.put(log_entry)
                
                # Store in status
                process_status["logs"].append(log_entry)
                
                # Parse the line for statistics
                parse_log_line(line)
                
                # Also parse for frontend stats format
                stats = parse_stats(line)
                if stats:
                    # Send stats update to frontend
                    stats_update = json.dumps({'stats': stats})
                    process_queue.put(f"STATS:{stats_update}")
                
                # Check if process is complete
                if any(completion_indicator in line for completion_indicator in [
                    "Final Offers:",
                    "Workflow completed successfully",
                    "All job offers sent",
                    "process_resumes_with_complete_workflow()"
                ]):
                    process_status["completed"] = True
                    process_status["current_phase"] = "Completed"
                    process_status["running"] = False
                    
                    # Send completion status
                    process_queue.put(json.dumps({'status': 'completed'}))
                    
                    # Wait a bit for final logs
                    time.sleep(2)
                    
                    # Terminate the subprocess
                    process.terminate()
                    process.wait()
                    
                    # Add completion message
                    completion_time = time.strftime("%I:%M:%S %p")
                    process_queue.put(f"{completion_time} - 🎉 HR Workflow completed successfully!")
                    process_queue.put(f"{completion_time} - ✅ All offers sent. Process terminated.")
                    break
        
        # If process ends naturally
        process.wait()
        
        if process.returncode == 0 and not process_status["completed"]:
            process_status["completed"] = True
            process_status["current_phase"] = "Completed"
        elif process.returncode != 0 and not process_status["completed"]:
            process_status["error"] = f"Process exited with code {process.returncode}"
            
    except Exception as e:
        process_status["error"] = str(e)
    finally:
        process_status["running"] = False

@process_runner_bp.route('/start', methods=['POST'])
def start_process():
    """Start the resume processing script"""
    global process_status
    
    if process_status["running"]:
        return jsonify({"error": "Process already running"}), 400
    
    # Reset status
    process_status = {
        "running": True,
        "completed": False,
        "error": None,
        "logs": [],
        "stats": {
            "total_resumes": 30,
            "processed": 0,
            "selected": 0,
            "rejected": 0,
            "emails_sent": 0,
            "assessments_sent": 0,
            "interviews_scheduled": 0,
            "offers_made": 0
        },
        "current_phase": "Starting..."
    }
    
    # Clear the queue
    while not process_queue.empty():
        process_queue.get()
    
    # Start the process in a thread
    thread = threading.Thread(target=run_process)
    thread.daemon = True
    thread.start()
    
    return jsonify({"status": "started"})

@process_runner_bp.route('/status', methods=['GET'])
def get_status():
    """Get the current process status"""
    return jsonify(process_status)

@process_runner_bp.route('/logs', methods=['GET'])
def stream_logs():
    """Stream logs in real-time"""
    def generate():
        while process_status["running"] or not process_queue.empty():
            try:
                log = process_queue.get(timeout=1)
                
                # Check if it's a stats update
                if log.startswith("STATS:"):
                    stats_data = log.replace("STATS:", "")
                    yield f"data: {stats_data}\n\n"
                else:
                    # Regular log entry
                    yield f"data: {json.dumps({'log': log})}\n\n"
            except:
                # Send heartbeat to keep connection alive
                yield f"data: {json.dumps({'heartbeat': True})}\n\n"
        
        # Send final completion message
        yield f"data: {json.dumps({'status': 'completed', 'completed': True})}\n\n"
    
    return Response(generate(), mimetype="text/event-stream")

@process_runner_bp.route('/results', methods=['GET'])
def get_results():
    """Get the final results JSON file"""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        results_path = os.path.join(base_dir, "..", "data", "complete_workflow_results.json")
        
        if os.path.exists(results_path):
            with open(results_path, 'r') as f:
                return jsonify(json.load(f))
        else:
            return jsonify({"error": "Results file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500