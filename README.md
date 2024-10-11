# Falcon Admin Management Tool

Falcon Admin Management Tool is a Flask-based web application designed to interact with CrowdStrike's Falcon APIs. The tool automates various administrative tasks, providing an interface to manage and monitor devices, user accounts, and other endpoints, streamlining the management of a CrowdStrike environment.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Overview

This tool leverages CrowdStrike's Falcon APIs to perform a variety of administrative operations, such as removing admin rights from devices, checking and altering host containment status, managing stale accounts, and conducting endpoint monitoring. It provides a user-friendly interface for security administrators to efficiently manage and secure their CrowdStrike environment.

## Features

- **Admin Rights Management**: Automate the removal of admin rights from specific devices using the RealTimeResponse API.
- **Containment Status Check**: View the containment status of hosts or groups.
- **Host/Group Containment**: Contain or lift containment for hosts and groups based on certain criteria.
- **Stale Account Management**: Identify and handle stale accounts within your environment using CrowdStrike's API.
- **User Authentication**: Secure login, logout, and session management.
- **IOC and Detection Lookup**: Search for IOCs and detections, view related incidents, alerts, and CrowdScore data.

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
    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000)
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
├── static/                          # Contains static files (CSS, images)
├── templates/                       # HTML templates for Flask rendering
├── blueprints/
│   ├── auth.py                      # Handles user authentication and session management
│   ├── home.py                      # Contains routes and logic for the homepage
│   └── __init__.py                  # Initializes Flask blueprints
├── scripts/
│   ├── adminRights.py               # Script for automating the removal of admin rights
│   ├── containment.py               # Manages containment status of hosts and groups
│   ├── endpoint.py                  # Endpoint-related operations (IOCs, detections, incidents)
│   ├── stale.py                     # Loads and processes stale accounts
│   └── utils.py                     # Utility functions for API interactions and data handling
├── requirements.txt                 # Lists the required Python packages
├── config.py                        # Configuration settings (e.g., API keys, database URIs)
├── main.py                          # Main entry point of the application
├── README.md                        # General README (this file)
└── LICENSE                          # License information
```

## Usage

Once the application is running, you can navigate to the various pages to perform tasks such as:

- Viewing the list of stale accounts.
- Checking and modifying the containment status of hosts/groups.
- Searching IOCs, detections, and incidents.
- Managing user authentication and roles.

The application also provides detailed logs and alerts for each operation performed.

## Contributing

Contributions are welcome! If you find a bug or have an idea for a new feature, please open an issue or submit a pull request. Make sure to follow the coding standards and write clear, concise commit messages.
