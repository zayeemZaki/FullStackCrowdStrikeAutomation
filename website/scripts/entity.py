from flask import Blueprint, render_template
from flask_login import login_required, current_user

entity = Blueprint('entity', __name__)

# Base URL for the GraphQL API
graphqlUrl = 'https://api.crowdstrike.com/identity-protection/combined/graphql/v1'

@entity.route('/entities', methods=['GET', 'POST'])
@login_required
def entities():
    return render_template("entity/entity.html", user=current_user)

@entity.route('/entity-table', methods=['GET', 'POST'])
@login_required
def entity_table():
    pass