from flask import Flask, render_template, redirect, url_for, request, jsonify
import mysql.connector

app = Flask(__name__)

# Configure MySQL connection
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',       # Change if your MySQL is on a different host
        user='root',           # Your MySQL username
        password='root',       # Your MySQL password
        database='myfinal'     # Your database name
    )
    return connection

@app.route('/')
def home():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('index.html', students=students)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        year = request.form['year']
        
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            'INSERT INTO students (name, email, year) VALUES (%s, %s, %s)',
            (name, email, year)
        )
        connection.commit()
        cursor.close()
        connection.close()
        
        return redirect(url_for('home'))  # Redirect to the home page after adding
    return render_template('add_student.html')

@app.route('/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        year = request.form['year']
        cursor.execute(
            'UPDATE students SET name = %s, email = %s, year = %s WHERE id = %s',
            (name, email, year, student_id)
        )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect('/')
    else:
        cursor.execute('SELECT * FROM students WHERE id = %s', (student_id,))
        student = cursor.fetchone()
        cursor.close()
        connection.close()
        return render_template('edit_student.html', student=student)

@app.route('/delete/<int:student_id>')
def delete_student(student_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM students WHERE id = %s', (student_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect('/')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form['search']
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        # Search for students by name or email
        cursor.execute("SELECT * FROM students WHERE name LIKE %s OR email LIKE %s", 
                       ('%' + search_query + '%', '%' + search_query + '%'))
        students = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('index.html', students=students)

    return redirect(url_for('home'))  # Redirect to home if it's a GET request

# REST API for students
@app.route('/api/students', methods=['GET'])
def get_students():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(students)

@app.route('/api/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM students WHERE id = %s', (student_id,))
    student = cursor.fetchone()
    cursor.close()
    connection.close()
    if student:
        return jsonify(student)
    else:
        return jsonify({'error': 'Student not found'}), 404

@app.route('/api/students', methods=['POST'])
def create_student():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    year = data.get('year')
    
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        'INSERT INTO students (name, email, year) VALUES (%s, %s, %s)',
        (name, email, year)
    )
    connection.commit()
    cursor.close()
    connection.close()
    
    return jsonify({'message': 'Student created successfully'}), 201

@app.route('/api/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.json
    name = data.get('name')
    email = data.get('email')
    year = data.get('year')
    
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        'UPDATE students SET name = %s, email = %s, year = %s WHERE id = %s',
        (name, email, year, student_id)
    )
    connection.commit()
    cursor.close()
    connection.close()
    
    return jsonify({'message': 'Student updated successfully'})

@app.route('/api/students/<int:student_id>', methods=['DELETE'])
def delete_student_api(student_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM students WHERE id = %s', (student_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({'message': 'Student deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)
