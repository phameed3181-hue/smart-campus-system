from flask import Flask, render_template, request, jsonify
import json
import os
import matplotlib
matplotlib.use('Agg')  # Prevents GUI errors on cloud servers
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/students', methods=['GET'])
def get_students():
    return jsonify(load_records())

@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.json
    records = load_records()
    
    if any(r['id'] == data['id'] for r in records):
        return jsonify({"success": False, "message": "Student ID already exists!"}), 400
        
    course_entries = data.get('course_scores', [])
    course_count = len(course_entries)
    
    # Calculate Total Fee based on 5,000 per valid enrolled course
    base_fee = course_count * 5000
    
    amenities_fee = 0
    if data.get('hostel') == 'Yes': amenities_fee += 15000
    if data.get('transport') == 'Yes': amenities_fee += 8000
    
    new_student = {
        "id": data['id'],
        "name": data['name'],
        "age": data['age'],
        "tier": data['tier'],
        "hostel": data['hostel'],
        "transport": data['transport'],
        "course_scores": course_entries,
        "total_fee": base_fee + amenities_fee
    }
    
    records.append(new_student)
    save_records(records)
    
    # Generate only the Bar Graph asset
    generate_bar_graph(records)
    return jsonify({"success": True})

@app.route('/api/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    records = load_records()
    updated_records = [r for r in records if r['id'] != student_id]
    save_records(updated_records)
    
    # Refresh the Bar Graph asset
    generate_bar_graph(updated_records)
    return jsonify({"success": True})

def generate_bar_graph(records):
    """Generates a Professional Light-Mode Bar Graph inside static directory"""
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir, exist_ok=True)
        
    chart_path = os.path.join(static_dir, 'analytics_bar.png')
    
    fig, ax = plt.subplots(figsize=(6, 4), facecolor='#ffffff')
    ax.set_facecolor('#ffffff')

    if not records:
        ax.text(0.5, 0.5, 'No Data Found\n(Add student records to generate visualization)', 
                color='#6c757d', ha='center', va='center', fontsize=11, weight='bold')
        ax.axis('off')
        plt.tight_layout()
        plt.savefig(chart_path, facecolor='#ffffff', dpi=150)
        plt.close()
        return

    student_ids = [r['id'] for r in records]
    total_fees = [r['total_fee'] for r in records]

    # Draw modern purple metric tracking bars
    ax.bar(student_ids, total_fees, color='#7209b7', edgecolor='#560bad', width=0.4)
    
    ax.tick_params(colors='#2b2d42', labelsize=9)
    ax.xaxis.label.set_color('#2b2d42')
    ax.yaxis.label.set_color('#2b2d42')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#dee2e6')
    ax.spines['bottom'].set_color('#dee2e6')
    ax.grid(axis='y', linestyle='--', alpha=0.5, color='#dee2e6')
    
    plt.title("Financial Record Account Mapping (₹)", color='#2b2d42', fontsize=12, pad=10, weight='bold')
    plt.ylabel("Total Fee Amount (INR)")
    plt.xlabel("Student Unique ID")
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(chart_path, facecolor='#ffffff', dpi=150)
    plt.close()

if __name__ == '__main__':
    records = load_records()
    generate_bar_graph(records)
    app.run(debug=True, host='0.0.0.0', port=5000)
