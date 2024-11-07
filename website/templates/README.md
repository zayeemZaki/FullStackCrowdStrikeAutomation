# `templates` Folder Documentation

This folder contains the HTML templates used to render the views for different routes in the **Falcon Admin Management Tool**. Each subfolder corresponds to a specific module or functionality within the application.

## Folder Structure

```
templates/
├── adminRights/
│   ├── adminRights.html             # Admin rights management page
├── endPoint/
│   ├── crowdScore/
│   │   ├── crowd_score.html         # CrowdScore page view
│   ├── manageAlerts/
│   │   ├── manage_alerts.html       # Alerts management view
│   ├── manageBehaviors/
│   │   ├── manage_behaviors.html    # Behavior management view
│   ├── manageDetections/
│   │   ├── manage_detections.html   # Detections management view
│   ├── manageIncidents/
│   │   ├── manage_incidents.html    # Incident management view
│   ├── searchIOCs/
│   │   ├── ioc_filter_page.html     # IOC filter page
│   │   ├── ioc_results.html         # IOC search results page
│   ├── endPointView.html            # Main endpoint view
├── entity/
|   ├── entity.html                  # Apply filters
|   ├── entity_table.html            # displays entities
├── falcon_containment/
│   ├── contain_group.html           # Contain group management page
│   ├── contain_host.html            # Contain host management page
│   ├── containment.html             # General containment view
├── maliciousFiles/
|   ├── maliciousFiles.html          # Malicious Files filter view and table
├── stale_accounts/
│   ├── stale_accounts.html          # Stale accounts management view
├── authenticate.html                # Authentication form
├── base.html                        # Base layout template
├── home.html                        # Home page template
```

## Overview

The templates are used to render the front-end views of the Falcon Admin Management Tool. They include forms, tables, and other UI elements needed for the application’s functionality. The folder structure is organized based on the modules of the application, making it easy to maintain and update.

## Template Descriptions

- **adminRights.html**: Handles the UI for managing and removing admin rights.
- **crowd_score.html**: Displays the CrowdScore data retrieved from the API.
- **manage_alerts.html**: Displays and manages alerts.
- **manage_behaviors.html**: Manages behavior-based detections.
- **manage_detections.html**: Provides UI for viewing and managing detections.
- **manage_incidents.html**: Manages incidents in the CrowdStrike environment.
- **ioc_filter_page.html**: Provides filtering options for searching IOCs.
- **ioc_results.html**: Displays IOC search results.
- **entity.html**: Shows all the filters for entity lookup.
- **entity_table.html**: retrieves and displays entities.
- **contain_group.html**: Allows containment of groups.
- **contain_host.html**: Allows containment of individual hosts.
- **maliciousFiles.html**: Displays filters and lists malicious files based on those filters.
- **stale_accounts.html**: Displays and manages stale accounts.
- **authenticate.html**: User login and authentication form.
- **base.html**: The base layout template used for consistent styling across pages.
- **home.html**: Home page view with links to various modules.
  