from flask import Flask, request, jsonify, abort, Response
from typing import Any
import json
import os
import uuid

app = Flask(__name__)

# garantir persistência dos dados em um arquivo JSON
DATA_DIR: str = os.getenv('DATA_DIR', 'data')
DATA_FILE: str = os.path.join(DATA_DIR, 'tasks.json')

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

TaskDict = dict[str, dict[str, Any]]

def load_tasks() -> TaskDict:
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_tasks(tasks: TaskDict) -> None:
    with open(DATA_FILE, 'w') as f:
        json.dump(tasks, f)

@app.route('/health', methods=['GET'])
def health_check() -> tuple[Response, int]:
    return jsonify({"status": "ok"}), 200

# Fazendo um CRUD completo para tarefas

@app.route('/tasks', methods=['POST'])
def create_task() -> tuple[Response, int]:
    tasks: TaskDict = load_tasks()
    task_id: str = str(uuid.uuid4())
    
    data: dict[str, Any] = request.get_json() or {}
    
    nova_tarefa: dict[str, Any] = {
        "id": task_id, 
        "title": data.get("title", "Tarefa sem título"),
        "status": data.get("status", "pendente")
    }
    
    tasks[task_id] = nova_tarefa
    save_tasks(tasks)
    return jsonify(nova_tarefa), 201

@app.route('/tasks', methods=['GET'])
def get_all_tasks() -> tuple[Response, int]:
    tasks: TaskDict = load_tasks()
    return jsonify(list(tasks.values())), 200

@app.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id: str) -> tuple[Response, int]:
    tasks: TaskDict = load_tasks()
    if task_id not in tasks:
        abort(404)
    return jsonify(tasks[task_id]), 200

@app.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id: str) -> tuple[Response, int]:
    tasks: TaskDict = load_tasks()
    if task_id not in tasks:
        abort(404)
        
    data: dict[str, Any] = request.get_json() or {}
    
    tasks[task_id]["title"] = data.get("title", tasks[task_id]["title"])
    tasks[task_id]["status"] = data.get("status", tasks[task_id]["status"])
    
    save_tasks(tasks)
    return jsonify(tasks[task_id]), 200

@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id: str) -> tuple[str, int]:
    tasks: TaskDict = load_tasks()
    if task_id not in tasks:
        abort(404) 
        
    del tasks[task_id]
    save_tasks(tasks)
    return '', 204