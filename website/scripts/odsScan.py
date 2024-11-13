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
        if response.status_code == 401:
            flash("Unauthorized access while checking device status. Please refresh your API token.", 'danger')
        else:
            flash(f"HTTP Error: {str(e)}", 'danger')
        return False
    except Exception as e:
        flash(f"Unexpected Error: {str(e)}", 'danger')
        return False


def getDeviceId(token, hostname):
    url = "https://api.crowdstrike.com/devices/queries/devices/v1"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "filter": f"hostname:'{hostname}'"
    }
    response = requests.get(url, headers=headers, params=params)

    try:
        response.raise_for_status()
        devices = response.json().get("resources", [])
        return devices[0] if devices else None
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            flash("Unauthorized access. Please check your API token.", 'danger')
        else:
            flash(f"HTTP Error: {str(e)}", 'danger')
        return None
    except Exception as e:
        flash(f"Unexpected Error: {str(e)}", 'danger')
        return None




@odsScan.route('/ods_scan', methods=['GET', 'POST'])
@login_required
def ods_scan():
    if request.method == 'POST':
        host_ids_input = request.form.get('host-id')
        group_id = request.form.get('group-id')
        client_id = session.get('client_id')
        client_secret = session.get('client_secret')

        if not host_ids_input and not group_id:
            flash("Please provide either Host IDs or a Group ID.", 'danger')
            return render_template("odsScan/odsScan.html", user=current_user)

        # Parse host IDs
        host_ids_list = host_ids_input.splitlines() if host_ids_input else []
        token = session.get('token')

        if not token:
            flash("Missing API token. Please log in again.", 'danger')
            return redirect(url_for('auth.login'))

        falcon = ODS(client_id=client_id, client_secret=client_secret)

        # Retrieve Device IDs
        host_ids = [getDeviceId(token, host) for host in host_ids_list if host]
        if group_id:
            host_ids_from_group = host_group_members(group_id, client_id, client_secret)
            if host_ids_from_group:
                host_ids.extend(host_ids_from_group)

        if not host_ids:
            flash("No valid host IDs found.", 'danger')
            return render_template("odsScan/odsScan.html", user=current_user)

        hosts_queue = deque(host_ids)

        while hosts_queue:
            current_host_id = hosts_queue.popleft()
            if is_device_online(token, current_host_id):
                BODY = {
                    "cloud_ml_level_detection": 2,
                    "cloud_ml_level_prevention": 2,
                    "description": "On Demand Scan",
                    "endpoint_notification": True,
                    "file_paths": ["C:\\Windows"],
                    "hosts": [current_host_id],
                    "quarantine": True,
                }
                try:
                    response = falcon.create_scan(body=BODY)
                    if response.get('status_code') in [200, 201]:
                        scan_info = response.get('body', {}).get('resources', [])[0]
                        flash("Scan created successfully.", 'success')
                        flash(f"Scan ID: {scan_info.get('id')}", 'info')
                    else:
                        flash("Failed to create scan.", 'danger')
                except Exception as e:
                    flash(f"Error creating scan: {str(e)}", 'danger')
            else:
                flash(f"Device {current_host_id} is offline.", 'warning')
                time.sleep(60)

        return redirect(url_for('odsScan.ods_scan'))

    return render_template("odsScan/odsScan.html", user=current_user)

if __name__ == "__main__":
    # This __main__ block is not needed in the blueprint file context.
    pass
