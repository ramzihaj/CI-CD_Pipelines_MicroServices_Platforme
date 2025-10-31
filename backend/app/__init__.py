from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from prometheus_flask_exporter import PrometheusMetrics
import os
import redis

db = SQLAlchemy()
redis_client = None

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 
        'postgresql://postgres:postgres@localhost:5432/microservices'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    
    # Prometheus metrics
    metrics = PrometheusMetrics(app)
    metrics.info('app_info', 'Application info', version='1.0.0')
    
    # Redis connection
    global redis_client
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = int(os.getenv('REDIS_PORT', 6379))
    try:
        redis_client = redis.Redis(
            host=redis_host, 
            port=redis_port, 
            db=0, 
            decode_responses=True,
            socket_connect_timeout=5
        )
        redis_client.ping()
        print(f"✅ Redis connected at {redis_host}:{redis_port}")
    except Exception as e:
        print(f"⚠️  Redis connection failed: {e}")
        redis_client = None
    
    # Initialize security middleware
    from app.middleware import init_security_middleware
    init_security_middleware(app)
    
    # Register blueprints
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
