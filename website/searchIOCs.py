import concurrent.futures
import requests
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
import pandas as pd

searchIOCs = Blueprint('searchIOCs', __name__)

IOC_QUERY_URL = "https://api.crowdstrike.com/iocs/queries/indicators/v1"
IOC_DETAIL_URL = "https://api.crowdstrike.com/iocs/entities/indicators/v1"
DETECTION_QUERY_URL = "https://api.crowdstrike.com/detects/queries/detects/v1"
DETECTION_DETAIL_URL = "https://api.crowdstrike.com/detects/entities/summaries/GET/v1"

severity_map = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4
}

@searchIOCs.route('/search-IOCs', methods=['GET', 'POST'])
@login_required
def search_IOCs_view():
    return render_template("searchIOCs/ioc_filter_page.html", user=current_user)

@searchIOCs.route('/process-ioc-search', methods=['POST'])
@login_required
def process_ioc_search():
    token = session.get('token')  # Get the token from the session

    severity = request.form.get('severity')
    ioc_types = request.form.getlist('ioc_type')
    start_date = request.form.get('date')

    session['severity'] = severity
    session['ioc_types'] = ioc_types
    session['start_date'] = start_date

    min_severity_value = severity_map.get(severity, 0)

    try:
        ioc_ids = query_ioc_ids(token)
        if not ioc_ids:
            flash("No IOCs detected.", "info")
            return redirect(url_for('searchIOCs.search_IOCs_view'))

        # Use concurrent fetch to get IOC details faster
        ioc_details_list = fetch_ioc_details_concurrently(token, ioc_ids)
        
        # Filter IOCs based on form criteria
        filtered_iocs = []
        for ioc in ioc_details_list:
            ioc_severity_value = severity_map.get(ioc.get('severity', 'unknown').lower(), 0)
            if min_severity_value and ioc_severity_value < min_severity_value:
                continue
            if ioc_types and ioc.get('type', 'unknown').lower() not in ioc_types:
                continue
            if start_date and not filter_ioc_by_date(ioc, start_date):
                continue
            filtered_iocs.append(ioc)

        # Convert filtered IOCs into DataFrame and then to HTML table
        if filtered_iocs:
            data = {
                # 'IOC ID': [ioc.get('id', 'N/A') for ioc in filtered_iocs],
                'Indicator': [ioc.get('value', 'N/A') for ioc in filtered_iocs],
                'Type': [ioc.get('type', 'N/A') for ioc in filtered_iocs],
                'Severity': [ioc.get('severity', 'N/A') for ioc in filtered_iocs],
                'Created On': [ioc.get('created_on', 'N/A') for ioc in filtered_iocs],
                'Modified On': [ioc.get('modified_on', 'N/A') for ioc in filtered_iocs],
                'Description': [ioc.get('description', 'N/A') for ioc in filtered_iocs]
            }
            df = pd.DataFrame(data)
            df_html = df.to_html(classes='table table-striped')

            # Passing the table to the template
            return render_template("searchIOCs/ioc_results.html", tables=[df_html], titles=df.columns.values, user=current_user)
        else:
            flash("No IOCs matched the criteria.", "info")
            return redirect(url_for('searchIOCs.search_IOCs_view'))
    except Exception as e:
        flash(f"Error processing IOC search: {str(e)}", "danger")
        return redirect(url_for('searchIOCs.search_IOCs_view'))

@searchIOCs.route('/details-ioc-search', methods=['POST'])
@login_required
def get_ioc_details_by_id():
    ioc_id = request.form.get('ioc-id')
    token = session.get('token')

    try:
        ioc_details = get_ioc_details_single(token, ioc_id)
        if not ioc_details:
            flash("No details found for the provided IOC ID.", "danger")
            return redirect(url_for('searchIOCs.search_IOCs_view'))

        ioc = ioc_details[0]
        
        details = [
            {"key": "Type", "value": ioc['type']},
            {"key": "Value", "value": ioc['value']},
            {"key": "Severity", "value": ioc.get('severity', 'N/A')},
            {"key": "Description", "value": ioc.get('description', 'N/A')},
            {"key": "Created On", "value": ioc.get('created_on', 'N/A')},
            {"key": "Created By", "value": ioc.get('created_by', 'N/A')},
            {"key": "Modified On", "value": ioc.get('modified_on', 'N/A')},
            {"key": "Modified By", "value": ioc.get('modified_by', 'N/A')},
            {"key": "Deleted", "value": ioc['deleted']}
        ]

        # Get detection details
        detection_ids = get_detections_for_ioc(token, ioc['value'])
        formatted_details = []
        if detection_ids:
            detection_details_response = get_detection_details(token, detection_ids)
            formatted_details = format_detection_details(detection_details_response)

        # Convert detection details into DataFrame and then to HTML table
        detection_df_html = ""
        if formatted_details:
            detection_data = {
                'Detection ID': [det['Detection ID'] for det in formatted_details],
                'Timestamp': [det['Timestamp'] for det in formatted_details],
                'Severity': [det['Severity'] for det in formatted_details],
                'Status': [det['Status'] for det in formatted_details],
                'Description': [det['Description'] for det in formatted_details],
                'Host': [det['Host'] for det in formatted_details]
            }
            detection_df = pd.DataFrame(detection_data)
            detection_df_html = detection_df.to_html(classes='table table-striped')

        return render_template("searchIOCs/ioc_results.html", user=current_user, details=details, detection_tables=[detection_df_html])
    except Exception as e:
        flash(f"Error fetching IOC details: {e}", "danger")
        return redirect(url_for('searchIOCs.search_IOCs_view'))

def query_ioc_ids(token):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    ioc_ids = []
    next_cursor = None
    params = {
        'limit': 100
    }

    while True:
        if next_cursor:
            params['after'] = next_cursor
        
        response = requests.get(IOC_QUERY_URL, headers=headers, params=params)
        if response.status_code == 200:
            json_response = response.json()
            new_ioc_ids = json_response.get('resources', [])
            
            if not new_ioc_ids:
                break
            
            ioc_ids.extend(new_ioc_ids)
            next_cursor = json_response.get('meta', {}).get('pagination', {}).get('after')
            
            # If there is no next_cursor, we are done
            if not next_cursor:
                break

        else:
            print(f"Error in pagination loop: {response.status_code} - {response.text}")
            raise Exception(f"Failed to query IOCs: {response.text}")
    
    return ioc_ids

def fetch_ioc_details_concurrently(token, ioc_ids):
    def fetch_detail(ioc_id):
        return get_ioc_details_single(token, ioc_id)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ioc = {executor.submit(fetch_detail, ioc_id): ioc_id for ioc_id in ioc_ids}
        ioc_details = []
        for future in concurrent.futures.as_completed(future_to_ioc):
            try:
                ioc_details.extend(future.result())
            except Exception as e:
                print(f"Error occurred: {e}")
    
    return ioc_details

def get_ioc_details_single(token, ioc_id):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    params = {'ids': ioc_id}
    response = requests.get(IOC_DETAIL_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('resources', [])
    else:
        raise Exception(f"Failed to get IOC details for {ioc_id}: {response.text}")

def get_detections_for_ioc(token, ioc_value):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    fql_filter = f"behaviors.ioc_value:'{ioc_value}'"
    params = {'filter': fql_filter}
    
    response = requests.get(DETECTION_QUERY_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('resources', [])
    else:
        raise Exception(f"Failed to get detections for IOC: {response.text}")

def get_detection_details(token, detection_ids):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {"ids": detection_ids}
    response = requests.post(DETECTION_DETAIL_URL, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def format_detection_details(detection_details):
    formatted_details = []
    for detection in detection_details.get('resources', []):
        host_info = detection.get("device", {}) 
        behaviors = detection.get("behaviors", [{}])[0] 
        detail = {
            "Detection ID": detection.get("detection_id", "N/A"),
            "Timestamp": behaviors.get("timestamp", "N/A"),
            "Severity": detection.get("max_severity_displayname", "N/A"),
            "Status": detection.get("status", "N/A"),
            "Description": behaviors.get("description", "N/A"),
            "Host": host_info.get("hostname", "N/A")
        }
        formatted_details.append(detail)
    return formatted_details

def filter_ioc_by_date(ioc, start_date):
    created_date = ioc.get('created_timestamp')
    if created_date and start_date:
        return created_date >= start_date
    return True
