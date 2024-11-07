import requests
import pandas as pd
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, session
from flask_login import login_required, current_user

entity = Blueprint('entity', __name__)

# Base URL for the GraphQL API
graphqlUrl = 'https://api.crowdstrike.com/identity-protection/combined/graphql/v1'

@entity.route('/entities', methods=['GET', 'POST'])
@login_required
def entities():
    return render_template("entity/entity.html", user=current_user)

@entity.route('/entity-table', methods=['POST'])
@login_required
def entity_table():
    try:
        # Get token
        token = session.get('token')  # Get the token from the session
        if not token:
            return "Authentication failed", 403

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        # Capture form data securely
        form_data = {k: v.strip() for k, v in request.form.items() if v.strip()}

        # Construct filters based on form input
        query_filters = []
        for key, value in form_data.items():
            if value:
                if key in ["first", "last"]:
                    query_filters.append(f'{key}: {value}')
                elif key == "types":
                    query_filters.append(f'{key}: [{value}]')
                else:
                    query_filters.append(f'{key}: {"true" if value.lower() == "true" else "false" if value.lower() == "false" else value}')

        query_filters_string = ", ".join(query_filters)

        # Construct the GraphQL query
        entity_query = f"""
        query {{
            entities({query_filters_string}) {{
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
            }}
        }}
        """

        # Send the request
        response = requests.post(graphqlUrl, headers=headers, json={'query': entity_query})

        if response.status_code == 200:
            data = response.json()
            users = data.get('data', {}).get('entities', {}).get('nodes', [])
            allEntities = []

            for user in users:
                primaryName = user.get('primaryDisplayName')
                secondaryName = user.get('secondaryDisplayName')
                isHuman = user.get('hasRole')
                riskScore = user.get('riskScore')
                riskScoreSeverity = user.get('riskScoreSeverity')
                domain = user.get('accounts', [{}])[0].get('domain')
                mostRecentActivity = user.get('mostRecentActivity')

                # Calculate inactive period if available
                if mostRecentActivity:
                    mostRecentActivityDate = datetime.fromisoformat(mostRecentActivity.replace('Z', '+00:00')).replace(tzinfo=timezone.utc)
                    inactivePeriod = (datetime.now(timezone.utc) - mostRecentActivityDate).days
                else:
                    inactivePeriod = None

                allEntities.append((primaryName, secondaryName, isHuman, riskScore, riskScoreSeverity, domain, inactivePeriod))

            # Create DataFrame
            data = {
                'Primary Name': [user[0] for user in allEntities],
                'Secondary Name': [user[1] for user in allEntities],
                'Is Human': [user[2] for user in allEntities],
                'Risk Score': [user[3] for user in allEntities],
                'Risk Severity': [user[4] for user in allEntities],
                'Domain': [user[5] for user in allEntities],
                'Inactive Period (days)': [user[6] for user in allEntities],
            }
            df = pd.DataFrame(data)

            # Render results in template
            return render_template("entity/entity_table.html", user=current_user, data=df.to_dict(orient="records"))

        else:
            return f"Failed to retrieve users: {response.status_code} - {response.text}", 500

    except Exception as e:
        return f"An error occurred: {str(e)}", 500