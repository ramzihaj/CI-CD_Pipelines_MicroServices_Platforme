from flask import Blueprint, jsonify, request
from app import db, redis_client
from app.models import User, Product
import json
import time

api_bp = Blueprint('api', __name__)

# Health check endpoint
@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Kubernetes probes"""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
    
    # Check Redis connection
    redis_status = 'healthy' if redis_client and redis_client.ping() else 'unavailable'
    
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'database': db_status,
        'redis': redis_status,
        'version': '1.0.0'
    }), 200

# Ready check endpoint
@api_bp.route('/ready', methods=['GET'])
def ready_check():
    """Readiness check endpoint"""
    try:
        db.session.execute('SELECT 1')
        return jsonify({'status': 'ready'}), 200
    except Exception:
        return jsonify({'status': 'not ready'}), 503

# Users endpoints
@api_bp.route('/users', methods=['GET'])
def get_users():
    """Get all users with optional caching"""
    cache_key = 'users:all'
    
    # Try to get from cache
    if redis_client:
        cached = redis_client.get(cache_key)
        if cached:
            return jsonify({
                'users': json.loads(cached),
                'cached': True
            }), 200
    
    # Get from database
    users = User.query.all()
    users_data = [user.to_dict() for user in users]
    
    # Cache for 5 minutes
    if redis_client:
        redis_client.setex(cache_key, 300, json.dumps(users_data))
    
    return jsonify({
        'users': users_data,
        'cached': False
    }), 200

@api_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID"""
    cache_key = f'user:{user_id}'
    
    # Try cache
    if redis_client:
        cached = redis_client.get(cache_key)
        if cached:
            return jsonify(json.loads(cached)), 200
    
    user = User.query.get_or_404(user_id)
    user_data = user.to_dict()
    
    # Cache
    if redis_client:
        redis_client.setex(cache_key, 300, json.dumps(user_data))
    
    return jsonify(user_data), 200

@api_bp.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email'):
        return jsonify({'error': 'Username and email are required'}), 400
    
    # Check if user exists
    existing_user = User.query.filter(
        (User.username == data['username']) | (User.email == data['email'])
    ).first()
    
    if existing_user:
        return jsonify({'error': 'User already exists'}), 409
    
    user = User(
        username=data['username'],
        email=data['email']
    )
    
    db.session.add(user)
    db.session.commit()
    
    # Invalidate cache
    if redis_client:
        redis_client.delete('users:all')
    
    return jsonify(user.to_dict()), 201

@api_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    # Invalidate cache
    if redis_client:
        redis_client.delete('users:all')
        redis_client.delete(f'user:{user_id}')
    
    return jsonify({'message': 'User deleted successfully'}), 200

# Products endpoints
@api_bp.route('/products', methods=['GET'])
def get_products():
    """Get all products"""
    cache_key = 'products:all'
    
    if redis_client:
        cached = redis_client.get(cache_key)
        if cached:
            return jsonify({
                'products': json.loads(cached),
                'cached': True
            }), 200
    
    products = Product.query.all()
    products_data = [product.to_dict() for product in products]
    
    if redis_client:
        redis_client.setex(cache_key, 300, json.dumps(products_data))
    
    return jsonify({
        'products': products_data,
        'cached': False
    }), 200

@api_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product"""
    cache_key = f'product:{product_id}'
    
    if redis_client:
        cached = redis_client.get(cache_key)
        if cached:
            return jsonify(json.loads(cached)), 200
    
    product = Product.query.get_or_404(product_id)
    product_data = product.to_dict()
    
    if redis_client:
        redis_client.setex(cache_key, 300, json.dumps(product_data))
    
    return jsonify(product_data), 200

@api_bp.route('/products', methods=['POST'])
def create_product():
    """Create a new product"""
    data = request.get_json()
    
    required_fields = ['name', 'price']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Name and price are required'}), 400
    
    product = Product(
        name=data['name'],
        description=data.get('description', ''),
        price=data['price'],
        stock=data.get('stock', 0)
    )
    
    db.session.add(product)
    db.session.commit()
    
    if redis_client:
        redis_client.delete('products:all')
    
    return jsonify(product.to_dict()), 201

@api_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update a product"""
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        product.price = data['price']
    if 'stock' in data:
        product.stock = data['stock']
    
    db.session.commit()
    
    if redis_client:
        redis_client.delete('products:all')
        redis_client.delete(f'product:{product_id}')
    
    return jsonify(product.to_dict()), 200

@api_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product"""
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    
    if redis_client:
        redis_client.delete('products:all')
        redis_client.delete(f'product:{product_id}')
    
    return jsonify({'message': 'Product deleted successfully'}), 200

# Stats endpoint
@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get application statistics"""
    user_count = User.query.count()
    product_count = Product.query.count()
    
    return jsonify({
        'users': user_count,
        'products': product_count,
        'timestamp': time.time()
    }), 200
