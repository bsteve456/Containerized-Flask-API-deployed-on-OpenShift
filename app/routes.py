from flask import jsonify, request
from app.main import app
from app.models import tasks_db, Task

next_id = 1

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


@app.route('/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks"""
    tasks_list = [task.to_dict() for task in tasks_db.values()]
    return jsonify(tasks_list), 200


@app.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    global next_id
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'title required'}), 400
    
    task = Task(next_id, data['title'])
    tasks_db[next_id] = task
    next_id += 1
    
    return jsonify(task.to_dict()), 201


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    if task_id not in tasks_db:
        return jsonify({'error': 'task not found'}), 404
    
    del tasks_db[task_id]
    return '', 204