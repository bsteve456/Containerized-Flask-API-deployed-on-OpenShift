import pytest
from app.main import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    """Test GET /health returns 200"""
    response = client.get('/health')
    assert response.status_code == 200


def test_get_tasks_empty(client):
    """Test GET /tasks returns empty list initially"""
    response = client.get('/tasks')
    assert response.status_code == 200
    assert response.json == []


def test_create_task(client):
    """Test POST /tasks creates a new task"""
    new_task = {'title': 'Buy milk'}
    response = client.post('/tasks', json=new_task)
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['title'] == 'Buy milk'


def test_delete_task(client):
    """Test DELETE /tasks/{id} deletes a task"""
    # First, create a task
    new_task = {'title': 'Buy milk'}
    create_response = client.post('/tasks', json=new_task)
    task_id = create_response.json['id']
    
    # Then delete it
    delete_response = client.delete(f'/tasks/{task_id}')
    assert delete_response.status_code == 204