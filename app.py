from flask import Flask, render_template, request, redirect, url_for
import os
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Prevents GUI popups on the server background
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
STORAGE_FILE = "campus_records.json"

# ==========================================
# FILE MANAGEMENT & UTILITY FUNCTIONS
# ==========================================

def load_data():
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def save_data(data):
    try:
        with open(STORAGE_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"Failed to write data to disk: {e}")

def calculate_fees(enrolled_courses, student_type, has_hostel, has_transport):
    """Calculates updated dynamic tuition fees, optional hostel, and transport charges."""
    base_fee_per_course = 10000  # Set to 10000 as requested
    tuition_fee = len(enrolled_courses) * base_fee_per_course
    
    # 20% tuition concession for Scholars
    if student_type.lower() == "scholar":
        tuition_fee *= 0.80  
        
    # Optional Facility Add-ons
    hostel_fee = 40000 if has_hostel else 0
    transport_fee = 15000 if has_transport else 0
    
    total_fee = tuition_fee + hostel_fee + transport_fee
    return int(total_fee)

def evaluate_grade(marks):
    if marks is None: return "N/A"
    if marks >= 90: return "S"
    elif marks >= 80: return "A"
    elif marks >= 70: return "B"
    elif marks >= 60: return "C"
    elif marks >= 50: return "D"
    else: return "F"


# ==========================================
# WEB APPLICATION ROUTES
# ==========================================

@app.route('/')
def index():
    students = load_data()
    display_students = []
    rows = []

    for sid, info in students.items():
        # Read the optional flags, default to False if missing from older records
        has_hostel = info.get('hostel', False)
        has_transport = info.get('transport', False)
        
        fee = calculate_fees(info['enrolled_courses'], info['type'], has_hostel, has_transport)
        
        graded_courses = {}
        for course, marks in info['enrolled_courses'].items():
            grade = evaluate_grade(marks)
            graded_courses[course] = {"marks": marks if marks is not None else "Pending", "grade": grade}
            
            if marks is not None:
                rows.append({"Course": course, "Marks": marks})

        display_students.append({
            'id': sid,
            'name': info['name'],
            'type': info['type'],
            'hostel': "Yes" if has_hostel else "No",
            'transport': "Yes" if has_transport else "No",
            'courses': graded_courses,
            'fee': fee
        })

    # Data Analytics Pipeline (Pandas, NumPy & Matplotlib)
    chart_url = None
    if rows:
        df = pd.DataFrame(rows)
        course_means = df.groupby("Course")["Marks"].agg(np.mean)

        plt.figure(figsize=(6.5, 3.5))
        course_means.plot(kind='bar', color=['#3498db', '#2ecc71', '#e74c3c', '#f1c40f'])
        plt.title('Average Performance Metrics per Course', fontsize=12, fontweight='bold', pad=10)
        plt.ylabel('Average Marks', fontsize=10)
        plt.xlabel('Course Titles', fontsize=10)
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        plt.tight_layout()

        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        chart_url = base64.b64encode(img.getvalue()).decode('utf-8')
        plt.close()

    return render_template('index.html', students=display_students, chart_url=chart_url)


@app.route('/register', methods=['POST'])
def register():
    sid = request.form['student_id'].strip().upper()
    name = request.form['name'].strip()
    stype = request.form['type']
    
    # Checkbox values are only sent if checked
    has_hostel = 'hostel' in request.form
    has_transport = 'transport' in request.form
    
    if not sid or not name:
        return redirect(url_for('index'))

    students = load_data()
    if sid not in students:
        students[sid] = {
            "name": name, 
            "type": stype, 
            "hostel": has_hostel,
            "transport": has_transport,
            "enrolled_courses": {}
        }
        save_data(students)
        
    return redirect(url_for('index'))


@app.route('/enroll', methods=['POST'])
def enroll():
    sid = request.form['student_id'].strip().upper()
    course = request.form['course'].strip()
    marks_raw = request.form['marks'].strip()
    
    if not sid or not course:
        return redirect(url_for('index'))

    students = load_data()
    if sid in students:
        marks_val = int(marks_raw) if marks_raw != "" else None
        students[sid]["enrolled_courses"][course] = marks_val
        save_data(students)
        
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)