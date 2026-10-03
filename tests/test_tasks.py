import pytest
from app import app, db
from app.models import Task

@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_get_tasks_empty(client):
    response = client.get('/tasks')
    assert response.status_code == 200
    assert response.json == []

def test_create_task(client):
    response = client.post('/tasks', json={
        'title': 'Test Task',
        'description': 'A test task'
    })
    assert response.status_code == 201
    assert response.json['title'] == 'Test Task'
    assert response.json['id'] == 1

def test_delete_task(client):
    client.post('/tasks', json={'title': 'Task to Delete'})
    response = client.delete('/tasks/1')
    assert response.status_code == 204
    
    get_response = client.get('/tasks')
    assert len(get_response.json) == 0