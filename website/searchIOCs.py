import requests
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
import pandas as pd

searchIOCs = Blueprint('searchIOCs', __name__)
IOC_QUERY_URL = "https://api.crowdstrike.com/iocs/queries/indicators/v1"
IOC_DETAIL_URL = "https://api.crowdstrike.com/iocs/entities/indicators/v1"

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

    severity_map = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4
    }
    min_severity_value = severity_map.get(severity, 0)

    try:
        ioc_ids = query_ioc_ids(token)
        if not ioc_ids:
            flash("No IOCs detected.", "info")
            return redirect(url_for('searchIOCs.search_IOCs_view'))

        # Filter IOCs based on form criteria
        filtered_iocs = []
        for ioc_id in ioc_ids:
            ioc_details = get_ioc_details_single(token, ioc_id)
            for ioc in ioc_details:
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
                'IOC ID': [ioc.get('id', 'N/A') for ioc in filtered_iocs],
                'Type': [ioc.get('type', 'N/A') for ioc in filtered_iocs],
                'Severity': [ioc.get('severity', 'N/A') for ioc in filtered_iocs],
                'Value': [ioc.get('value', 'N/A') for ioc in filtered_iocs],
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
def get_ioc_details_by_id():
    while True:
        ioc_id = request.form.get('ioc-id')
        token = session.get('token')
        
        try:
            ioc_details = get_ioc_details_single(token, ioc_id)
            if not ioc_details:
                flash("No details found for the provided IOC ID.", "danger")
                continue       

            ioc = ioc_details[0]

            details = []
            details.append(f"Type: {ioc['type']}")
            details.append(f"Value: {ioc['value']}")
            details.append(f"Severity: {ioc.get('severity', 'N/A')}")
            details.append(f"Description: {ioc.get('description', 'N/A')}")
            details.append(f"Created On: {ioc.get('created_on', 'N/A')}")
            details.append(f"Created By: {ioc.get('created_by', 'N/A')}")
            details.append(f"Modified On: {ioc.get('modified_on', 'N/A')}")
            details.append(f"Modified By: {ioc.get('modified_by', 'N/A')}")
            details.append(f"Deleted: {ioc['deleted']}")
            details.append("-" * 50)
                    
            return render_template("searchIOCs/ioc_results.html", user=current_user, details=details)


        except Exception as e:
            print(f"Error fetching IOC details: {e}")
















































#helper funcs
def query_ioc_ids(token):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    ioc_ids = []
    next_cursor = None
    while True:
        params = {}
        if next_cursor:
            params['cursor'] = next_cursor
        
        response = requests.get(IOC_QUERY_URL, headers=headers, params=params)
        if response.status_code == 200:
            json_response = response.json()
            ioc_ids.extend(json_response.get('resources', []))
            next_cursor = json_response.get('meta', {}).get('pagination', {}).get('next_cursor')
            
            if not next_cursor:
                break
        else:
            raise Exception(f"Failed to query IOCs: {response.text}")
    
    return ioc_ids

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

def filter_ioc_by_date(ioc, start_date):
    created_date = ioc.get('created_timestamp')
    if created_date and start_date:
        return created_date >= start_date
    return True
