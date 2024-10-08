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
- **End Point**: Searches IOCs and detections related to it, looks up incidents, alerts, detections and crowdscore

## Prerequisites

Ensure you have the following installed:

- [Python 3.8+](https://www.python.org)
- pip (Python package installer)
- A valid CrowdStrike API key

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/zayeemZaki/FullStackCrowdStrikeAutomation.git
    cd FullStackCrowdStrikeAutomation
    ```

2. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

3. Make sure to change the IP address and port in `main.py` before running the application. You can find the relevant portion in `main.py`:

    ```python
    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000)
    ```

4. Run the Flask application:

    ```bash
    python main.py
    ```

## Project Structure

- `adminRights.py`: Handles the automation of removing admin rights from devices.
- `auth.py`: Manages user authentication and session handling.
- `containment.py`: Checks the containment status of hosts/groups and contains and lifts hosts/groups.
- `stale.py`: Loads and processes stale accounts using the CrowdStrike API.
- `endpoint.py`: looks up IOCs, detections, incidents, alerts and crowdscore
