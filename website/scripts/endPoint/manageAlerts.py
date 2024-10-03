import requests
import pandas as pd
from flask import Blueprint, render_template, flash, redirect, url_for, session
from flask_login import login_required, current_user

manageAlerts = Blueprint('manageAlerts', __name__)

@manageAlerts.route('/manage-alerts', methods=['GET', 'POST'])
@login_required
def manage_alert():
    try:
        token = session.get('token')  # Get the token from the session
        alerts_response = find_alerts(token)

        if 'resources' in alerts_response:
            alert_ids = alerts_response['resources']
            
            if alert_ids:
                alert_details_response = get_alert_details(token, alert_ids)
                if 'resources' in alert_details_response:
                    alerts_data = alert_details_response['resources']
                    
                    # Convert list of alert details to DataFrame
                    df = pd.DataFrame(alerts_data)
                    
                    # Convert DataFrame to HTML table
                    df_html = df.to_html(classes='table table-striped left-align-headers')
                    
                    return render_template("endPoint/manageAlerts/manage_alerts.html", tables=[df_html], titles=df.columns.values, user=current_user)
                else:
                    flash("Error retrieving alert details: " + str(alert_details_response.get('errors')), "danger")
            else:
                flash("No alerts found.", "info")
        else:
            flash("Error retrieving alerts: " + str(alerts_response.get('errors')), "danger")
    except requests.exceptions.HTTPError as err:
        flash(f"HTTP error occurred: {err}", "danger")
    except Exception as err:
        flash(f"An error occurred: {err}", "danger")
    
    return redirect(url_for('searchIOCs.search_IOCs_view'))  # Adjust redirect as necessary

def find_alerts(token):
    url = "https://api.crowdstrike.com/alerts/queries/alerts/v2"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # This will raise an exception for HTTP errors
    return response.json()

def get_alert_details(token, alert_ids):
    url = "https://api.crowdstrike.com/alerts/entities/alerts/v2"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "composite_ids": alert_ids
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # This will raise an exception for HTTP errors
    return response.json()
