from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

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

    def __init__(self, name):
        self.name = name
        self.completed = False


class User(db.Model):
    '''Create new users once they register through register form and save in database'''

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))

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

            return redirect('/')
        else:
# TODO - explain why the login failed
            pass

    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    '''Display registration page to the user'''

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

#TODO - add validation

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email

            return redirect('/')
        else:
# TODO - user response messaging
            return '<h1>Duplicate user</h1>'


    return render_template('register.html')


@app.route('/', methods=['POST', 'GET'])
def index():
    '''Add each input posted from todo.html to tasks list'''

    if request.method == 'POST':
        task_name = request.form['task']
        if task_name:
            new_task = Task(task_name)
            db.session.add(new_task)
            db.session.commit()
    
    tasks = Task.query.filter_by(completed=False).all()
    completed_tasks = Task.query.filter_by(completed=True).all()

    return render_template('todos.html', title="Get It Done", tasks=tasks,
                           completed_tasks=completed_tasks)

@app.route('/logout')
def lougout():
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