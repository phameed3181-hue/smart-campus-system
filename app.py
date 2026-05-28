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
        
    # Calculate Total Fee based on 5,000 per course
    course_count = len(data.get('courses', []))
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
        "courses": data.get('courses', []),
        "sub1": data.get('sub1', 0),
        "sub2": data.get('sub2', 0),
        "sub3": data.get('sub3', 0),
        "sub4": data.get('sub4', 0),
        "sub5": data.get('sub5', 0),
        "total_fee": base_fee + amenities_fee
    }
    
    records.append(new_student)
    save_records(records)
    
    generate_pie_chart(records)
    generate_bar_graph(records)
    return jsonify({"success": True})

@app.route('/api/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    records = load_records()
    updated_records = [r for r in records if r['id'] != student_id]
    save_records(updated_records)
    
    generate_pie_chart(updated_records)
    generate_bar_graph(updated_records)
    return jsonify({"success": True})

def generate_pie_chart(records):
    """Generates a Professional Light-Mode Pie Chart"""
    static_dir = os.path.join('static')
    if not os.path.exists(static_dir): os.makedirs(static_dir)
    chart_path = os.path.join(static_dir, 'analytics_pie.png')
    
    if not records:
        plt.figure(figsize=(5, 4), facecolor='#ffffff')
        plt.text(0.5, 0.5, 'No Tier Data Available', color='#333333', ha='center', va='center')
        plt.axis('off')
        plt.savefig(chart_path, facecolor='#ffffff')
        plt.close()
        return

    tier_counts = {"Regular": 0, "Scholar": 0}
    for r in records:
        if r['tier'] in tier_counts: tier_counts[r['tier']] += 1

    labels = list(tier_counts.keys())
    sizes = list(tier_counts.values())
    if sum(sizes) == 0: sizes = [1, 1]

    colors = ['#4361ee', '#4cc9f0']  # Royal blue and soft sky blue
    fig, ax = plt.subplots(figsize=(5, 4), facecolor='#ffffff')
    ax.set_facecolor('#ffffff')
    
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors, textprops=dict(color="#333333"))
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_weight('bold')

    plt.title("Student Tier Distribution Matrix", color='#333333', fontsize=12, pad=10, weight='bold')
    plt.tight_layout()
    plt.savefig(chart_path, facecolor='#ffffff')
    plt.close()

def generate_bar_graph(records):
    """Generates a Professional Light-Mode Bar Graph"""
    static_dir = os.path.join('static')
    if not os.path.exists(static_dir): os.makedirs(static_dir)
    chart_path = os.path.join(static_dir, 'analytics_bar.png')
    
    if not records:
        plt.figure(figsize=(5, 4), facecolor='#ffffff')
        plt.text(0.5, 0.5, 'No Fee Data Available', color='#333333', ha='center', va='center')
        plt.axis('off')
        plt.savefig(chart_path, facecolor='#ffffff')
        plt.close()
        return

    student_ids = [r['id'] for r in records]
    total_fees = [r['total_fee'] for r in records]

    fig, ax = plt.subplots(figsize=(5, 4), facecolor='#ffffff')
    ax.set_facecolor('#ffffff')
    
    bars = ax.bar(student_ids, total_fees, color='#7209b7', edgecolor='#560bad', width=0.5)
    
    ax.tick_params(colors='#333333', labelsize=9)
    ax.xaxis.label.set_color('#333333')
    ax.yaxis.label.set_color('#333333')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cccccc')
    ax.spines['bottom'].set_color('#cccccc')
    ax.grid(axis='y', linestyle='--', alpha=0.3, color='#cccccc')
    
    plt.title("Financial Record Account Mapping (₹)", color='#333333', fontsize=12, pad=10, weight='bold')
    plt.ylabel("Total Fee Amount (INR)")
    plt.xlabel("Student Unique ID")
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(chart_path, facecolor='#ffffff')
    plt.close()

if __name__ == '__main__':
    records = load_records()
    generate_pie_chart(records)
    generate_bar_graph(records)
    app.run(debug=True, host='0.0.0.0', port=5000)
