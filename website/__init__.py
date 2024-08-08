from flask import Flask
from flask_login import LoginManager, UserMixin
from flask import session

class User(UserMixin):
    pass

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hbywiofnaugiarg;ag;'

    from .views import views
    from .auth import auth
    from .stale import stale

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(stale, url_prefix='/')

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
