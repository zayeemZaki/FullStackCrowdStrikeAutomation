import requests
import pandas as pd
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from flask_login import login_required, current_user

entity = Blueprint('entity', __name__)

graphqlUrl = 'https://api.crowdstrike.com/identity-protection/combined/graphql/v1'

@entity.route('/entities', methods=['GET', 'POST'])
@login_required
def entities():
    return render_template("entity/entity.html", user=current_user)

@entity.route('/entity-table', methods=['POST', 'GET'])
@login_required
def entity_table():
    try:
        token = session.get('token')
        if not token:
            return "Authentication failed", 403

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        form_data = request.form if request.method == 'POST' else request.args

        checkbox_fields = ['accountLocked', 'archived', 'hasAgedPassword', 'hasExposedPassword', 'impersonator',
                           'hasNeverExpiringPassword', 'hasOpenIncidents', 'hasVulnerableOs', 'inactive', 'stale',
                           'hasWeakPassword', 'isMarked', 'cloudEnabled', 'cloudOnly', 'hasAccount']

        filters = {field: (form_data.get(field) == 'on') for field in checkbox_fields}

        filters.update({
            'maxRiskScoreSeverity': form_data.get('maxRiskScoreSeverity', ''),
            'accountCreationEndTime': form_data.get('accountCreationEndTime', ''),
            'accountCreationStartTime': form_data.get('accountCreationStartTime', ''),
            'accountExpirationEndTime': form_data.get('accountExpirationEndTime', ''),
            'accountExpirationStartTime': form_data.get('accountExpirationStartTime', ''),
            'agentIds': form_data.get('agentIds', ''),
            'businessRoles': form_data.get('businessRoles', ''),
            'domains': form_data.get('domains', ''),
            'entityIds': form_data.get('entityIds', '')
        })

        query_filters = []
        for key, value in filters.items():
            if value:
                if isinstance(value, bool):
                    query_filters.append(f'{key}: {str(value).lower()}')
                else:
                    query_filters.append(f'{key}: "{value}"')

        query_filters_string = ", ".join(query_filters)

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

                if mostRecentActivity:
                    mostRecentActivityDate = datetime.fromisoformat(mostRecentActivity.replace('Z', '+00:00')).replace(tzinfo=timezone.utc)
                    inactivePeriod = (datetime.now(timezone.utc) - mostRecentActivityDate).days
                else:
                    inactivePeriod = None

                allEntities.append((primaryName, secondaryName, isHuman, riskScore, riskScoreSeverity, domain, inactivePeriod))

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

            # Pagination logic
            page = int(request.args.get('page', 1))
            per_page = 10
            total_pages = (len(df) + per_page - 1) // per_page
            start = (page - 1) * per_page
            end = start + per_page

            page_data = df.iloc[start:end].to_dict(orient="records")

            return render_template("entity/entity_table.html", user=current_user, data=page_data, page=page, total_pages=total_pages)

        else:
            return f"Failed to retrieve users: {response.status_code} - {response.text}", 500

    except Exception as e:
        return f"An error occurred: {str(e)}", 500
    
@entity.route('/entity-action', methods=['POST'])
@login_required
def entity_action():
    try:
        token = session.get('token')
        if not token:
            return "Authentication failed", 403

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        action = request.form.getlist('action')
        host_name = request.form.get('host-name')

        if not host_name.strip():
            flash('Host name cannot be empty', 'danger')
            return redirect(url_for('entity.entity_table'))

        mutations = []

        if 'mark' in action:
            mark_mutation = f"""
            mutation {{
                markEntity(entityName: "{host_name.strip()}", marked: true) {{
                    success
                    message
                }}
            }}
            """
            mutations.append(mark_mutation)

        if 'watch' in action:
            watch_mutation = f"""
            mutation {{
                addToWatchList(entityName: "{host_name.strip()}", watchListed: true) {{
                    success
                    message
                }}
            }}
            
            """
            mutations.append(watch_mutation)

        for mutation in mutations:
            response = requests.post(graphqlUrl, headers=headers, json={'query': mutation})
            if response.status_code != 200 or not response.json().get('data'):
                return f"Failed to perform action: {response.status_code} - {response.text}", 500

            if 'errors' in response.json():
                error_message = response.json()['errors'][0]['message']
                flash(f"Action failed: {error_message}", 'danger')
            else:
                success_message = response.json()['data']
                flash(f"Action successful: {success_message}", 'success')

        return redirect(url_for('entity.entity_table'))

    except Exception as e:
        return f"An error occurred: {str(e)}", 500
