# `/website` Directory Documentation

This directory contains the core components of the **Falcon Admin Management Tool**. It is organized to separate scripts, templates, and configuration files, ensuring a clear and maintainable structure for the Flask application.

For general details, features, prerequisites, and installation instructions, please refer to the main [README.md](../README.md).

## Table of Contents

- [Overview](#overview)
- [Directory Structure](#directory-structure)
- [Components](#components)
  - [Scripts Folder](#scripts-folder)
  - [Templates Folder](#templates-folder)
  - [__init__.py](#__init__.py)
  - [auth.py](#authpy)
  - [views.py](#viewspy)

## Overview

The `/website` directory contains the following primary components:

1. **Scripts**: This folder contains Python scripts that handle automation tasks such as admin rights management, containment operations, and handling stale accounts.
2. **Templates**: This folder contains HTML templates rendered by Flask for various routes.
3. **Blueprints and Flask Configuration Files**: Files such as [`__init__.py`](./__init__.py), [`auth.py`](./auth.py), and [`views.py`](./views.py) handle user authentication, session management, and the overall application structure.

## Directory Structure

```
/website/
├── scripts/                          # Contains automation scripts for different administrative tasks
│   ├── endPoint/                     # Scripts related to endpoint management and data extraction
│   │   ├── crowdScore.py             # Handles operations related to CrowdScore
│   │   ├── endPoint.py               # Main script for endpoint management
│   │   ├── manageAlerts.py           # Script to manage alerts from CrowdStrike
│   │   ├── manageBehaviors.py        # Manages behavior-based detections
│   │   ├── manageDetections.py       # Handles detection management and actions
│   │   ├── manageIncidents.py        # Manages incidents within the CrowdStrike environment
│   │   ├── searchIOCs.py             # Searches and filters Indicators of Compromise (IOCs)
│   ├── adminRights.py                # Automates the removal of admin rights
│   ├── containment.py                # Manages containment status of hosts and groups
│   ├── stale.py                      # Loads and processes stale accounts
│
├── templates/                        # HTML templates for rendering pages in Flask
│   ├── adminRights/                  # Contains templates for admin rights management
│   ├── endPoint/                     # Contains templates for endpoint management
│   │   ├── crowdScore/
│   │   │   ├── crowd_score.html
│   │   ├── manageAlerts/
│   │   │   ├── manage_alerts.html
│   │   ├── manageBehaviors/
│   │   │   ├── manage_behaviors.html
│   │   ├── manageDetections/
│   │   │   ├── manage_detections.html
│   │   ├── manageIncidents/
│   │   │   ├── manage_incidents.html
│   │   ├── searchIOCs/
│   │   │   ├── ioc_filter_page.html
│   │   │   ├── ioc_results.html
│   │   ├── endPointView.html
│   ├── falcon_containment/           # Templates for host and group containment
│   ├── stale_accounts/               # Templates for displaying and managing stale accounts
│   ├── authenticate.html             # User authentication form
│   ├── base.html                     # Base template for common layout structure
│   ├── home.html                     # Homepage template
│
├── [__init__.py](./__init__.py)                       # Initializes the Flask application and blueprints
├── [auth.py](./auth.py)                           # Handles user authentication and session management
├── [views.py](./views.py)                          # Defines general routes and main views for the application
```

## Components

### Scripts Folder

The `scripts/` folder contains the main Python files that handle the back-end logic for different administrative functionalities. The folder is further divided into subdirectories like `endPoint/`, which holds scripts specifically related to endpoint operations.

- **adminRights.py**: Automates the removal of admin rights from devices using CrowdStrike's RealTimeResponse API.
- **containment.py**: Manages the containment status of hosts and groups, including applying or lifting containment.
- **stale.py**: Loads and processes stale accounts from CrowdStrike.
- **endPoint Folder**: Contains scripts for handling IOCs, detections, alerts, incidents, behaviors, and CrowdScores.

### Templates Folder

The `templates/` folder holds all the HTML files that are rendered by Flask for different web pages. These templates are organized to correspond with the scripts and routes defined in the application.

- **adminRights Folder**: Templates related to admin rights management.
- **endPoint Folder**: Templates for displaying and managing various endpoint-related operations like detections, incidents, and CrowdScores.
- **falcon_containment Folder**: Contains templates to handle host and group containment views.
- **stale_accounts Folder**: Templates for displaying stale accounts and handling related actions.

### [`__init__.py`](./__init__.py)

The `__init__.py` file is the entry point for initializing and configuring the Flask application. It handles the following:

- Sets up the Flask app and configures server-side sessions using `flask_session`.
- Registers all blueprints for different application components, such as `auth`, `views`, `stale`, and others from the `scripts` directory.
- Initializes Flask-Login for user authentication and manages user sessions.

```python
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)

    from .views import views
    from .auth import auth
    # Import other scripts and register blueprints

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    # Register other blueprints

    login_manager = LoginManager()
    login_manager.login_view = 'auth.authenticate'
    login_manager.init_app(app)

    return app
```

### [`auth.py`](./auth.py)

The `auth.py` file manages user authentication and session handling using CrowdStrike's API. It includes the following components:

- **User Class**: A simple user class that extends `UserMixin` from Flask-Login, used for managing user sessions.
- **Routes**:
  - `/authenticate`: Displays the login form and handles the login process.
  - `/exit`: Logs out the current user and clears their session data.

```python
@auth.route('/authenticate', methods=['GET', 'POST'])
def authenticate():
    # Authentication logic here
    return render_template("authenticate.html")
```

### [`views.py`](./views.py)

The `views.py` file defines general routes and views for the application. It contains the following:

- **Home Route**: The home route (`/`) renders the `home.html` template, passing in the user's IP address and port. This route is secured with the `@login_required` decorator, ensuring that only authenticated users can access it.

```python
@views.route('/')
@login_required
def home():
    return render_template("home.html")
```

## Dependencies

- `flask`: For creating routes and rendering templates.
- `flask_login`: For managing user sessions and securing routes.
- `flask_session`: For managing server-side sessions.
- `requests`: For making API calls to CrowdStrike's endpoints.
- `falconpy`: Python SDK to interact with CrowdStrike's APIs.

For more detailed information about the project structure and other files, please refer to the main [README.md](../README.md).
