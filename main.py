from flask import Flask, request, redirect, render_template

app = Flask(__name__)
app.config['DEBUG'] = True

tasks = []

@app.route('/', methods=['POST', 'GET'])
def index():
    '''Add each input posted from todo.html to tasks list'''

    if request.method == 'POST':
        task = request.form['task']
        if task != '':
            tasks.append(task)

    return render_template('todos.html', title="Get It Done", tasks=tasks)

app.run()