from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from flask_login import login_required, current_user
import requests
import pandas as pd
from datetime import datetime, timezone
from falconpy import RealTimeResponse

views = Blueprint('views', __name__)



@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)








@views.route('/stale-accounts', methods=['GET', 'POST'])
@login_required
def stale_accounts():
    token = session.get('token')  # Get the token from the session
    if not token:
        flash('You need to authenticate first', category='error')
        return redirect(url_for('auth.authenticate'))

    graphqlUrl = 'https://api.crowdstrike.com/identity-protection/combined/graphql/v1'
    rest_api_url = 'https://api.crowdstrike.com/alerts/entities/alerts/v1'

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # Query to get the count of stale user entities
    count_query = """
    query {
     countEntities(types: [USER], stale: true)
    }
    """
    count_response = requests.post(graphqlUrl, headers=headers, json={'query': count_query})

    if count_response.status_code != 200:
        flash('Failed to retrieve entity count', category='error')
        return redirect(url_for('views.home'))

    count_data = count_response.json()
    stale_users_count = count_data.get('data', {}).get('countEntities', 0)
    flash(f"Total number of stale user entities: {stale_users_count}", category='info')

    # Query to fetch stale user entities
    entity_query = """
    query {
        entities(types: [USER], stale: true, first: 100) {
            nodes {
                primaryDisplayName
                secondaryDisplayName
                hasRole(type: HumanUserAccountRole)
                riskScore
                riskScoreSeverity
                accounts {
                    ... on ActiveDirectoryAccountDescriptor {
                        domain
                    }
                }
                ... on EndpointEntity {
                    mostRecentActivity
                }
            }
        }
    }
    """

    response = requests.post(graphqlUrl, headers=headers, json={'query': entity_query})

    if response.status_code != 200:
        flash('Failed to retrieve users', category='error')
        return redirect(url_for('views.home'))

    data = response.json()
    users = data.get('data', {}).get('entities', {}).get('nodes', [])
    allStaleUsers = []

    for user in users:
        primaryName = user.get('primaryDisplayName')
        secondaryName = user.get('secondaryDisplayName')
        isHuman = user.get('hasRole')
        riskScore = user.get('riskScore')
        riskScoreSeverity = user.get('riskScoreSeverity')
        domain = user.get('accounts', [{}])[0].get('domain')
        mostRecentActivity = user.get('mostRecentActivity')

        # Calculate inactive period
        if mostRecentActivity:
            mostRecentActivityDate = datetime.fromisoformat(mostRecentActivity.replace('Z', '+00:00')).replace(tzinfo=timezone.utc)
            inactivePeriod = (datetime.now(timezone.utc) - mostRecentActivityDate).days
        else:
            inactivePeriod = None

        allStaleUsers.append((primaryName, secondaryName, isHuman, riskScore, riskScoreSeverity, domain, inactivePeriod))

    data = {
        'Primary Name': [user[0] for user in allStaleUsers],
        'Secondary Name': [user[1] for user in allStaleUsers],
        'Is Human': [user[2] for user in allStaleUsers],
        'Risk Score': [user[3] for user in allStaleUsers],
        'Risk Severity': [user[4] for user in allStaleUsers],
        'Domain': [user[5] for user in allStaleUsers],
        'Inactive Period (days)': [user[6] for user in allStaleUsers],
    }

    df = pd.DataFrame(data)
    df_html = df.to_html(classes='table table-striped')

    return render_template("stale_accounts.html", tables=[df_html], titles=df.columns.values, user=current_user)










