from flask import Flask, render_template, redirect, url_for, request, jsonify
import mysql.connector

app = Flask(__name__)

# Configure MySQL connection
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root', 
        database='myfinal'
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
        
        return redirect(url_for('home'))
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
        
        cursor.execute("SELECT * FROM students WHERE name LIKE %s OR year LIKE %s", 
                       ('%' + search_query + '%', '%' + search_query + '%'))
        students = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return render_template('index.html', students=students)

    return redirect(url_for('home')) 


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

if __name__ == '__main__':
    app.run(debug=True)
