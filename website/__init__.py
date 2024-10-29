from flask import Flask
from flask_login import LoginManager, UserMixin
from flask import session
from flask_session import Session
# import os

# # Ensure the log file exists.
# log_file_path = "group_containment_log.txt"
# if not os.path.exists(log_file_path):
#     with open(log_file_path, 'w') as log_file:
#         log_file.write("")

class User(UserMixin):
    pass

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hbywiofnaugiarg;ag;'


    # Configure server-side sessions
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = './flask_session'  # Directory where session files will be stored
    app.config['SESSION_PERMANENT'] = False  # Session is not permanent
    app.config['SESSION_USE_SIGNER'] = True  # Encrypt the session data

    # Initialize the server-side session extension
    Session(app)

    from .views import views
    from .auth import auth
    from .scripts.stale import stale
    from .scripts.containment import containment
    from .scripts.adminRights import adminRights
    from .scripts.endPoint.searchIOCs import searchIOCs
    from .scripts.endPoint.endPoint import endPoint
    from .scripts.endPoint.manageAlerts import manageAlerts
    from .scripts.endPoint.manageDetections import manageDetections
    from .scripts.endPoint.manageIncidents import manageIncidents
    from .scripts.endPoint.manageBehaviors import manageBehaviors
    from .scripts.endPoint.crowdScore import crowdscores
    from .scripts.getMaliciousFiles import maliciousFiles

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(stale, url_prefix='/')
    app.register_blueprint(containment, url_prefix='/')
    app.register_blueprint(adminRights, url_prefix='/')
    app.register_blueprint(searchIOCs, url_prefix='/')
    app.register_blueprint(endPoint, url_prefix='/')
    app.register_blueprint(manageAlerts, url_prefix='/')
    app.register_blueprint(manageDetections, url_prefix='/')
    app.register_blueprint(manageIncidents, url_prefix='/')
    app.register_blueprint(manageBehaviors, url_prefix='/')
    app.register_blueprint(crowdscores, url_prefix='/')
    app.register_blueprint(maliciousFiles, url_prefix='/')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.authenticate'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        if user_id in session:
            user = User()
            user.id = user_id
            return user
        return None

    return app
