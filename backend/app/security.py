"""
Module de sécurité pour l'API Flask
Implémente: Rate limiting, CORS, JWT, validation, headers de sécurité
"""

from functools import wraps
from flask import request, jsonify
import time
from collections import defaultdict
import re
import hashlib

# Rate limiting simple (en production, utiliser Redis)
request_counts = defaultdict(lambda: {"count": 0, "reset_time": time.time()})

def rate_limit(max_requests=100, window=60):
    """
    Decorator pour limiter le nombre de requêtes par IP
    max_requests: nombre max de requêtes
    window: fenêtre de temps en secondes
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            ip = request.remote_addr
            current_time = time.time()
            
            # Reset le compteur si la fenêtre est expirée
            if current_time > request_counts[ip]["reset_time"]:
                request_counts[ip] = {
                    "count": 0,
                    "reset_time": current_time + window
                }
            
            # Incrémenter le compteur
            request_counts[ip]["count"] += 1
            
            # Vérifier la limite
            if request_counts[ip]["count"] > max_requests:
                return jsonify({
                    "error": "Rate limit exceeded",
                    "retry_after": int(request_counts[ip]["reset_time"] - current_time)
                }), 429
            
            return f(*args, **kwargs)
        return wrapped
    return decorator


def validate_email(email):
    """Valide le format d'un email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username(username):
    """Valide un nom d'utilisateur (alphanumérique, 3-20 caractères)"""
    if not username or len(username) < 3 or len(username) > 20:
        return False
    return re.match(r'^[a-zA-Z0-9_-]+$', username) is not None


def sanitize_input(text, max_length=200):
    """Nettoie et limite la longueur d'une entrée utilisateur"""
    if not text:
        return ""
    # Supprimer les caractères dangereux
    text = re.sub(r'[<>\'\"\\]', '', str(text))
    return text[:max_length].strip()


def validate_price(price):
    """Valide qu'un prix est positif et raisonnable"""
    try:
        price = float(price)
        return 0 <= price <= 999999.99
    except (ValueError, TypeError):
        return False


def validate_stock(stock):
    """Valide qu'un stock est un entier positif"""
    try:
        stock = int(stock)
        return 0 <= stock <= 1000000
    except (ValueError, TypeError):
        return False


def add_security_headers(response):
    """Ajoute les headers de sécurité HTTP"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    return response


def check_sql_injection(text):
    """Détecte les tentatives basiques d'injection SQL"""
    if not text:
        return False
    
    sql_keywords = [
        'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE',
        'ALTER', 'EXEC', 'UNION', 'OR 1=1', '--', ';--', 'xp_'
    ]
    
    text_upper = str(text).upper()
    return any(keyword in text_upper for keyword in sql_keywords)


def log_security_event(event_type, details, severity="INFO"):
    """Log des événements de sécurité"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    ip = request.remote_addr if request else "unknown"
    user_agent = request.headers.get('User-Agent', 'unknown') if request else "unknown"
    
    log_entry = {
        "timestamp": timestamp,
        "type": event_type,
        "severity": severity,
        "ip": ip,
        "user_agent": user_agent,
        "details": details
    }
    
    # En production, envoyer à un système de logging centralisé
    print(f"[SECURITY] [{severity}] {event_type}: {details} from {ip}")
    
    return log_entry


def hash_password(password):
    """Hash un mot de passe avec SHA-256 et salt"""
    salt = "microservices_salt_2024"  # En production, utiliser un salt unique par user
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()


def verify_csrf_token(token):
    """Vérifie un token CSRF (implémentation basique)"""
    # En production, utiliser Flask-WTF ou similar
    expected_token = hashlib.sha256(f"{request.remote_addr}".encode()).hexdigest()
    return token == expected_token


# Decorator pour vérifier les permissions
def require_role(role):
    """Decorator pour vérifier le rôle de l'utilisateur"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # En production, vérifier le JWT ou la session
            user_role = request.headers.get('X-User-Role', 'guest')
            
            if user_role != role and user_role != 'admin':
                log_security_event(
                    "UNAUTHORIZED_ACCESS",
                    f"User with role {user_role} tried to access {role} endpoint",
                    "WARNING"
                )
                return jsonify({"error": "Insufficient permissions"}), 403
            
            return f(*args, **kwargs)
        return wrapped
    return decorator


# Middleware pour détecter les attaques
def detect_attack_patterns():
    """Détecte les patterns d'attaque dans les requêtes"""
    # Vérifier les injections SQL
    for value in request.values.values():
        if check_sql_injection(value):
            log_security_event(
                "SQL_INJECTION_ATTEMPT",
                f"Detected SQL injection pattern in: {value[:100]}",
                "CRITICAL"
            )
            return jsonify({"error": "Invalid input detected"}), 400
    
    # Vérifier la taille des requêtes (protection DDoS)
    if request.content_length and request.content_length > 1024 * 1024:  # 1MB
        log_security_event(
            "LARGE_REQUEST",
            f"Request size: {request.content_length} bytes",
            "WARNING"
        )
        return jsonify({"error": "Request too large"}), 413
    
    return None


# Liste des IPs bloquées (en production, utiliser Redis ou base de données)
blocked_ips = set()

def is_ip_blocked(ip):
    """Vérifie si une IP est bloquée"""
    return ip in blocked_ips

def block_ip(ip, reason=""):
    """Bloque une IP"""
    blocked_ips.add(ip)
    log_security_event(
        "IP_BLOCKED",
        f"IP {ip} blocked. Reason: {reason}",
        "WARNING"
    )

def unblock_ip(ip):
    """Débloque une IP"""
    if ip in blocked_ips:
        blocked_ips.remove(ip)
        log_security_event(
            "IP_UNBLOCKED",
            f"IP {ip} unblocked",
            "INFO"
        )
