from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Route to add a student
@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.get_json()
    name = data['name']
    contact = data['contact']
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("INSERT INTO students (name, contact) VALUES (?, ?)", (name, contact))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Student added successfully'})

# Route to update student information
@app.route('/update_student/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json()
    name = data['name']
    contact = data['contact']
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("UPDATE students SET name = ?, contact = ? WHERE id = ?", (name, contact, id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Student updated successfully'})

# Route to delete a student
@app.route('/delete_student/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Student deleted successfully'})

# Route to add a subject
@app.route('/add_subject', methods=['POST'])
def add_subject():
    data = request.get_json()
    name = data['name']
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Subject added successfully'})

# Route to record attendance
@app.route('/record_attendance', methods=['POST'])
def record_attendance():
    data = request.get_json()
    student_id = data['student_id']
    subject_id = data['subject_id']
    lecture_date = data['lecture_date']
    status = data['status']
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("INSERT INTO attendance (student_id, subject_id, lecture_date, status) VALUES (?, ?, ?, ?)",
              (student_id, subject_id, lecture_date, status))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Attendance recorded successfully'})

# Route to get attendance records for a student
@app.route('/attendance/<int:student_id>', methods=['GET'])
def get_attendance(student_id):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("SELECT * FROM attendance WHERE student_id = ?", (student_id,))
    records = c.fetchall()
    conn.close()
    return jsonify(records)

# Route to generate attendance report
@app.route('/attendance_report/<int:student_id>/<int:subject_id>', methods=['GET'])
def attendance_report(student_id, subject_id):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM attendance WHERE student_id = ? AND subject_id = ? AND status = 'Present'",
              (student_id, subject_id))
    present_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM attendance WHERE student_id = ? AND subject_id = ?",
              (student_id, subject_id))
    total_count = c.fetchone()[0]
    conn.close()
    attendance_percentage = (present_count / total_count) * 100 if total_count > 0 else 0
    status = 'Below 75%' if attendance_percentage < 75 else 'Satisfactory'
    return jsonify({'attendance_percentage': attendance_percentage, 'status': status})

# Add number of lectures for a subject
@app.route('/add_lectures', methods=['POST'])
def add_lectures():
    data = request.get_json()
    subject_id = data['subject_id']
    lectures = data['lectures']
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("UPDATE subjects SET lectures = ? WHERE id = ?", (lectures, subject_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Lectures added successfully'})

if __name__ == '__main__':
    app.run(debug=True)
