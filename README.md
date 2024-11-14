# Falcon Admin Management Tool

Falcon Admin Management Tool is a Flask-based web application designed to interact with CrowdStrike's Falcon APIs. The tool automates various administrative tasks, viewing and modifying containment status, providing an interface to remove users' admin rights, searching IOCs, detections, and other endpoints, searching for entities, malware files, scanning devices and streamlining the management of a CrowdStrike environment.

Please refer here for detailed documentation : [README.md](/website/README.md)

├── [Doc1](/README.md)    
|  ├── [Doc2](/website/README.md)     
|  |   ├── [Doc3](/website/scripts/README.md)  
|  |   ├── [Doc4](/website/templates/README.md)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Contributing](#contributing)

## Overview

This tool leverages CrowdStrike's Falcon APIs to perform a variety of administrative operations, such as removing admin rights from devices, checking and altering host containment status, managing stale accounts, conducting endpoint monitoring, retrieving malicious files, scanning devices and dealing with entities. It provides a user-friendly interface for security administrators to efficiently manage and secure their CrowdStrike environment.

## Features

- **Admin Rights Management**: Automate the removal of admin rights from specific devices using the RealTimeResponse API.
- **Containment Status Check**: View the containment status of hosts or groups.
- **Host/Group Containment**: Contain or lift containment for hosts and groups.
- **Stale Account Management**: Identify and handle stale accounts within your environment using CrowdStrike's API.
- **User Authentication**: Secure login, logout, and session management.
- **IOC and Detection Lookup**: Search for IOCs and detections, view related incidents, alerts, and CrowdScore data.
- **Entities Lookup**: Searches for entities after applying filters to find accounts which are stale, have weak or exposed passwords and more.
- **Malicious Files Search**: Searches malicious files based on selected filters.
- **ODS Scan**: Scans devices using on demand scan.

## Prerequisites

Before running the application, ensure that you have the following installed on your system:

- [Python 3.8+](https://www.python.org)
- [pip (Python package installer)](https://pip.pypa.io/en/stable/installation/)
- A valid CrowdStrike API key with appropriate permissions for RealTimeResponse, Hosts, and Detections APIs.

## Installation

To set up and run the application locally, follow these steps:

1. **Clone the repository:**

    ```bash
    git clone https://github.com/zayeemZaki/FullStackCrowdStrikeAutomation.git
    cd FullStackCrowdStrikeAutomation
    ```

2. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Configure IP and port (if necessary):**

   Edit the `main.py` file to configure the IP address and port for the Flask server:

    ```python
        from flask import g
        from website import create_app
        
        app = create_app()
        
        @app.before_request
        def before_request():
            ip_address = '0.0.0.0'
            g.ip_address = ip_address
            g.port = '0000'
        
        if __name__ == '__main__':
            ip_address = '0.0.0.0'
            port = 0000
            app.run(host=ip_address, port=port, debug=True)
    ```

4. **Run the Flask application:**

    ```bash
    python main.py
    ```

5. **Access the application:**

   Open your browser and navigate to `http://localhost:5000` (or the IP/port you configured in `main.py`).

## Project Structure

The project is structured as follows:

```
FullStackCrowdStrikeAutomation/
├── .venv/
├── website/
│   ├── scripts/
│   │   ├── endPoint/
│   │   │   ├── crowdScore.py
│   │   │   ├── endPoint.py
│   │   │   ├── manageAlerts.py
│   │   │   ├── manageBehaviors.py
│   │   │   ├── manageDetections.py
│   │   │   ├── manageIncidents.py
│   │   │   ├── searchIOCs.py
│   │   ├── adminRights.py               # Script for automating the removal of admin rights
│   │   ├── containment.py               # Manages containment status of hosts and groups
│   │   ├── stale.py                     # Loads and processes stale accounts
|   |   ├── entity.py                    # retrieves entities
|   |   ├── getMaliciousFiles.py         # gets the list of malicious files
|   |   ├── odsScan.py                   # Scans devices using on demand scan
│   ├── templates/
│   │   ├── adminRights/
│   │   │   ├── adminRights.html
│   │   ├── endPoint/
│   │   │   ├── crowdScore/
│   │   │   │   ├── crowd_score.html
│   │   │   ├── manageAlerts/
│   │   │   │   ├── manage_alerts.html
│   │   │   ├── manageBehaviors/
│   │   │   │   ├── manage_behaviors.html
│   │   │   ├── manageDetections/
│   │   │   │   ├── manage_detections.html
│   │   │   ├── manageIncidents/
│   │   │   │   ├── manage_incidents.html
│   │   │   ├── searchIOCs/
│   │   │   │   ├── ioc_filter_page.html
│   │   │   │   ├── ioc_results.html
│   │   │   ├── endPointView.html
|   |   ├── entity/
|   |   |   ├── entity.html
|   |   |   ├── entity_table.html
│   │   ├── falcon_containment/
│   │   │   ├── contain_group.html
│   │   │   ├── contain_host.html
│   │   │   ├── containment.html
|   |   ├── maliciousFiles/
|   |   |   ├── maliciousFiles.html
|   |   ├── odsScan/
|   |   |   ├── odsScan.html
│   │   ├── stale_accounts/
│   │   │   ├── stale_accounts.html
│   │   ├── authenticate.html
│   │   ├── base.html
│   │   ├── home.html
│   ├── README.md
│   ├── __init__.py
│   ├── auth.py
│   ├── views.py
├── .gitignore
├── README.md
├── main.py
├── requirements.txt
```

## Usage

Once the application is running, you can navigate to the various pages to perform tasks such as:

- Viewing the list of stale accounts.
- Checking and modifying the containment status of hosts/groups.
- Searching IOCs, detections, and incidents.
- Removing admin rights from hosts.
- Searchig for entities with using specific filters.
- Searching for malicious files using certain filters.
- Scanning devices using ODS.

The application also provides detailed logs and alerts for each operation performed.

## Contributing

Contributions are welcome! If you find a bug or have an idea for a new feature, please open an issue or submit a pull request. Make sure to follow the coding standards and write clear, concise commit messages.
