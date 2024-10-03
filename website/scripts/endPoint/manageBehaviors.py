import requests
import pandas as pd
from flask import Blueprint, render_template, flash, redirect, url_for, session
from flask_login import login_required, current_user

manageBehaviors = Blueprint('manageBehaviors', __name__)

@manageBehaviors.route('/manage-behaviors', methods=['GET', 'POST'])
@login_required
def manage_behaviors():
    try:
        token = session.get('token')
        behaviors_response = find_behaviors(token)

        if 'resources' in behaviors_response:
            behavior_ids = behaviors_response['resources']
            
            if behavior_ids:
                behavior_details_response = get_behavior_details(token, behavior_ids)
                if 'resources' in behavior_details_response:
                    behaviors_data = behavior_details_response['resources']
                    
                    # Convert list of behavior details to DataFrame
                    df = pd.DataFrame(behaviors_data)
                    
                    # Convert DataFrame to HTML table
                    df_html = df.to_html(classes='table table-striped left-align-headers')
                    
                    return render_template("endPoint/manageBehaviors/manage_behaviors.html", tables=[df_html], titles=df.columns.values, user=current_user)
                else:
                    flash("Error retrieving behavior details: " + str(behavior_details_response.get('errors')), "danger")
            else:
                flash("No behaviors found.", "info")
        else:
            flash("Error retrieving behaviors: " + str(behaviors_response.get('errors')), "danger")
    except requests.exceptions.HTTPError as err:
        flash(f"HTTP error occurred: {err}", "danger")
    except Exception as err:
        flash(f"An error occurred: {err}", "danger")
    
    return redirect(url_for('searchIOCs.search_IOCs_view'))  # Adjust redirect as necessary

def find_behaviors(token):
    url = "https://api.crowdstrike.com/incidents/queries/behaviors/v1"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # This will raise an exception for HTTP errors
    return response.json()

def get_behavior_details(token, behavior_ids):
    url = "https://api.crowdstrike.com/incidents/entities/behaviors/GET/v1"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "ids": behavior_ids
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # This will raise an exception for HTTP errors
    return response.json()
