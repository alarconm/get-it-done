from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://get-it-done:moto@localhost:8889/get-it-done'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Task(db.Model):
    '''Used to add new task objects to the database based on what user enters into form'''

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))

    def __init__(self, name):
        self.name = name


@app.route('/', methods=['POST', 'GET'])
def index():
    '''Add each input posted from todo.html to tasks list'''

    if request.method == 'POST':
        task_name = request.form['task']
        if task_name != '':
            new_task = Task(task_name)
            db.session.add(new_task)
            db.session.commit()
    
    tasks = Task.query.all()

    return render_template('todos.html', title="Get It Done", tasks=tasks)

@app.route('/delete-task', methods=['POST'])
def delete_task():
    '''Delete selected task from the database when the user clicks the button, then
    return user to the index page'''

    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    db.session.delete(task)
    db.session.commit()

    return redirect('/')


if __name__ == '__main__':
    app.run()