from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

users = []

@login_manager.user_loader
def load_user(user_id):
    for user in users:
        if user.id == user_id:
            return user
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data['username']
        password = data['password']
        new_user = User(id=len(users)+1, username=username, password=password)
        users.append(new_user)
        return jsonify({'message': 'User registered successfully'})
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data['username']
        password = data['password']
        user = [user for user in users if user.username == username and user.password == password]
        if user:
            login_user(user[0])
            return jsonify({'message': 'Logged in successfully'})
        return jsonify({'message': 'Invalid credentials'}), 401
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

if __name__ == '__main__':
    app.run(debug=True)


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

@app.route('/remaining_lectures/<int:subject_id>', methods=['GET'])
def remaining_lectures(subject_id):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("SELECT lectures FROM subjects WHERE id = ?", (subject_id,))
    total_lectures = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM attendance WHERE subject_id = ?", (subject_id,))
    attended_lectures = c.fetchone()[0]
    conn.close()
    remaining_lectures = total_lectures - attended_lectures
    return jsonify({'remaining_lectures': remaining_lectures})

# Add the number of lectures for a subject
@app.route('/add_lectures', methods=['POST'])
@login_required
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

@app.route('/remaining_lectures/<int:subject_id>', methods=['GET'])
@login_required
def remaining_lectures(subject_id):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("SELECT lectures FROM subjects WHERE id = ?", (subject_id,))
    total_lectures = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM attendance WHERE subject_id = ?", (subject_id,))
    attended_lectures = c.fetchone()[0]
    conn.close()
    remaining_lectures = total_lectures - attended_lectures
    return jsonify({'remaining_lectures': remaining_lectures})

@app.route('/attendance_report/<int:student_id>/<int:subject_id>', methods=['GET'])
@login_required
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


if __name__ == '__main__':
    app.run(debug=True)
