# app.py
from flask import Flask
from blueprints.auth import auth_bp
from blueprints.dashboard import dashboard_bp
from blueprints.directory import directory_bp

app = Flask(__name__)
app.secret_key = 'replace_this_with_a_secure_random_string' 

# Register the blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(directory_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)