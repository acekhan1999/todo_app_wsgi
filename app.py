from wsgiref.simple_server import make_server
import urllib.parse
import db
from datetime import datetime
from jinja2 import Template
from bson.objectid import ObjectId

userID = ""
fullname = ""

def render_template(template_name = "index.html", context={}):
    htmlstr = ""

    with open(template_name, "r") as f:
        htmlstr = f.read()
        htmlstr = htmlstr.format(**context)

    return htmlstr

def form_data_handler(page_route, data):
    global userID
    global fullname

    if page_route == "/":
        user_fullname = data['user_fullname'][0]
        username = data['username'][0]
        password = data['password'][0]

        new_user = {"user_fullname" : user_fullname, "username" : username, "password" : password}
        db.insert_user(new_user)

        user = db.get_user(username, password)

        userID = user['_id']
        fullname = user['user_fullname']

    elif page_route == "/todo":
        todo_subject = data['todo_subject'][0]
        todo_desc = data['todo_desc'][0]
        due_date = data['due_date'][0]
        due_date = datetime.strptime(due_date, "%Y-%m-%d")
        
        try:
            priority = bool(data['priority'][0])
        
        except KeyError:
            priority = False

        new_todo = {"todo_subject" : todo_subject, "todo_desc" : todo_desc, "due_date" : due_date, "priority" : priority, "completed" : False, "userID" : userID}

        db.insert_todo(new_todo)

    elif page_route == "/login":
        username = data['username'][0]
        password = data['password'][0]

        user = db.get_user(username, password)

        try:
            userID = user['_id']
            fullname = user['user_fullname']
        except TypeError:
            userID = ""
            fullname = ""


def home(environment):
    path = environment.get("PATH_INFO")

    if environment.get("REQUEST_METHOD") == "POST":
        data = check_form_data(environment)
        form_data_handler(path, data)

    return render_template(
        template_name="index.html", 
        context={"fullname":fullname,"userID":userID}
    )

def todo(environment):
    path = environment.get("PATH_INFO")

    if environment.get("REQUEST_METHOD") == "POST":
        data = check_form_data(environment)
        form_data_handler(path, data)

    return render_template(
        template_name="todo.html", 
        context={"fullname":fullname}
    )

def check_form_data(environment):
    data = ""
    
    try:
        length= int(environment.get('CONTENT_LENGTH', '0'))
    except ValueError:
        length= 0

    if length!=0:
        data = urllib.parse.parse_qs(environment['wsgi.input'].read(length).decode(),True)

    return data

def login(environment):
    path = environment.get("PATH_INFO")

    if environment.get("REQUEST_METHOD") == "POST":
        data = check_form_data(environment)
        form_data_handler(path, data)
    
    return render_template(
        template_name="login.html", 
        context={}
    )

def delete_todo(environment):
    path = environment.get("PATH_INFO")
    todoID = environment.get("QUERY_STRING")

    db.remove_todo(todoID)
    view_todo(environment)

def mark_completed(environment):
    path = environment.get("PATH_INFO")
    todoID = environment.get("QUERY_STRING")

    db.update_todo(todoID)
    view_todo(environment)

def update_todo(environment):
    global userID

    path = environment.get("PATH_INFO")
    todoID = environment.get("QUERY_STRING")

    user_todo = db.get_user_todo(todoID)

    update_template = f'''
    <form action="/update_todo/todo_id?{todoID}" enctype="application/x-www-form-urlencoded" method="post">
        <input type="text" name="todo_subject" value="{user_todo['todo_subject']}" placeholder="Enter todo subject...">
        <textarea name="todo_desc" id="todo_desc" cols="30" rows="10">{user_todo['todo_desc']}</textarea>
        <label for="due_date">Due Date</label>
        <input type="date" name="due_date" id="due_date" value="{user_todo['due_date'].date()}">
        {{% if {user_todo['priority']} == True: %}}
        <input type="checkbox" name="priority" value="True" checked>
        {{% else %}}
        <input type="checkbox" name="priority" value="True">
        {{% endif %}}
        <label for="priority">Priority</label>
        <input type="submit" value="Update Todo">
    </form>
    '''

    if environment.get("REQUEST_METHOD") == "POST":
        data = check_form_data(environment)
        
        todo_subject = data['todo_subject'][0]
        todo_desc = data['todo_desc'][0]
        due_date = data['due_date'][0]
        due_date = datetime.strptime(due_date, "%Y-%m-%d")

        try:
            priority = bool(data['priority'][0])
        
        except KeyError:
            priority = False

        todo = {
            "_id":  ObjectId(todoID),
            "todo_subject":  todo_subject,
            "todo_desc"   :  todo_desc,
            "due_date"    :  due_date,
            "priority"    :  priority,
            "completed"    :  False,
            "userID"      :  userID,
        } #make a todo dict from POST data

        db.remove_todo(todoID)
        db.insert_todo(todo)

    update_todo_template = Template(update_template).render()
    
    return render_template(
        template_name="update_todo.html", 
        context={"update_todo_template":update_todo_template}
    )

def view_todo(environment):
    global userID, fullname
    path = environment.get("PATH_INFO")

    todos = db.get_todos(userID)

    if userID == "":
        s = '''
        no user found
        <a href="/login">Please Try Logging in Again.</a> 
        '''
    else:
        s = '''    
        <a href="/todo">Create New Todo</a>
        {% for element in elements %}
        <h1>{{element['todo_subject']}}</h1>
        <p>{{element['todo_desc']}}</p>
        <p>Due Date: {{element['due_date']}} </p>
        <p>Priority: {{element['priority']}} </p>
        <p>Completed: {{element['completed']}} </p>

        <a href="/update_todo/todo_id?{{element['_id']}}">Update Todo</a>
        <a href="/delete_todo/todo_id?{{element['_id']}}">Delete Todo</a>
        {% if element['completed'] == False %}
        <a href="/mark_completed/todo_id?{{element['_id']}}">Mark Completed</a>
        {% endif %}
        <hr/>
        {% endfor %}
        '''

    todo = Template(s).render(elements=todos)

    
    return render_template(
        template_name="view_todo.html", 
        context={"todo":todo, "fullname":fullname}
    )

def web_app(environment, response):

    path = environment.get("PATH_INFO")

    # rendering templates based on paths

    if path == "/":
        data = home(environment)
        if environment.get("REQUEST_METHOD") == "POST":
            data = view_todo(environment)

    elif path == "/todo":
        data = todo(environment)
        if environment.get("REQUEST_METHOD") == "POST":
            data = view_todo(environment)

    elif path == "/login":
        data = login(environment)
        if environment.get("REQUEST_METHOD") == "POST":
            data = view_todo(environment)

    elif path == "/view_todo":
        data = view_todo(environment)

    elif path == "/update_todo/todo_id":
        data = update_todo(environment)
        if environment.get("REQUEST_METHOD") == "POST":
            data = view_todo(environment)

    elif path == "/delete_todo/todo_id":
        delete_todo(environment)
        data = view_todo(environment)

    elif path == "/mark_completed/todo_id":
        mark_completed(environment)
        data = view_todo(environment)

    else:
        data = render_template(template_name="404.html", context={"path":path})

    status = "200 OK"
    
    data=data.encode("utf-8")
    headers = [("Content-Type", "text/html; charset=utf-8")]

    response(status, headers)

    return [data]

with make_server("", 8000, web_app) as server:
    print(f"serving on port 8000...\nvisit http://127.0.0.1:8000\nto kill the server ENTER 'Ctrl+C'")

    # server forever, until we kill it or kills itself because of an error
    server.serve_forever()