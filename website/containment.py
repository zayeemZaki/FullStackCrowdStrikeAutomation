from flask import Blueprint, render_template, session, request, redirect, url_for, send_file
from flask_login import login_required, current_user
from falconpy import Hosts, HostGroup, APIError, APIHarnessV2
import pandas as pd
import io

containment = Blueprint('containment', __name__)




@containment.route('/containment', methods=['GET', 'POST'])
@login_required
def falcon_containment():
    return render_template("falcon_containment/containment.html", user=current_user)




@containment.route('/group-containment', methods=['GET', 'POST'])
@login_required
def list_groups():
    auth = {
        "client_id": session.get('client_id'),
        "client_secret": session.get('client_secret'),
        "pythonic": True
    }

    groupNames, groupIds, groupDescription = list(), list(), list()

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
        session['group_id'] = group_id  # Save the selected group_id in the session

    # Only pass member_tables if members were successfully retrieved
    if members_df_html:
        return render_template("falcon_containment/contain_group.html", tables=[df_html], member_tables=[members_df_html], titles=df.columns.values, user=current_user, group_id=group_id)
    else:
        return render_template("falcon_containment/contain_group.html", tables=[df_html], titles=df.columns.values, user=current_user)


def list_host_group_members(group_id):
    falcon = HostGroup(client_id=session.get('client_id'), client_secret=session.get('client_secret'))
    try:
        response = falcon.query_combined_group_members(id=group_id, limit=5000)
        if response['status_code'] != 200 or not response['body']['resources']:
            print(f"Error fetching group members or no members found: {response.get('errors', 'Unknown error')}")
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


        session['host_ids'] = hostIds  # Save the host IDs in the session
        
        return df.to_html(classes='table table-striped')
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    

@containment.route('/group-containment-action', methods=['POST'])
@login_required
def group_containment_action():
    action = request.form.get('action')
    group_id = session.get('group_id')
    host_ids = session.get('host_ids')
    
    falcon_hosts = Hosts(client_id=session.get('client_id'), client_secret=session.get('client_secret'))
    
    if action == "contain":
        contain_group(host_ids, falcon_hosts)
    elif action == "lift":
        lift_containment_group(host_ids, falcon_hosts)

    return redirect(url_for('containment.list_groups'))

# Containment and lift containment functions
def contain_group(hosts, falcon_hosts):
    for host_id in hosts:
        response = falcon_hosts.perform_action(action_name="contain", ids=[host_id])
        if response['status_code'] == 200:
            print(f"Successfully contained host ID: {host_id}")
        else:
            print(f"Failed to contain host ID: {host_id}, Response: {response}")

def lift_containment_group(hosts, falcon_hosts):
    for host_id in hosts:
        response = falcon_hosts.perform_action(action_name="lift_containment", ids=[host_id])
        if response['status_code'] == 200:
            print(f"Successfully lifted containment for host ID: {host_id}")
        else:
            print(f"Failed to lift containment for host ID: {host_id}, Response: {response}")















@containment.route('/host-containment', methods=['GET', 'POST'])
@login_required
def hosts_containment_status():
    if request.method == 'POST':
        host_names = request.form.get('host-name')
        if not host_names:
            return render_template("falcon_containment/contain_host.html", error="Please enter host IDs.", user=current_user)

        host_names = host_names.splitlines()
        session['host_names'] = host_names

        falcon_hosts = Hosts(client_id=session.get('client_id'), client_secret=session.get('client_secret'))

        status_data = []
        for hostname in host_names:
            response = falcon_hosts.query_devices_by_filter(filter=f"hostname:'{hostname}'")
            host_id = response["body"]["resources"][0]  # Get the host ID from the response


            # Attempt to retrieve host details
            containment_status_response = falcon_hosts.get_device_details(ids=[host_id])

            if containment_status_response and containment_status_response['status_code'] == 200:
                resources = containment_status_response['body'].get('resources', [])
                if resources:
                    containment_status = resources[0].get('status', 'Unknown')
                    status_data.append({'Host ID': hostname, 'Status': containment_status})
                else:
                    error_message = containment_status_response['body'].get('errors', [{}])[0].get('message', 'Unknown error')
                    status_data.append({'Host ID': hostname, 'Status': f"Error: {error_message}"})
            else:
                error_message = containment_status_response['body'].get('errors', [{}])[0].get('message', 'Unknown error')
                status_data.append({'Host ID': hostname, 'Status': f"API Error: {error_message}"})

        df = pd.DataFrame(status_data)
        host_status_table = df.to_html(classes='table table-striped')

        return render_template("falcon_containment/contain_host.html", host_status_table=host_status_table, user=current_user)

    return render_template("falcon_containment/contain_host.html", user=current_user)







@containment.route('/host-containment-action', methods=['POST'])
@login_required
def hosts_containment_action():
    action = request.form.get('action')
    host_names = session.get('host_names')

    falcon_hosts = Hosts(client_id=session.get('client_id'), client_secret=session.get('client_secret'))

    if action == "contain":
        contain_hosts(host_names, falcon_hosts)
    elif action == "lift":
        lift_containment_hosts(host_names, falcon_hosts)

    return redirect(url_for('containment.hosts_containment_status'))

def contain_hosts(hosts, falcon_hosts):
    for host_name in hosts:

        host_id = falcon_hosts.query_devices_by_filter(filter=f"hostname:'{host_name}'")["body"]["resources"][0]  # Get the host ID from the response

        response = falcon_hosts.perform_action(action_name="contain", ids=[host_id])
        if response['status_code'] == 200:
            print(f"Successfully contained host ID: {host_id}")
        else:
            print(f"Failed to contain host ID: {host_id}, Response: {response}")

def lift_containment_hosts(hosts, falcon_hosts):
    for host_name in hosts:

        host_id = falcon_hosts.query_devices_by_filter(filter=f"hostname:'{host_name}'")["body"]["resources"][0]  # Get the host ID from the response
        
        response = falcon_hosts.perform_action(action_name="lift_containment", ids=[host_id])
        if response['status_code'] == 200:
            print(f"Successfully lifted containment for host ID: {host_id}")
        else:
            print(f"Failed to lift containment for host ID: {host_id}, Response: {response}")











