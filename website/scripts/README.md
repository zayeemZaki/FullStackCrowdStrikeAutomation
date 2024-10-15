# `/scripts` Directory Documentation

The `/scripts` folder contains all the Python scripts responsible for automating various administrative tasks within the **Falcon Admin Management Tool**. Each script is dedicated to a specific set of operations, including managing admin rights, handling containment actions, retrieving stale accounts, and working with various endpoints in CrowdStrike's Falcon environment.

## Table of Contents

- [Overview](#overview)
- [Directory Structure](#directory-structure)
- [Script Descriptions](#script-descriptions)
  - [adminRights.py](#adminrightspy)
  - [containment.py](#containmentpy)
  - [stale.py](#stalepy)
  - [endPoint Folder](#endpoint-folder)
    - [crowdScore.py](#crowdscorepy)
    - [endPoint.py](#endpointpy)
    - [manageAlerts.py](#managealertspy)
    - [manageBehaviors.py](#managebehaviorspy)
    - [manageDetections.py](#managedetectionspy)
    - [manageIncidents.py](#manageincidentspy)
    - [searchIOCs.py](#searchiocspy)
- [Dependencies](#dependencies)

## Overview

The scripts in this directory enable the core functionalities of the Falcon Admin Management Tool. They interact with CrowdStrike's APIs to perform tasks such as:

- **Automating admin rights removal**
- **Managing host and group containment**
- **Processing stale accounts**
- **Handling detections, incidents, and alerts**

These scripts are designed to work together with the Flask application to provide an interface for administrators to monitor and manage the CrowdStrike environment.

## Directory Structure

```
/scripts/
├── adminRights.py                # Automates the removal of admin rights
├── containment.py                # Manages containment status of hosts and groups
├── stale.py                      # Loads and processes stale accounts
├── endPoint/                     # Folder containing scripts for endpoint management
│   ├── crowdScore.py             # Handles operations related to CrowdScore
│   ├── endPoint.py               # General endpoint management operations
│   ├── manageAlerts.py           # Script to manage alerts from CrowdStrike
│   ├── manageBehaviors.py        # Manages behavior-based detections
│   ├── manageDetections.py       # Handles detection management and actions
│   ├── manageIncidents.py        # Manages incidents within the CrowdStrike environment
│   ├── searchIOCs.py             # Searches and filters Indicators of Compromise (IOCs)
```

## Script Descriptions

### adminRights.py

This script automates the removal of admin rights from devices using CrowdStrike's RealTimeResponse API. It uploads a PowerShell script (`removeAdminRights.ps1`) to a device, initiates a session, and executes the script to remove the specified user from the `Administrators` group.

- **Key Functions:**
  - `remove_admin_rights`: Handles the form submission, retrieves device information, and initiates a session to execute the script.
  - `upload_script`: Uploads the PowerShell script to CrowdStrike.
  - `edit_script`: Modifies the existing script if necessary.
  - `run_script`: Executes the uploaded script on the target device.

### containment.py

The `containment.py` script manages the containment status of hosts and groups within CrowdStrike. It allows administrators to apply or lift containment actions on specific hosts or groups.

- **Key Functions:**
  - `list_groups`: Lists all host groups and their members.
  - `group_containment_action`: Contains or lifts containment for a specified group.
  - `hosts_containment_action`: Contains or lifts containment for individual hosts.

### stale.py

The `stale.py` script processes stale accounts within the CrowdStrike environment. It identifies accounts that have been inactive for a long period and displays them in a table format. It also allows exporting this data as CSV or TXT files.

- **Key Functions:**
  - `stale_accounts_table`: Retrieves and displays a table of stale accounts.
  - `download_table`: Exports the data in CSV or TXT format.

### EndPoint Folder

The `endPoint/` folder contains scripts for handling various endpoint-related operations, including managing CrowdScores, alerts, behaviors, detections, incidents, and searching IOCs.

#### crowdScore.py

The `crowdScore.py` script retrieves and displays CrowdScore data, showing the overall security posture of the organization based on the CrowdStrike environment.

- **Key Function:**
  - `crowd_score`: Retrieves CrowdScore data from the CrowdStrike API and displays it in a table format.

#### endPoint.py

The `endPoint.py` script provides a general view for managing various endpoints in the CrowdStrike environment.

- **Key Function:**
  - `end_point_view`: Renders the main endpoint management page.

#### manageAlerts.py

The `manageAlerts.py` script handles the retrieval and display of alert data. It allows administrators to view alert details and take appropriate actions.

- **Key Functions:**
  - `find_alerts`: Retrieves a list of alerts.
  - `get_alert_details`: Retrieves detailed information for specified alerts.

#### manageBehaviors.py

The `manageBehaviors.py` script handles detection behaviors. It allows administrators to view, filter, and respond to behavior-based detections.

- **Key Functions:**
  - `find_behaviors`: Retrieves a list of detection behaviors.
  - `get_behavior_details`: Retrieves detailed information for specified behaviors.

#### manageDetections.py

The `manageDetections.py` script manages detections within the CrowdStrike environment. It allows administrators to view and respond to detections based on predefined filters and criteria.

- **Key Functions:**
  - `find_detections`: Retrieves a list of detections.
  - `get_detection_details`: Retrieves detailed information for specified detections.

#### manageIncidents.py

The `manageIncidents.py` script handles incidents in the CrowdStrike environment. It allows administrators to view, filter, and respond to incidents.

- **Key Functions:**
  - `find_incidents`: Retrieves a list of incidents.
  - `get_incident_details`: Retrieves detailed information for specified incidents.

#### searchIOCs.py

The `searchIOCs.py` script handles searching for Indicators of Compromise (IOCs) within the environment. It allows administrators to search IOCs based on severity, type, and other criteria, and view related detections.

- **Key Functions:**
  - `query_ioc_ids`: Retrieves a list of IOCs.
  - `get_ioc_details_single`: Retrieves detailed information for a specific IOC.

## Dependencies

The scripts rely on the following Python packages:

- `requests`: For making HTTP requests to CrowdStrike's APIs.
- `falconpy`: Python SDK to interact with CrowdStrike's Falcon APIs.
- `pandas`: For data manipulation and analysis.
- `flask`: For creating routes and handling HTTP requests.
