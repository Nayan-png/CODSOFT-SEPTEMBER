from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"
TASKS_FILE = "tasks.json"

# ======================= Helper Functions ======================= #
def load_tasks():
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

def reassign_ids(tasks):
    for idx, task in enumerate(tasks, start=1):
        task["id"] = idx
    return tasks

# ======================= Flask Routes ======================= #
@app.route("/", methods=["GET"])
def index():
    tasks = load_tasks()
    status_filter = request.args.get("status", "All")
    search_query = request.args.get("search", "").strip()
    
    if status_filter != "All":
        tasks = [t for t in tasks if t["status"]==status_filter]
    if search_query:
        tasks = [t for t in tasks if search_query.lower() in t["title"].lower() or search_query.lower() in t["description"].lower()]
    
    total = len(load_tasks())
    completed = len([t for t in load_tasks() if t["status"]=="Completed"])
    pending = total - completed
    completion_rate = int((completed/total)*100) if total>0 else 0
    
    return render_template_string(TEMPLATE, tasks=tasks, search_query=search_query, 
                                  status_filter=status_filter, total=total, completed=completed,
                                  pending=pending, completion_rate=completion_rate)

@app.route("/add", methods=["POST"])
def add_task():
    tasks = load_tasks()
    title = request.form.get("title").strip()
    description = request.form.get("description").strip()
    priority = request.form.get("priority", "Medium")
    if not title:
        flash("Task title cannot be empty!", "danger")
        return redirect(url_for("index"))
    task = {
        "id": len(tasks)+1,
        "title": title,
        "description": description,
        "priority": priority,
        "status": "Pending",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "completed_at": None
    }
    tasks.append(task)
    save_tasks(tasks)
    flash(f"Task '{title}' added successfully!", "success")
    return redirect(url_for("index"))

@app.route("/update/<int:task_id>", methods=["POST"])
def update_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            title = request.form.get(f"title_{task_id}").strip()
            description = request.form.get(f"description_{task_id}").strip()
            priority = request.form.get(f"priority_{task_id}", "Medium")
            task["title"] = title
            task["description"] = description
            task["priority"] = priority
            break
    save_tasks(tasks)
    flash(f"Task #{task_id} updated successfully!", "success")
    return redirect(url_for("index"))

@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task["id"]==task_id:
            task["status"]="Completed"
            task["completed_at"]=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            break
    save_tasks(tasks)
    flash(f"Task #{task_id} marked as completed!", "success")
    return redirect(url_for("index"))

@app.route("/delete", methods=["POST"])
def delete_task():
    selected_ids = request.form.getlist("task_ids")
    if not selected_ids:
        flash("Select at least one task to delete!", "warning")
        return redirect(url_for("index"))
    tasks = load_tasks()
    tasks = [t for t in tasks if str(t["id"]) not in selected_ids]
    tasks = reassign_ids(tasks)
    save_tasks(tasks)
    flash(f"Deleted {len(selected_ids)} task(s) successfully!", "success")
    return redirect(url_for("index"))

@app.route("/reorder", methods=["POST"])
def reorder_tasks():
    order = request.json.get("order", [])
    tasks = load_tasks()
    tasks_dict = {str(t["id"]): t for t in tasks}
    new_tasks = [tasks_dict[str(i)] for i in order if str(i) in tasks_dict]
    new_tasks = reassign_ids(new_tasks)
    save_tasks(new_tasks)
    return jsonify({"status":"success"})

# ======================= HTML Template ======================= #
TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Todo Dashboard</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body {background-color:#f8f9fa;}
.completed {text-decoration: line-through; color: gray;}
.priority-High {color:#ff4d4f; font-weight:bold;}
.priority-Medium {color:#faad14;}
.priority-Low {color:#52c41a;}
input.inline-edit {width: 100%;}
</style>
</head>
<body>
<div class="container mt-4">
    <h1 class="text-center mb-4">🚀Todo Dashboard</h1>

    <!-- Dashboard Cards -->
    <div class="row mb-4">
        <div class="col-md-3"><div class="card text-center bg-light"><div class="card-body"><h5>Total Tasks</h5><h3>{{total}}</h3></div></div></div>
        <div class="col-md-3"><div class="card text-center bg-success text-white"><div class="card-body"><h5>Completed</h5><h3>{{completed}}</h3></div></div></div>
        <div class="col-md-3"><div class="card text-center bg-warning text-dark"><div class="card-body"><h5>Pending</h5><h3>{{pending}}</h3></div></div></div>
        <div class="col-md-3"><div class="card text-center bg-info text-white"><div class="card-body"><h5>Completion Rate</h5><h3>{{completion_rate}}%</h3></div></div></div>
    </div>

    <!-- Add Task Form -->
    <form method="POST" action="{{ url_for('add_task') }}" class="row g-2 mb-4">
        <div class="col-md-3"><input type="text" class="form-control" name="title" placeholder="Task Title" required></div>
        <div class="col-md-4"><input type="text" class="form-control" name="description" placeholder="Description"></div>
        <div class="col-md-2">
            <select class="form-select" name="priority">
                <option value="High">High</option>
                <option value="Medium" selected>Medium</option>
                <option value="Low">Low</option>
            </select>
        </div>
        <div class="col-md-3"><button type="submit" class="btn btn-success w-100">Add Task</button></div>
    </form>

    <!-- Filters -->
    <div class="mb-3">
        <a href="{{ url_for('index', status='All') }}" class="btn btn-outline-primary {% if status_filter=='All' %}active{% endif %}">All</a>
        <a href="{{ url_for('index', status='Pending') }}" class="btn btn-outline-warning {% if status_filter=='Pending' %}active{% endif %}">Pending</a>
        <a href="{{ url_for('index', status='Completed') }}" class="btn btn-outline-success {% if status_filter=='Completed' %}active{% endif %}">Completed</a>
    </div>

    <!-- Task Table -->
    <form method="POST" action="{{ url_for('delete_task') }}">
    <div class="mb-3 text-end">
        <button type="submit" class="btn btn-danger">Delete Selected</button>
    </div>
    <table class="table table-hover table-bordered" id="taskTable">
        <thead class="table-dark">
            <tr>
                <th><input type="checkbox" id="selectAll"></th>
                <th>ID</th>
                <th>Title</th>
                <th>Description</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Created</th>
                <th>Completed</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody id="sortable">
            {% for task in tasks %}
            <tr class="{{ 'completed' if task.status=='Completed' }}">
                <td><input type="checkbox" name="task_ids" value="{{task.id}}"></td>
                <td>{{task.id}}</td>
                <td>
                    <form method="POST" action="{{ url_for('update_task', task_id=task.id) }}">
                        <input type="text" name="title_{{task.id}}" class="inline-edit" value="{{task.title}}">
                </td>
                <td><input type="text" name="description_{{task.id}}" class="inline-edit" value="{{task.description}}"></td>
                <td>
                    <select name="priority_{{task.id}}" class="form-select form-select-sm">
                        <option value="High" {% if task.priority=='High' %}selected{% endif %}>High</option>
                        <option value="Medium" {% if task.priority=='Medium' %}selected{% endif %}>Medium</option>
                        <option value="Low" {% if task.priority=='Low' %}selected{% endif %}>Low</option>
                    </select>
                </td>
                <td>{{task.status}}</td>
                <td>{{task.created_at}}</td>
                <td>{{task.completed_at or ''}}</td>
                <td>
                    <button type="submit" class="btn btn-sm btn-primary mb-1">Save</button>
                    {% if task.status != 'Completed' %}
                    <a href="{{ url_for('complete_task', task_id=task.id) }}" class="btn btn-sm btn-success mb-1">Complete</a>
                    {% endif %}
                </td>
                </form>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    </form>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"></script>
<script>
document.getElementById("selectAll").addEventListener("change", function(){
    document.querySelectorAll('input[name="task_ids"]').forEach(cb => cb.checked = this.checked);
});

// Drag-and-drop reordering
new Sortable(document.getElementById("sortable"), {
    animation: 150,
    handle: ".drag-handle",
    onEnd: function (evt) {
        let order = Array.from(document.querySelectorAll("#sortable tr")).map(row => row.children[1].textContent);
        fetch("{{ url_for('reorder_tasks') }}", {
            method:"POST",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify({order: order})
        });
    }
});
</script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
