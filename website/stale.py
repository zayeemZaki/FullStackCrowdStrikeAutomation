from flask import Blueprint, render_template, flash, session, redirect, url_for, request, send_file
from flask_login import login_required, current_user
import requests
from datetime import datetime, timezone
import pandas as pd
import io

stale = Blueprint('stale', __name__)

# Base URL for the GraphQL API
graphqlUrl = 'https://api.crowdstrike.com/identity-protection/combined/graphql/v1'

@stale.route('/stale_accounts', methods=['GET', 'POST'])
@login_required
def stale_accounts():
    
    return render_template("stale_accounts/stale_accounts.html", user=current_user)


@stale.route('/stale-accounts-table', methods=['GET', 'POST'])
@login_required
def stale_accounts_table():
    token = session.get('token')  # Get the token from the session
    if not token:
        flash('You need to authenticate first', category='error')
        return redirect(url_for('auth.authenticate'))

    # Get the cursor for the next set of results
    cursor = request.args.get('cursor', None)
    print(f"[DEBUG] Current cursor: {cursor}")
    
    # Retrieve sorting option from the form or session
    sortingBasedOn = request.form.get('sorting', session.get('sorting'))
    session['sorting'] = sortingBasedOn
    print(f"[DEBUG] Sorting based on: {sortingBasedOn}")

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # Query to fetch stale user entities with cursor-based pagination
    entity_query = f"""
    query {{
        entities(types: [USER], stale: true, first: 100 {f', after: "{cursor}"' if cursor else ''}) {{
            nodes {{
                primaryDisplayName
                secondaryDisplayName
                hasRole(type: HumanUserAccountRole)
                riskScore
                riskScoreSeverity
                accounts {{
                    ... on ActiveDirectoryAccountDescriptor {{
                        domain
                    }}
                }}
                ... on EndpointEntity {{
                    mostRecentActivity
                }}
            }}
            pageInfo {{
                endCursor
                hasNextPage
            }}
        }}
    }}
    """
    print(f"[DEBUG] GraphQL Query: {entity_query}")

    response = requests.post(graphqlUrl, headers=headers, json={'query': entity_query})
    print(f"[DEBUG] Response status code: {response.status_code}")

    if response.status_code != 200:
        flash('Failed to retrieve users', category='error')
        print(f"[ERROR] Failed to retrieve users: {response.text}")
        return redirect(url_for('views.home'))

    data = response.json()
    print(f"[DEBUG] Response JSON: {data}")

    users = data.get('data', {}).get('entities', {}).get('nodes', [])
    print(f"[DEBUG] Number of users retrieved: {len(users)}")

    pageInfo = data.get('data', {}).get('entities', {}).get('pageInfo', {})
    endCursor = pageInfo.get('endCursor')
    hasNextPage = pageInfo.get('hasNextPage')
    print(f"[DEBUG] endCursor: {endCursor}, hasNextPage: {hasNextPage}")

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

        print(f"[DEBUG] User: {primaryName}, Inactive Period: {inactivePeriod}")

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
    print(f"[DEBUG] DataFrame created with {len(df)} records")

    # Perform sorting based on user input
    if sortingBasedOn == "risk_score":
        df = df.sort_values(by='Risk Score', ascending=False)
    elif sortingBasedOn == "is_human":
        df = df.sort_values(by='Is Human', ascending=False)
    elif sortingBasedOn == "domain":
        df = df.sort_values(by='Domain')
    elif sortingBasedOn == "inactive_period":
        df = df.sort_values(by='Inactive Period (days)', ascending=False)
    else:
        print(f"[ERROR] Invalid sorting input: {sortingBasedOn}")
        return redirect(url_for('views.home'))

    dict_obj = df.to_dict('dict')
    session['data'] = dict_obj
    print(f"[DEBUG] Data stored in session")

    df_html = df.to_html(classes='table table-striped')
    print(f"[DEBUG] DataFrame converted to HTML table")

    return render_template(
        "stale_accounts/stale_accounts.html", 
        tables=[df_html], 
        titles=df.columns.values, 
        user=current_user, 
        end_cursor=endCursor, 
        has_next_page=hasNextPage
    )

@stale.route('/download-table/<file_format>', methods=['GET'])
@login_required
def download_table(file_format):
    data = session.get('data')
    df = pd.DataFrame(data)
    print(f"[DEBUG] Downloading table as {file_format}")

    if file_format == 'csv':
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        print(f"[DEBUG] CSV generated")
        return send_file(io.BytesIO(output.getvalue().encode('utf-8')), mimetype='text/csv', as_attachment=True, download_name='stale_accounts.csv')
    elif file_format == 'txt':
        output = io.StringIO()
        df.to_string(output, index=False)
        output.seek(0)
        print(f"[DEBUG] TXT file generated")
        return send_file(io.BytesIO(output.getvalue().encode('utf-8')), mimetype='text/plain', as_attachment=True, download_name='stale_accounts.txt')
    
    print(f"[ERROR] Invalid file format requested: {file_format}")
    return redirect(url_for('stale.stale_accounts_table'))
