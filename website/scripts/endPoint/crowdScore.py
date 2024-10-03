import requests
import pandas as pd
from flask import Blueprint, render_template, flash, redirect, url_for, session
from flask_login import login_required, current_user

crowdscores = Blueprint('crowdscores', __name__)

@crowdscores.route('/crowd-score', methods=['GET', 'POST'])
@login_required
def crowd_score():
    try:
        token = session.get('token')
        score_response = get_crowdscores(token)

        if 'resources' in score_response:
            scores_data = score_response['resources']
            
            # Convert list of scores to DataFrame
            df = pd.DataFrame(scores_data)
            
            # Convert DataFrame to HTML table
            df_html = df.to_html(classes='table table-striped left-align-headers')
            
            return render_template("endPoint/crowdScore/crowd_score.html", tables=[df_html], titles=df.columns.values, user=current_user)
        else:
            flash("Error retrieving CrowdScores: " + str(score_response.get('errors')), "danger")
    except requests.exceptions.HTTPError as err:
        flash(f"HTTP error occurred: {err}", "danger")
    except Exception as err:
        flash(f"An error occurred: {err}", "danger")
    
    return redirect(url_for('searchIOCs.search_IOCs_view'))  # Adjust redirect as necessary

def get_crowdscores(token):
    url = "https://api.crowdstrike.com/incidents/combined/crowdscores/v1"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # This will raise an exception for HTTP errors
    return response.json()
