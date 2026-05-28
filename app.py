from flask import Flask, render_template, request, jsonify
import json
import os
import matplotlib
matplotlib.use('Agg')  # Prevents GUI interface errors on cloud servers like Render
import matplotlib.pyplot as plt

app = Flask(__name__)
DATA_FILE = 'campus_records.json'

def load_records():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_records(records):
    with open(DATA_FILE, 'w') as f:
        json.dump(records, f, indent=4)

def calculate_fees(student_data):
    course_count = len(student_data.get('courses', []))
    base_fee = course_count * 5000
    amenities_fee = 0
    if student_data.get('hostel') == 'Yes': amenities_fee += 15000
    if student_data.get('transport') == 'Yes': amenities_fee += 8000
    return base_fee + amenities_fee

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/students', methods=['GET'])
def get_students():
    return jsonify(load_records())

# OPERATION 1: Add Base Student Profile
@app.route('/api/students', methods=['POST'])
def add_student_identity():
    data = request.json
    records = load_records()
    
    if any(r['id'] == data['id'] for r in records):
        return jsonify({"success": False, "message": "Student ID already exists!"}), 400
        
    new_student = {
        "id": data['id'],
        "name": data['name'],
        "age": data['age'],
        "tier": data['tier'],
        "hostel": "No",
        "transport": "No",
        "courses": [],
        "sub1": 0, "sub2": 0, "sub3": 0, "sub4": 0, "sub5": 0,
        "total_fee": 0
    }
    
    records.append(new_student)
    save_records(records)
    
    generate_pie_chart(records)
    generate_bar_graph(records)
    return jsonify({"success": True, "message": "Student profile added successfully! Now use Block 2 to add courses & facilities."})

# OPERATION 2: Add Student Courses, Facilities & Academic Marks
@app.route('/api/students/enrollment', methods=['POST'])
def update_student_enrollment():
    data = request.json
    records = load_records()
    
    student_to_update = None
    for r in records:
        if r['id'] == data['id']:
            student_to_update = r
            break
            
    if not student_to_update:
        return jsonify({"success": False, "message": "Student ID not found! Please create the profile in Block 1 first."}), 404
        
    # Bind incoming values
    student_to_update['courses'] = data.get('courses', [])
    student_to_update['hostel'] = data.get('hostel', 'No')
    student_to_update['transport'] = data.get('transport', 'No')
    student_to_update['sub1'] = data.get('sub1', 0)
    student_to_update['sub2'] = data.get('sub2', 0)
    student_to_update['sub3'] = data.get('sub3', 0)
    student_to_update['sub4'] = data.get('sub4', 0)
    student_to_update['sub5'] = data.get('sub5', 0)
    
    # Recalculate financial breakdown metrics
    student_to_update['total_fee'] = calculate_fees(student_to_update)
    
    save_records(records)
    generate_pie_chart(records)
    generate_bar_graph(records)
    return jsonify({"success": True, "message": "Student courses, facilities, and marks successfully updated!"})

@app.route('/api/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    records = load_records()
    updated_records = [r for r in records if r['id'] != student_id]
    save_records(updated_records)
    
    generate_pie_chart(updated_records)
    generate_bar_graph(updated_records)
    return jsonify({"success": True})

def generate_pie_chart(records):
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    if not os.path.exists(static_dir): os.makedirs(static_dir, exist_ok=True)
    chart_path = os.path.join(static_dir, 'analytics_pie.png')
    fig, ax = plt.subplots(figsize=(5, 4), facecolor='#ffffff')
    ax.set_facecolor('#ffffff')

    if not records:
        ax.text(0.5, 0.5, 'No Data Found', color='#6c757d', ha='center', va='center', weight='bold')
        ax.axis('off')
        plt.savefig(chart_path, dpi=150); plt.close(); return

    tier_counts = {"Regular": 0, "Scholar": 0}
    for r in records:
        if r['tier'] in tier_counts: tier_counts[r['tier']] += 1

    ax.pie(list(tier_counts.values()), labels=list(tier_counts.keys()), autopct='%1.1f%%', startangle=140, colors=['#4361ee', '#4cc9f0'])
    plt.title("Student Tier Distribution Matrix", color='#2b2d42', weight='bold')
    plt.tight_layout()
    plt.savefig(chart_path, dpi=150); plt.close()

def generate_bar_graph(records):
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    if not os.path.exists(static_dir): os.makedirs(static_dir, exist_ok=True)
    chart_path = os.path.join(static_dir, 'analytics_bar.png')
    fig, ax = plt.subplots(figsize=(5, 4), facecolor='#ffffff')
    ax.set_facecolor('#ffffff')

    if not records:
        ax.text(0.5, 0.5, 'No Fee Data Found', color='#6c757d', ha='center', va='center', weight='bold')
        ax.axis('off')
        plt.savefig(chart_path, dpi=150); plt.close(); return

    student_ids = [str(r['id']) for r in records]
    total_fees = [float(r['total_fee']) for r in records]

    ax.bar(student_ids, total_fees, color='#7209b7', width=0.4)
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    plt.title("Financial Record Account Mapping (₹)", color='#2b2d42', weight='bold')
    plt.tight_layout()
    plt.savefig(chart_path, dpi=150); plt.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
