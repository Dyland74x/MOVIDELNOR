from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
from flask_socketio import SocketIO
from config import Config
from models import db, Usuario
from auth import auth_bp
from kiosco import kiosco_bp
from publico import publico_bp
from funcionario import funcionario_bp
from admin import admin_bp
from api import api_bp

# 1. Instanciamos SocketIO con soporte para CORS y Eventlet
socketio = SocketIO(
    cors_allowed_origins="*", 
    async_mode='eventlet', 
    ping_timeout=60, 
    ping_interval=25,
    logger=True, 
    engineio_logger=True # Esto nos dará más detalle si falla
)
app = Flask(__name__)
app.config.from_object(Config)

# 2. Inicializamos DB y SocketIO con la App
db.init_app(app)
socketio.init_app(app)

# 3. IMPORTANTE: Importar y registrar los eventos de sockets DESPUÉS de init_app
from sockets import init_socket_events
init_socket_events(socketio)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(kiosco_bp, url_prefix='/kiosco')
app.register_blueprint(publico_bp, url_prefix='/publico')
app.register_blueprint(funcionario_bp, url_prefix='/funcionario')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Ejecución manual en puerto 5000 para pruebas de impresión
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)