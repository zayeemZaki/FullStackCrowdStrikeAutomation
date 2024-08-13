from flask import Blueprint
from flask_login import login_required

adminRights = Blueprint('containment', __name__)

@adminRights.route('/admin-rights', methods=['GET', 'POST'])
@login_required
def adminRights():
    pass