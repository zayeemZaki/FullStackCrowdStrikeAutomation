import time
import requests
from falconpy import ODS, HostGroup
from flask import Blueprint, render_template, flash, redirect, url_for, request, session
from flask_login import login_required, current_user
from collections import deque

odsScan = Blueprint('odsScan', __name__)

def host_group_members(group_id, client_id, client_secret):
    try:
        falcon = HostGroup(client_id = client_id, client_secret = client_secret)
        response = falcon.query_combined_group_members(id=group_id, limit=5000)
        if response['status_code'] != 200:
            print(f"Error fetching group members: {response.get('errors', 'Unknown error')}")
            return
        
        # Extract and print hostnames and IDs
        members = response['body']['resources']
        hostIds = list()

        for member in members:
            hostIds.append(member.get('device_id', 'Unknown ID'))

        return hostIds
    
    except Exception as e:
        print(f"An error occurred: {e}")

def is_device_online(token, device_id):
    url = "https://api.crowdstrike.com/devices/entities/online-state/v1"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    params = {
        'ids': device_id
    }
    
    response = requests.get(url, headers=headers, params=params)
    try:
        response.raise_for_status()
        data = response.json()
        if data['resources']:
            state = data['resources'][0].get('state')
            return state == 'online'
        else:
            return False
    except requests.exceptions.HTTPError as e:
        raise Exception(f"HTTPError: {str(e)}")
    except Exception as e:
        raise Exception(f"Error: {str(e)}")

def getDeviceId(token, hostname):
    url = "https://api.crowdstrike.com/devices/queries/devices/v1"
    headers = {
        "Authorization": f"Bearer {token}"
        }
    params = {
        "filter": f"hostname:'{hostname}'"
        }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    devices = response.json()["resources"]
    return devices[0] if devices else None


@odsScan.route('/ods_scan', methods=['GET', 'POST'])
@login_required
def ods_scan():
    return render_template("odsScan/odsScan.html", user=current_user)


@login_required
def ods_scan():
    if request.method == 'POST':
        host_ids_input = request.form.get('host-id')
        group_id = request.form.get('group-id')
        client_id = session.get('client_id')
        client_secret = session.get('client_secret')

        # Parse host ids, one per line
        host_ids_list = host_ids_input.splitlines()
        
        # Load configuration file
        token = session.get('token')  
        falcon = ODS(client_id=client_id, client_secret=client_secret)
        
        # Retrieve Device IDs from host IDs
        host_ids = [getDeviceId(token, host) for host in host_ids_list if host]
        host_ids_from_group_id = host_group_members(group_id, client_id, client_secret)
        host_ids.extend(host_ids_from_group_id)

        if not host_ids:
            flash("No valid host IDs found.", 'danger')
            return render_template("odsScan/odsScan.html", user=current_user)

        # Use a deque to manage the hosts queue
        hosts_queue = deque(host_ids)
        hosts_tried = 0
        max_hosts = len(hosts_queue)

        while hosts_queue:
            current_host_id = hosts_queue.popleft()
            print(f"Checking if device {current_host_id} is online...")
            hosts_tried += 1
            if is_device_online(token, current_host_id):
                print(f"Device {current_host_id} is online. Proceeding with scan creation.")
                
                BODY = {
                    "cloud_ml_level_detection": 2,
                    "cloud_ml_level_prevention": 2,
                    "cpu_priority": 2,
                    "description": "On Demand Scan Description",
                    "endpoint_notification": True,
                    "file_paths": ["C:\\Windows"],
                    "hosts": [current_host_id],
                    "initiated_from": "manual",
                    "max_duration": 2,
                    "max_file_size": 60,
                    "pause_duration": 2,
                    "quarantine": True,
                    "sensor_ml_level_detection": 2,
                    "sensor_ml_level_prevention": 2
                }

                try:
                    response = falcon.create_scan(body=BODY)

                    if response.get('status_code') in [200, 201]:
                        print("Scan created successfully.")
                        scan_info = response.get('body', {}).get('resources', [])[0]
                        flash("Scan created successfully.", 'success')
                        flash(f"Scan ID: {scan_info.get('id')}", 'info')
                        flash(f"Status: {scan_info.get('status')}", 'info')
                        flash(f"Created On: {scan_info.get('created_on')}", 'info')
                    else:
                        error_message = response.get('body', {}).get('errors')
                        flash(f"Error creating scan. Status Code: {response.get('status_code')}, Error Message: {error_message}", 'danger')
                except Exception as e:
                    flash(f"Exception while creating scan: {str(e)}", 'danger')
                    return render_template("odsScan/odsScan.html", user=current_user)
                
            else:
                print(f"Device {current_host_id} is offline. Moving to the end of the queue and retrying in 60 seconds...")
                hosts_queue.append(current_host_id)
                if hosts_tried > len(max_hosts):
                    time.sleep(60)  # Delay before retrying

        return redirect(url_for('odsScan.ods_scan'))

    return render_template("odsScan/odsScan.html", user=current_user)

if __name__ == "__main__":
    # This __main__ block is not needed in the blueprint file context.
    pass
