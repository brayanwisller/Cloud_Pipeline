import pytest
import os
from flask.testing import FlaskClient
from app.main import app, DATA_FILE

@pytest.fixture
def client():
    app.config['TESTING'] = True
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    with app.test_client() as client:
        yield client

def test_health_check(client: FlaskClient):
    response = client.get('/health')
    assert response.status_code == 200

def test_crud_flow(client: FlaskClient):
    """Testa o fluxo completo de Create, Read e Update"""

    # CREATE (POST)
    create_resp = client.post('/tasks', json={"title": "Comprar pão de queijo", "status": "pendente"})
    assert create_resp.status_code == 201
    task_id = create_resp.get_json()["id"]
    
    # READ ALL (GET /tasks)
    get_all_resp = client.get('/tasks')
    assert get_all_resp.status_code == 200
    assert len(get_all_resp.get_json()) == 1

    # READ SINGLE (GET /tasks/<id>)
    get_single_resp = client.get(f'/tasks/{task_id}')
    assert get_single_resp.status_code == 200
    assert get_single_resp.get_json()["title"] == "Comprar pão de queijo"
    
    # UPDATE (PUT)
    update_resp = client.put(f'/tasks/{task_id}', json={"status": "concluido"})
    assert update_resp.status_code == 200
    assert update_resp.get_json()["status"] == "concluido"

def test_delete_task_success(client: FlaskClient):
    """Teste 1 do DELETE: Apagar com sucesso"""
    create_resp = client.post('/tasks', json={"title": "Tarefa temporária"})
    task_id = create_resp.get_json()["id"]

    delete_resp = client.delete(f'/tasks/{task_id}')
    assert delete_resp.status_code == 204

def test_delete_task_not_found(client: FlaskClient):
    """Teste 2 do DELETE: Retornar 404 se não existir"""
    delete_resp = client.delete('/tasks/id-falso-inexistente')
    assert delete_resp.status_code == 404

def test_update_task_not_found(client: FlaskClient):
    """Teste extra: Retornar 404 ao tentar atualizar tarefa inexistente"""
    update_resp = client.put('/tasks/id-falso-inexistente', json={"title": "Novo"})
    assert update_resp.status_code == 404