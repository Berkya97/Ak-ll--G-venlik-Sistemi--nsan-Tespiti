from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app():
    app = Flask(__name__, 
                template_folder='../../templates',  # Template klasörü yolunu düzelt
                static_folder='../../static')       # Static klasörü yolunu düzelt
    
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    socketio.init_app(app)
    
    return app
