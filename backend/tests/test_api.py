import pytest
from app import create_app, db
from app.models import User, Product

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'version' in data

def test_ready_check(client):
    """Test ready check endpoint"""
    response = client.get('/api/ready')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ready'

def test_create_user(client):
    """Test creating a user"""
    response = client.post('/api/users', json={
        'username': 'testuser',
        'email': 'test@example.com'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['username'] == 'testuser'
    assert data['email'] == 'test@example.com'

def test_get_users(client):
    """Test getting all users"""
    # Create a user first
    client.post('/api/users', json={
        'username': 'testuser',
        'email': 'test@example.com'
    })
    
    response = client.get('/api/users')
    assert response.status_code == 200
    data = response.get_json()
    assert 'users' in data
    assert len(data['users']) > 0

def test_get_user(client):
    """Test getting a specific user"""
    # Create a user
    create_response = client.post('/api/users', json={
        'username': 'testuser',
        'email': 'test@example.com'
    })
    user_id = create_response.get_json()['id']
    
    response = client.get(f'/api/users/{user_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == user_id

def test_delete_user(client):
    """Test deleting a user"""
    # Create a user
    create_response = client.post('/api/users', json={
        'username': 'testuser',
        'email': 'test@example.com'
    })
    user_id = create_response.get_json()['id']
    
    response = client.delete(f'/api/users/{user_id}')
    assert response.status_code == 200
    
    # Verify deletion
    get_response = client.get(f'/api/users/{user_id}')
    assert get_response.status_code == 404

def test_create_product(client):
    """Test creating a product"""
    response = client.post('/api/products', json={
        'name': 'Test Product',
        'description': 'A test product',
        'price': 29.99,
        'stock': 100
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'Test Product'
    assert data['price'] == 29.99

def test_get_products(client):
    """Test getting all products"""
    # Create a product
    client.post('/api/products', json={
        'name': 'Test Product',
        'price': 29.99
    })
    
    response = client.get('/api/products')
    assert response.status_code == 200
    data = response.get_json()
    assert 'products' in data

def test_update_product(client):
    """Test updating a product"""
    # Create a product
    create_response = client.post('/api/products', json={
        'name': 'Test Product',
        'price': 29.99
    })
    product_id = create_response.get_json()['id']
    
    # Update it
    response = client.put(f'/api/products/{product_id}', json={
        'name': 'Updated Product',
        'price': 39.99
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Updated Product'
    assert data['price'] == 39.99

def test_get_stats(client):
    """Test stats endpoint"""
    response = client.get('/api/stats')
    assert response.status_code == 200
    data = response.get_json()
    assert 'users' in data
    assert 'products' in data
