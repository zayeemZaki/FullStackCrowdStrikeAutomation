from flask import Blueprint, render_template, session, request, flash, redirect, url_for
from flask_login import login_required, current_user
from falconpy import APIHarnessV2
import requests
import pandas as pd

maliciousFiles = Blueprint('maliciousFiles', __name__)

@maliciousFiles.route('/malicious-files', methods=['GET', 'POST'])
@login_required
def malicious_files():
    return render_template("maliciousFiles/maliciousFiles.html", user=current_user)

@maliciousFiles.route('/get-malicious-files', methods=['GET', 'POST'])
@login_required
def get_malicious_files():
    # Default pagination parameters
    page = int(request.args.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page

    filter_type = request.form.get('sorting', 'no_filter')
    filter_value = request.form.get(f'filter_{filter_type}', '')
    token = session.get('token')
    client_id = session.get('client_id')
    client_secret = session.get('client_secret')

    if not token or not client_id or not client_secret:
        flash("Missing required session credentials.")
        return render_template("maliciousFiles/maliciousFiles.html", user=current_user)

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

    def query_malicious_files(falcon, filter_criteria, filter_type, offset, limit):
        if filter_type == "host_id":
            filters = f"host_id:'{filter_criteria}'"
        elif filter_type == "file_id":
            filters = f"id:'{filter_criteria}'"
        elif filter_type == "file_name":
            filters = f"filename:'{filter_criteria}'"
        elif filter_type == "severity":
            filters = f"severity:'{filter_criteria}'"
        elif filter_type == "quarantined":
            filters = f"quarantined:'{filter_criteria}'"
        else:
            filters = ""

        response = falcon.command("query_malicious_files",
                                  filter=filters,
                                  offset=offset,
                                  limit=limit)
        if response['status_code'] == 200 and 'resources' in response['body']:
            ids = response['body']['resources']
            if ids:
                return ids
            else:
                flash(f"No malicious files found for the filter {filter_type}.")
        else:
            flash(f"Unexpected response or no resources found: {response}")

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

    all_files_ids = []

    if filter_type == "host_id":
        device_id = getDeviceId(token, filter_value)
        files = query_malicious_files(falcon, device_id, filter_type, offset, per_page)
        all_files_ids.extend(files)
    elif filter_type == "file_id":
        file_id = filter_value
        files = query_malicious_files(falcon, file_id, filter_type, offset, per_page)
        all_files_ids.extend(files)
    elif filter_type == "file_name":
        file_name = filter_value
        files = query_malicious_files(falcon, file_name, filter_type, offset, per_page)
        all_files_ids.extend(files)
    elif filter_type == "severity":
        severity = filter_value
        files = query_malicious_files(falcon, severity, filter_type, offset, per_page)
        all_files_ids.extend(files)
    elif filter_type == "quarantined":
        quarantined = filter_value
        files = query_malicious_files(falcon, quarantined, filter_type, offset, per_page)
        all_files_ids.extend(files)
    else:
        files = query_malicious_files(falcon, "", filter_type, offset, per_page)
        all_files_ids.extend(files)

    all_files = []
    for file_id in all_files_ids:
        file_details = get_file_details(falcon, file_id)
        if file_details:
            all_files.append(file_details)

    df = pd.DataFrame(all_files)
    table_html = df.to_html(classes='table table-striped left-align-headers')

    # Check if there are more items for the next page
    more_files = len(all_files_ids) == per_page

    return render_template("maliciousFiles/maliciousFiles.html", 
                           tables=[table_html], 
                           titles=df.columns.values, 
                           user=current_user, 
                           page=page, 
                           more_files=more_files)
