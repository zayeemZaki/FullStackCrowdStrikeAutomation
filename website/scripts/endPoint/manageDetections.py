import requests
import pandas as pd
from flask import Blueprint, render_template, flash, redirect, url_for, session
from flask_login import login_required, current_user

manageDetections = Blueprint('manageDetections', __name__)

@manageDetections.route('/manage-detections', methods=['GET', 'POST'])
@login_required
def manage_detections():
    try:
        token = session.get('token')
        detections_response = find_detections(token)

        if 'resources' in detections_response:
            detection_ids = detections_response['resources']
            
            if detection_ids:
                detection_details_response = get_detection_details(token, detection_ids)
                if 'resources' in detection_details_response:
                    detections_data = detection_details_response['resources']
                    
                    # Convert list of detections to DataFrame
                    df = pd.DataFrame(detections_data)
                    
                    # Convert DataFrame to HTML table
                    df_html = df.to_html(classes='table table-striped left-align-headers')
                    
                    return render_template("endPoint/manageDetections/manage_detections.html", tables=[df_html], titles=df.columns.values, user=current_user)
                else:
                    flash("Error retrieving detection details: " + str(detection_details_response.get('errors')), "danger")
            else:
                flash("No detections found.", "info")
        else:
            flash("Error retrieving detections: " + str(detections_response.get('errors')), "danger")
    except requests.exceptions.HTTPError as err:
        flash(f"HTTP error occurred: {err}", "danger")
    except Exception as err:
        flash(f"An error occurred: {err}", "danger")
    
    return redirect(url_for('searchIOCs.search_IOCs_view'))  # Adjust redirect as necessary

def find_detections(token):
    url = "https://api.crowdstrike.com/detects/queries/detects/v1"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # This will raise an exception for HTTP errors
    return response.json()

def get_detection_details(token, detection_ids):
    url = "https://api.crowdstrike.com/detects/entities/summaries/GET/v1"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "ids": detection_ids
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # This will raise an exception for HTTP errors
    return response.json()
