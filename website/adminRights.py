from flask import Blueprint, render_template, flash, session, redirect, url_for, request, send_file
from flask_login import login_required, current_user
import requests

upload_url = "https://api.crowdstrike.com/real-time-response/entities/scripts/v1"
initiate_session_url = "https://api.crowdstrike.com/real-time-response/entities/sessions/v1"
run_script_url = "https://api.crowdstrike.com/real-time-response/entities/active-responder-command/v1"
list_scripts_url = "https://api.crowdstrike.com/real-time-response/entities/scripts/v1"


adminRights = Blueprint('adminRights', __name__)

@adminRights.route('/admin-rights', methods=['GET', 'POST'])
@login_required
def admin_rights_view():
    return render_template("adminRights/adminRights.html", user=current_user)

@adminRights.route('/remove-admin-rights', methods=['GET', 'POST'])
@login_required
def remove_admin_rights():
    user_name = request.form.get('user-name')
    device_name = request.form.get('device-name')
    token = session.get('token')
    script_name = 'removeAdminRights.ps1'
    script_content = f"Remove-LocalGroupMember -Group 'Administrators' -Member '{user_name}'"

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
        devices = response.json()["resources"]
        return devices[0] if devices else None
    
    def initiateRtrSession(device_id):
        url = "https://api.crowdstrike.com/real-time-response/entities/sessions/v1"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        data = {
            "device_id": device_id
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["resources"][0]["session_id"]
    
    def get_script_list():
        headers = {
            'Authorization': f'Bearer {token}',
        }
        response = requests.get(list_scripts_url, headers=headers)
        try:
            response.raise_for_status()
            response_json = response.json()
            return response_json
        except requests.exceptions.HTTPError as e:
            raise
        except Exception as e:
            raise

    def check_script_exists(script_name):
        scripts = get_script_list()
        for script in scripts.get('resources', []):
            if script['name'] == script_name:
                return script['id']
        return None
    
    def upload_script():
        headers = {
            'Authorization': f'Bearer {token}',
        }
        files = {
            'name': (None, script_name),
            'permission_type': (None, 'public'),
            'file': (script_name, script_content, 'application/octet-stream')
        }
                
        response = requests.post(upload_url, headers=headers, files=files)
        try:
            response.raise_for_status()  # Raises exception for HTTP errors
            print("Upload Script Response:", response.json())
            return response.json()
        except requests.exceptions.HTTPError as e:
            raise
        except Exception as e:
            raise

    def edit_script():
        headers = {
            'Authorization': f'Bearer {token}',
        }
        files = {
            'name': (None, script_name),
            'permission_type': (None, 'public'),
            'file': (script_name, script_content, 'application/octet-stream')
        }
                
        response = requests.patch(upload_url, headers=headers, files=files)
        try:
            response.raise_for_status()  # Raises exception for HTTP errors
            print("Update Script Response:", response.json())
            return response.json()
        except requests.exceptions.HTTPError as e:
            raise
        except Exception as e:
            raise

    def run_script(session_id):
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        payload = {
            'base_command': 'runscript',
            'command_string': f'runscript -CloudFile={script_name}',
            'session_id': session_id
        }
                
        response = requests.post(run_script_url, headers=headers, json=payload)
        try:
            response.raise_for_status()  # Raises exception for HTTP errors
            return response.json()
        except requests.exceptions.HTTPError as e:
            raise
        except Exception as e:
            raise

    if check_script_exists(script_name):
        edit_script()
    else:
        upload_script()

    device_id = getDeviceId(device_name)
    session_id = initiateRtrSession(device_id)
    if not session_id:
        print(f'Failed to initiate RTR session for device ID: {device_id}')
        exit()

    run_script(session_id)

    return render_template("adminRights/adminRights.html", user=current_user)
