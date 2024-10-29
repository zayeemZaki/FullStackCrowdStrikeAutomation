from flask import Blueprint, render_template, session, request, flash, redirect, url_for
from flask_login import login_required, current_user
from falconpy import APIHarnessV2
import requests
import pandas as pd

maliciousFiles = Blueprint('maliciousFiles', __name__)

@maliciousFiles.route('/malicious-files', methods=['GET', 'POST'])
@login_required
def malicious_files():
    if request.method == 'POST':
        return get_malicious_files()
    return render_template("maliciousFiles/maliciousFiles.html", user=current_user)

@login_required
def get_malicious_files():
    device_names = request.form.get('device-names', '').split('\n')
    token = session.get('token')
    client_id = session.get('client_id')
    client_secret = session.get('client_secret')

    if not token or not client_id or not client_secret:
        flash("Missing required session credentials.")
        return render_template("maliciousFiles/maliciousFiles.html", user=current_user)

    def getDeviceId(hostname):
        url = "https://api.crowdstrike.com/devices/queries/devices/v1"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        params = {
            "filter": f"hostname:'{hostname}'"
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        devices = response.json().get("resources", [])
        return devices[0] if devices else None

    def query_malicious_files(falcon, host_id):
        """ Query malicious files for a specified host """
        try:
            filters = f"host_id:'{host_id}'"
            response = falcon.command("query_malicious_files", filter=filters)

            if response['status_code'] == 200 and 'resources' in response['body']:
                ids = response['body']['resources']
                if ids:
                    return ids
                else:
                    flash(f"No malicious files found for host {host_id}.")
            else:
                flash(f"Unexpected response or no resources found: {response}")

            return []
        except Exception as e:
            flash(f"Error executing command: {e}")
            return []

    def query_malicious_files_without_filter(falcon):
        """ Query all malicious files without filter """
        try:
            response = falcon.command("query_malicious_files")

            if response['status_code'] == 200 and 'resources' in response['body']:
                ids = response['body']['resources']
                if ids:
                    return ids
                else:
                    flash("No malicious files found.")
            else:
                flash(f"Unexpected response or no resources found: {response}")

            return []
        except Exception as e:
            flash(f"Error executing command: {e}")
            return []
        
    def get_file_details(falcon, file_id):
        """ Get details about a specific file ID """
        try:
            response = falcon.command("get_malicious_files_by_ids", ids=file_id)
            if response['status_code'] == 200 and 'resources' in response['body']:
                file_details = response['body']['resources'][0]
                return {
                    'file_id': file_id,
                    'file_name': file_details.get('filename', 'Unknown'),
                    'file_path': file_details.get('filepath', 'Unknown'),
                    'hash': file_details.get('hash', 'Unknown'),
                    'severity': file_details.get('severity', 'Unknown'),
                    'quarantined': file_details.get('quarantined', False),
                    'last_updated': file_details.get('last_updated', 'Unknown')
                }
            else:
                flash(f"Unexpected response or no resources found: {response}")
        except Exception as e:
            flash(f"Error retrieving file details: {e}")
        return None

    falcon = APIHarnessV2(
        client_id=client_id,
        client_secret=client_secret
    )

    device_ids = []

    if device_names:
        for device_name in device_names:
            device_name = device_name.strip()
            if device_name:
                device_id = getDeviceId(device_name)
                if device_id:
                    device_ids.append(device_id)
    else:
        # Add default id for testing if no device names are provided
        device_ids.append('b9e1afd1cd38473b8d35ffa992ba5aa0')

    all_files_ids = []

    if device_ids:
        for device in device_ids:
            files = query_malicious_files(falcon, device)
            all_files_ids.extend(files)
    else:
        files = query_malicious_files_without_filter(falcon)
        all_files_ids.extend(files)

    all_files = []
    for file_id in all_files_ids:
        file_details = get_file_details(falcon, file_id)
        if file_details:
            all_files.append(file_details)

    df = pd.DataFrame(all_files)
    table_html = df.to_html(classes='table table-striped left-align-headers')

    return render_template("maliciousFiles/maliciousFiles.html", tables=[table_html], titles=df.columns.values, user=current_user)
