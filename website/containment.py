from flask import Blueprint, render_template, session
from flask_login import login_required, current_user, UserMixin
from falconpy import APIHarnessV2
import pandas as pd

containment = Blueprint('containment', __name__)




@containment.route('/containment', methods=['GET','POST'])
@login_required
def falcon_containment():
    return render_template("containment.html", user=current_user)





@containment.route('/group-members', methods=['GET', 'POST'])
@login_required
def group_members():
    # Create our base authentication dictionary (parent / child)
    auth = {
        "client_id": session.get('client_id'),
        "client_secret": session.get('client_secret'),
        "pythonic": True
    }

    print(session.get('client_id'))
        
    groupNames, groupIds, groupDescription= list(), list(), list()
        
    with APIHarnessV2(**auth) as sdk:
        results = sdk.command("queryCombinedHostGroups")
            
        for result in results:
            groupNames.append(result['name'])
            groupIds.append(result['id'])
            groupDescription.append(result.get('description', 'N/A'))

        # Create the DataFrame
        data = {
            'Group Name': groupNames,
            'Group Ids': groupIds,
            'Description': groupDescription
        }
        pd.set_option('display.max_rows', None)
        df = pd.DataFrame(data)
        print("Hello")    
        # Print the DataFrame
        # print("\n", df, "\n")
        df_html = df.to_html(classes='table table-striped')
    
        return render_template("contain_group.html", tables=[df_html], titles=df.columns.values, user=current_user)





@containment.route('/contain-host', methods=['GET', 'POST'])
@login_required
def contain_host():
    return render_template("contain_host.html")