from flask import Blueprint, render_template, session, request
from flask_login import login_required, current_user
from falconpy import APIHarnessV2, HostGroup
import pandas as pd

containment = Blueprint('containment', __name__)

@containment.route('/containment', methods=['GET','POST'])
@login_required
def falcon_containment():
    return render_template("containment.html", user=current_user)

@containment.route('/group-containment', methods=['GET', 'POST'])
@login_required
def list_groups():
    auth = {
        "client_id": session.get('client_id'),
        "client_secret": session.get('client_secret'),
        "pythonic": True
    }

    groupNames, groupIds, groupDescription= list(), list(), list()

    with APIHarnessV2(**auth) as sdk:
        results = sdk.command("queryCombinedHostGroups")

        for result in results:
            groupNames.append(result['name'])
            groupIds.append(result['id'])
            groupDescription.append(result.get('description', 'N/A'))

    data = {
        'Group Name': groupNames,
        'Group Ids': groupIds,
        'Description': groupDescription
    }
    pd.set_option('display.max_rows', None)
    df = pd.DataFrame(data)

    df_html = df.to_html(classes='table table-striped')

    group_id = request.form.get('group-id')
    members_df_html = None

    if group_id:
        members_df_html = list_host_group_members(group_id)

    return render_template("contain_group.html", tables=[df_html], member_tables=[members_df_html], titles=df.columns.values, user=current_user)

def list_host_group_members(group_id):
    falcon = HostGroup(client_id = session.get('client_id'), client_secret = session.get('client_secret'))
    try:
        response = falcon.query_combined_group_members(id=group_id, limit=5000)
        if response['status_code'] != 200:
            print(f"Error fetching group members: {response.get('errors', 'Unknown error')}")
            return None

        members = response['body']['resources']
        hostNames, hostIds = list(), list()

        for member in members:
            hostNames.append(member.get('hostname', 'Unknown hostname'))
            hostIds.append(member.get('device_id', 'Unknown ID'))

        data = {
            'Host_Name': hostNames,
            'HostIds': hostIds
        }
        pd.set_option('display.max_rows', None)
        df = pd.DataFrame(data)
        
        return df.to_html(classes='table table-striped')
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


    



@containment.route('/contain-host', methods=['GET', 'POST'])
@login_required
def contain_host():
    return render_template("contain_host.html")