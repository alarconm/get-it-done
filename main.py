from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://get-it-done:moto@localhost:8889/get-it-done'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'dillybar'

class Task(db.Model):
    '''Used to add new task objects to the database based on what user enters into form'''

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    completed = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, owner):
        self.name = name
        self.completed = False
        self.owner = owner


class User(db.Model):
    '''Create new users once they register through register form and save in database'''

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    tasks = db.relationship('Task', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password


@app.before_request
def require_login():
    '''Restrict and redirect user to register or login pages if not logged in'''

    allowed_routes = ['register', 'login']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    '''Display login page to the user'''

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged in")
            print(session)

            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

def validate_user(email, password, verify):
    '''Validate username(email address) and password entered. Return specified failure if failed'''

    if not re.match("([^@|\s]+@[^@]+\.[^@|\s]+)", email):
        return 'email'
    if len(password) >= 3 and len(password) <= 20:
        if re.search(r'\s', password):
            return 'password'
    else:
        return 'password'
    if verify != password:
        return 'verify'


@app.route('/register', methods=['POST', 'GET'])
def register():
    '''Display registration page to the user'''

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
    
        if validate_user(email, password, verify):
            if validate_user(email, password, verify) == 'email':
                flash('Not a valid email address', 'error')
            if validate_user(email, password, verify) == 'password':
                flash('Not a valid password, please enter a password between 3 and 20 characters long', 'error')
            if validate_user(email, password, verify) == 'verify':
                flash('Your passwords did not match', 'error')
            return render_template('register.html', email=email)

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email

            return redirect('/')
        else:
            flash('That username is already in use, please choose a different name', 'error')

    return render_template('register.html')


@app.route('/', methods=['POST', 'GET'])
def index():
    '''Add each input posted from todo.html to tasks list'''

    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        task_name = request.form['task']
        new_task = Task(task_name, owner)
        db.session.add(new_task)
        db.session.commit()

    tasks = Task.query.filter_by(completed=False, owner=owner).all()
    completed_tasks = Task.query.filter_by(completed=True, owner=owner).all()

    return render_template('todos.html', title="Get It Done", tasks=tasks,
                           completed_tasks=completed_tasks)


@app.route('/logout')
def logout():
    '''delete user email from the session and redirect to homepage'''
    del session['email']
    return redirect('/')


@app.route('/delete-task', methods=['POST'])
def delete_task():
    '''Delete selected task from the database when the user clicks the button, then
    return user to the index page'''

    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    task.completed = True
    db.session.add(task)
    db.session.commit()

    return redirect('/')


if __name__ == '__main__':
    app.run()