"""
Middleware de sécurité pour Flask
"""

from flask import request, jsonify
from app.security import (
    add_security_headers,
    detect_attack_patterns,
    is_ip_blocked,
    log_security_event
)

def init_security_middleware(app):
    """Initialise tous les middlewares de sécurité"""
    
    @app.before_request
    def security_checks():
        """Exécuté avant chaque requête"""
        
        # 1. Vérifier si l'IP est bloquée
        ip = request.remote_addr
        if is_ip_blocked(ip):
            log_security_event(
                "BLOCKED_IP_ACCESS",
                f"Blocked IP {ip} tried to access {request.path}",
                "WARNING"
            )
            return jsonify({"error": "Access denied"}), 403
        
        # 2. Détecter les patterns d'attaque
        attack_response = detect_attack_patterns()
        if attack_response:
            return attack_response
        
        # 3. Valider les headers obligatoires pour certaines routes
        if request.method in ['POST', 'PUT', 'DELETE']:
            if not request.is_json and request.path.startswith('/api/'):
                return jsonify({"error": "Content-Type must be application/json"}), 400
    
    @app.after_request
    def add_headers(response):
        """Exécuté après chaque requête"""
        # Ajouter les headers de sécurité
        response = add_security_headers(response)
        
        # Ajouter CORS headers si nécessaire
        if request.environ.get('HTTP_ORIGIN'):
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        
        return response
    
    @app.errorhandler(404)
    def not_found(error):
        """Handler pour 404"""
        return jsonify({"error": "Resource not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handler pour 500"""
        log_security_event(
            "INTERNAL_ERROR",
            str(error),
            "ERROR"
        )
        return jsonify({"error": "Internal server error"}), 500
    
    @app.errorhandler(429)
    def rate_limit_error(error):
        """Handler pour rate limit"""
        return jsonify({
            "error": "Too many requests",
            "message": "Please slow down"
        }), 429
