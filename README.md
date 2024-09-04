# Falcon Admin Management Tool

This project is a Flask-based web application that interacts with CrowdStrike's Falcon APIs 
to manage various administrative tasks such as removing admin rights, checking host containment status, containing and lifting hosts/groups,
handling stale accounts, and managing user authentication.

## Features

- **Admin Rights Management**: Automate the removal of admin rights from devices using the RealTimeResponse API.
- **Containment Status Check**: Check the containment status of hosts.
- **Contain Hosts/Groups**: Contain hosts/groups
- **Lift containment**: Lift containment from hosts/groups
- **Stale Accounts Handling**: Load and manage stale accounts using CrowdStrike's API.
- **User Authentication**: Secure login and session management.

## Prerequisites

Ensure you have the following installed:

- [Python 3.8+](https://www.python.org)
- pip (Python package installer)
- A valid CrowdStrike API key

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/yourrepository.git
    cd yourrepository
    ```

2. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

3. Run the Flask application:

    ```bash
    python main.py
    ```

## Project Structure

- `adminRights.py`: Handles the automation of removing admin rights from devices.
- `auth.py`: Manages user authentication and session handling.
- `containment.py`: Checks the containment status of hosts/groups and contains and lifts hosts/groups.
- `stale.py`: Loads and processes stale accounts using the CrowdStrike API.


