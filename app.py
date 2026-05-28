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
        "total_fee": base_fee + amenities_fee
    }
    
    records.append(new_student)
    save_records(records)
    
    # Generate both updated visual assets
    generate_pie_chart(records)
    generate_bar_graph(records)
    return jsonify({"success": True})

@app.route('/api/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    records = load_records()
    updated_records = [r for r in records if r['id'] != student_id]
    save_records(updated_records)
    
    # Refresh both visual assets
    generate_pie_chart(updated_records)
    generate_bar_graph(updated_records)
    return jsonify({"success": True})

def generate_pie_chart(records):
    """Generates a Dark-Mode Pie Chart for Tier Distribution"""
    static_dir = os.path.join('static')
    if not os.path.exists(static_dir): os.makedirs(static_dir)
    chart_path = os.path.join(static_dir, 'analytics_pie.png')
    
    if not records:
        plt.figure(figsize=(5, 4), facecolor='#0f0f1a')
        plt.text(0.5, 0.5, 'No Tier Data Available', color='white', ha='center', va='center')
        plt.axis('off')
        plt.savefig(chart_path, facecolor='#0f0f1a')
        plt.close()
        return

    tier_counts = {"Regular": 0, "Scholar": 0}
    for r in records:
        if r['tier'] in tier_counts: tier_counts[r['tier']] += 1

    labels = list(tier_counts.keys())
    sizes = list(tier_counts.values())
    if sum(sizes) == 0: sizes = [1, 1]

    colors = ['#9d4edd', '#00f5d4']
    fig, ax = plt.subplots(figsize=(5, 4), facecolor='#0f0f1a')
    ax.set_facecolor('#0f0f1a')
    
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors, textprops=dict(color="w"))
    for autotext in autotexts:
        autotext.set_color('black')
        autotext.set_weight('bold')

    plt.title("Student Tier Distribution Matrix", color='white', fontsize=12, pad=10)
    plt.tight_layout()
    plt.savefig(chart_path, facecolor='#0f0f1a')
    plt.close()

def generate_bar_graph(records):
    """Generates a Dark-Mode Bar Graph mapping Total Fees per Student ID"""
    static_dir = os.path.join('static')
    if not os.path.exists(static_dir): os.makedirs(static_dir)
    chart_path = os.path.join(static_dir, 'analytics_bar.png')
    
    if not records:
        plt.figure(figsize=(5, 4), facecolor='#0f0f1a')
        plt.text(0.5, 0.5, 'No Fee Data Available', color='white', ha='center', va='center')
        plt.axis('off')
        plt.savefig(chart_path, facecolor='#0f0f1a')
        plt.close()
        return

    student_ids = [r['id'] for r in records]
    total_fees = [r['total_fee'] for r in records]

    fig, ax = plt.subplots(figsize=(5, 4), facecolor='#0f0f1a')
    ax.set_facecolor('#0f0f1a')
    
    # Draw glowing neon pink/magenta bars
    bars = ax.bar(student_ids, total_fees, color='#ff007f', edgecolor='#ff75c3', width=0.5)
    
    # Style text parameters, grids, and boundaries
    ax.tick_params(colors='white', labelsize=9)
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#444')
    ax.spines['bottom'].set_color('#444')
    ax.grid(axis='y', linestyle='--', alpha=0.1, color='white')
    
    plt.title("Financial Record Account Mapping (₹)", color='white', fontsize=12, pad=10)
    plt.ylabel("Total Fee Amount (INR)")
    plt.xlabel("Student Unique UID")
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(chart_path, facecolor='#0f0f1a')
    plt.close()

if __name__ == '__main__':
    records = load_records()
    generate_pie_chart(records)
    generate_bar_graph(records)
    app.run(debug=True, host='0.0.0.0', port=5000)
