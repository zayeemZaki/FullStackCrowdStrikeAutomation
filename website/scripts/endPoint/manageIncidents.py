import requests
import pandas as pd
from flask import Blueprint, render_template, flash, redirect, url_for, session
from flask_login import login_required, current_user

manageIncidents = Blueprint('manageIncidents', __name__)

@manageIncidents.route('/manage-incidents', methods=['GET', 'POST'])
@login_required
def manage_incidents():
    try:
        token = session.get('token')
        incidents_response = find_incidents(token)

        if 'resources' in incidents_response:
            incident_ids = incidents_response['resources']
            
            if incident_ids:
                incident_details_response = get_incident_details(token, incident_ids)
                if 'resources' in incident_details_response:
                    incidents_data = incident_details_response['resources']
                    
                    # Convert list of incidents to DataFrame
                    df = pd.DataFrame(incidents_data)
                    
                    # Convert DataFrame to HTML table
                    df_html = df.to_html(classes='table table-striped left-align-headers')
                    
                    return render_template("endPoint/manageIncidents/manage_incidents.html", tables=[df_html], titles=df.columns.values, user=current_user)
                else:
                    flash("Error retrieving incident details: " + str(incident_details_response.get('errors')), "danger")
            else:
                flash("No incidents found.", "info")
        else:
            flash("Error retrieving incidents: " + str(incidents_response.get('errors')), "danger")
    except requests.exceptions.HTTPError as err:
        flash(f"HTTP error occurred: {err}", "danger")
    except Exception as err:
        flash(f"An error occurred: {err}", "danger")
    
    return redirect(url_for('searchIOCs.search_IOCs_view'))  # Adjust redirect as necessary

def find_incidents(token):
    url = "https://api.crowdstrike.com/incidents/queries/incidents/v1"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # This will raise an exception for HTTP errors
    return response.json()

def get_incident_details(token, incident_ids):
    url = "https://api.crowdstrike.com/incidents/entities/incidents/GET/v1"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "ids": incident_ids
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # This will raise an exception for HTTP errors
    return response.json()
