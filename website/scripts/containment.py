from flask import Blueprint, render_template, session, request, redirect, url_for, send_file
from flask_login import login_required, current_user
from falconpy import Hosts, HostGroup, APIError, APIHarnessV2
import pandas as pd
import io
from datetime import datetime
containment = Blueprint('containment', __name__)
import os
import time



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

    df_html = df.to_html(classes='table table-striped left-align-headers')

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
        group_members_status_data = list()
        print("----------")
        print(response)
        print("-----------")

        for member in members:
            hostNames.append(member.get('hostname', 'Unknown hostname'))
            hostIds.append(member.get('device_id', 'Unknown ID'))
            group_members_status_data.append(member.get('status', 'Unknown Status'))


        data = {
            'Host_Name': hostNames,
            'HostIds': hostIds,
            'status': group_members_status_data
        }
        pd.set_option('display.max_rows', None)


        df = pd.DataFrame(data)


        session['host_ids'] = hostIds
        session['host_names'] = hostNames

        return df.to_html(classes='table table-striped')
    except Exception as e:
        print(f"An error occurred: {e}")
        return None






@containment.route('/group-containment-logs', methods=['GET'])
@login_required
def view_group_containment_logs():
    return send_file('templates/logs/group_containment_log.txt', mimetype='text/plain')

def group_log_containment_action(hostname, host_id, action, status):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"{timestamp} - Hostname: {hostname}, Host ID: {host_id}, Action: {action}, Status: {status}\n"
    with open("website/templates/logs/group_containment_log.txt", "a") as log_file:
        log_file.write(log_message)










@containment.route('/group-containment-action', methods=['POST'])
@login_required
def group_containment_action():
    action = request.form.get('action')
    group_id = session.get('group_id')
    host_ids = session.get('host_ids')
    host_names = session.get('host_names')
    falcon_hosts = Hosts(client_id=session.get('client_id'), client_secret=session.get('client_secret'))
    
    if action == "contain":
        contain_group(host_names, host_ids, falcon_hosts)
    elif action == "lift":
        lift_containment_group(host_names, host_ids, falcon_hosts)

    return redirect(url_for('containment.list_groups'))


def contain_group(hostNames, hostIds, falcon_hosts):

    for i in range(len(hostIds)):
        falcon_hosts.perform_action(action_name="contain", ids=[hostIds[i]])
        
    time.sleep(60)

    for i in range(len(hostIds)):
        result = falcon_hosts.get_device_details(ids=hostIds[i])

        if result['status_code'] == 200:
            print(f"Successfully contained host ID: {hostIds[i]}")
            status = result["body"]["resources"][0]["status"]
        else:
            print(f"Failed to contain host ID: {hostIds[i]}, Response: {result}")
            status = result["body"]["resources"][0]["status"]
        
        group_log_containment_action(hostNames[i], hostIds[i], "contain", status)


def lift_containment_group(hostNames, hostIds, falcon_hosts):

    for i in range(len(hostIds)):
        falcon_hosts.perform_action(action_name="lift_containment", ids=[hostIds[i]])
    
    time.sleep(60)

    for i in range(len(hostIds)):
        result = falcon_hosts.get_device_details(ids=hostIds[i])

        if result['status_code'] == 200:
            print(f"Successfully lifted containment for host ID: {hostIds[i]}")
            status = result["body"]["resources"][0]["status"]
        else:
            print(f"Failed to lift containment for host ID: {hostIds[i]}, Response: {result}")
            status = result["body"]["resources"][0]["status"]
        
        group_log_containment_action(hostNames[i], hostIds[i], "lift_containment", status)







@containment.route('/hosts-containment-logs', methods=['GET'])
@login_required
def view_host_containment_logs():
    return send_file('templates/logs/hosts_containment_log.txt', mimetype='text/plain')

def host_log_containment_action(hostname, host_id, action, status):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"{timestamp} - Hostname: {hostname}, Host ID: {host_id}, Action: {action}, Status: {status}\n"
    with open("website/templates/logs/hosts_containment_log.txt", "a") as log_file:
        log_file.write(log_message)







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
                    status_data.append({'Host Name': hostname, 'Status': containment_status})
                else:
                    error_message = containment_status_response['body'].get('errors', [{}])[0].get('message', 'Unknown error')
                    status_data.append({'Host Name': hostname, 'Status': f"Error: {error_message}"})
            else:
                error_message = containment_status_response['body'].get('errors', [{}])[0].get('message', 'Unknown error')
                status_data.append({'Host Name': hostname, 'Status': f"API Error: {error_message}"})

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
        falcon_hosts.perform_action(action_name="contain", ids=[host_id])

    time.sleep(60)

    for host_name in hosts:
        host_id = falcon_hosts.query_devices_by_filter(filter=f"hostname:'{host_name}'")["body"]["resources"][0]  # Get the host ID from the response
        result = falcon_hosts.get_device_details(ids=host_id)

        if result['status_code'] == 200:
            print(f"Successfully contained host ID: {host_id}")
            status = result["body"]["resources"][0]["status"]
        else:
            print(f"Failed to contain host ID: {host_id}, Response: {result}")
            status = result["body"]["resources"][0]["status"]
        
        host_log_containment_action(host_name, host_id, "contain", status)

def lift_containment_hosts(hosts, falcon_hosts):
    for host_name in hosts:
        host_id = falcon_hosts.query_devices_by_filter(filter=f"hostname:'{host_name}'")["body"]["resources"][0]  # Get the host ID from the response
        falcon_hosts.perform_action(action_name="lift_containment", ids=[host_id])

    time.sleep(60)

    for host_name in hosts:
        host_id = falcon_hosts.query_devices_by_filter(filter=f"hostname:'{host_name}'")["body"]["resources"][0]  # Get the host ID from the response
        result = falcon_hosts.get_device_details(ids=host_id)

        if result['status_code'] == 200:
            print(f"Successfully lifted containment from host ID: {host_id}")
            status = result["body"]["resources"][0]["status"]
        else:
            print(f"Failed to lift containment from host ID: {host_id}, Response: {result}")
            status = result["body"]["resources"][0]["status"]
        
        host_log_containment_action(host_name, host_id, "lift", status)










