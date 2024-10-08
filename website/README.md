# Falcon Admin Management Tool

This project is a Flask-based web application that interacts with CrowdStrike's Falcon APIs 
to manage various administrative tasks such as removing admin rights, checking host containment status, containing and lifting hosts/groups,
handling stale accounts, and managing user authentication.

For general details, features, prerequisites, and installation instructions, please refer to the main [README.md](https://github.com/zayeemZaki/FullStackCrowdStrikeAutomation/blob/main/README.md).

## Detailed Documentation

### `__init__.py`

This module is the entry point for initializing and configuring the Flask application. It sets up:

- The Flask application
- User session management
- Blueprints for different application components and routes

#### Components

**User Class**

A simple user class that extends `UserMixin` from Flask-Login, used for user session management.

```python
class User(UserMixin):
    pass
```

create_app Function

This function initializes the Flask application, configures server-side sessions using flask_session, registers blueprints, and sets up Flask-Login for managing user authentication.

```python
def create_app():
    # Configuration and initialization code
    return app
```

Blueprints

The following blueprints are registered within create_app:

views: General routes and views for the application.
auth: User authentication routes.
stale: Routes for handling stale accounts.
containment: Routes for containment management.
adminRights: Routes for admin rights management.
searchIOCs, endPoint, manageAlerts, manageDetections, manageIncidents, manageBehaviors, crowdscores: EndPoint management routes.
User Loader

A function to load users from the session storage:

```python
@login_manager.user_loader
def load_user(user_id):
    if user_id in session:
        user = User()
        user.id = user_id
        return user
    return None
```

auth.py
This module handles user authentication using CrowdStrike's API. It includes routes for user login and logout.

Components
User Class

A simple user class that extends UserMixin from Flask-Login.

```python

class User(UserMixin):
    pass
```

Routes

/authenticate

Handles both GET (display form) and POST (process form) requests. On successful authentication, it stores the session token, logs in the user, and redirects to the home page.

```python
@auth.route('/authenticate', methods=['GET', 'POST'])
def authenticate():
    # Authentication logic
```

/exit

Logs out the current user and clears their session.

```python
@auth.route('/exit')
@login_required
def logout():
    # Logout logic
Session Management
```

Session data is used to store:

User's client_id after successful login.
CrowdStrike API token for subsequent authorized requests.
views.py
This module handles the main views and routes for the application, including rendering templates and securing routes.

Components
Routes

/

The home route, which requires user login (@login_required) and renders the home.html template, passing the user's IP address, port, and current user object.

```python
@views.route('/')
@login_required
def home():
    return render_template("home.html", ip_address=g.ip_address, port=g.port, user=current_user)
```

Dependencies
flask: For route and template rendering.
flask_login: For securing routes and managing user sessions.
requests: For making API requests to CrowdStrike.
pandas: For data manipulation.
falconpy: To interact with CrowdStrike's RealTimeResponse.
For more detailed information about the project structure and other files, please refer to the main [README.md](https://github.com/zayeemZaki/FullStackCrowdStrikeAutomation/blob/main/README.md).

