from flask import Flask, jsonify # type: ignore
import json
from application.routes.user_routes import user_bp
from application.database import close_db
from application import config

def create_app():
   
    app = Flask(__name__)
    app.config.from_object(config.Config) 

    
    app.register_blueprint(user_bp)

    
    app.teardown_appcontext(close_db)

   
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"message": "Invalid endpoint."}), 404

    @app.errorhandler(405)
    def method_not_allowed_error(error):
        return jsonify({"message": "Method not allowed for this resource."}), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        if app.config['DEBUG']:
            return jsonify({"message": f"A server error occurred: {error}"}), 500
        else:
            return jsonify({"message": "An unexpected issue occurred on the server. Please try again later."}), 500
    

    @app.route('/')
    def home():
       
        return "User Management System API is Running!"

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=app.config['DEBUG'])