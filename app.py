from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector

app = Flask(__name__)
app.secret_key = "super_secret_key" 

# Database Configuration
db_config = {
    'host': "localhost",
    'user': "root",
    'password': "vaniya", 
    'database': "todo_app"
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# --- ROUTES ---

# 1. REGISTER ROUTE (Uses register.html)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Insert new user
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                           (username, email, password))
            conn.commit()
            conn.close()
            return redirect('/login') # Go to login after success
        except mysql.connector.Error as err:
            return f"Error: {err}"

    return render_template('register.html')

# 2. LOGIN ROUTE (Uses login.html)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password') # In a real app, you should hash this!

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Check if user exists
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect('/')
        else:
            return "Invalid username or password"

    return render_template('login.html')

# 3. DASHBOARD / HOME (Uses index.html)
@app.route('/')
@app.route('/dashboard')
def home():
    if 'user_id' not in session:
        return redirect('/login')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Get tasks ONLY for the logged-in user
    cursor.execute("SELECT * FROM tasks WHERE user_id = %s", (session['user_id'],))
    tasks = cursor.fetchall()
    conn.close()
    
    return render_template('index.html', tasks=tasks, username=session['username'])

# 4. ADD TASK ROUTE (Uses add_task.html)
@app.route('/add', methods=['GET', 'POST'])
def add_task():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        due_date = request.form.get('due_date')
        priority = request.form.get('priority')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (user_id, title, description, due_date, priority, status) VALUES (%s, %s, %s, %s, %s, 'Pending')",
            (session['user_id'], title, description, due_date, priority)
        )
        conn.commit()
        conn.close()
        return redirect('/')
    
    # If method is GET, show the form
    return render_template('add_task.html')

# 5. ACTIONS (Complete/Delete/Logout)
@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = 'Completed' WHERE id = %s", (task_id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)