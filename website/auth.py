from flask import Blueprint, render_template, request, flash, redirect, url_for
import requests
from flask_login import login_user, login_required, logout_user, UserMixin
from flask import session

auth = Blueprint('auth', __name__)

authUrl = 'https://api.crowdstrike.com/oauth2/token'

class User(UserMixin):
    pass

@auth.route('/authenticate', methods=['GET', 'POST'])
def authenticate():
    if request.method == 'POST':
        client_id = request.form.get('client_id')
        client_secret = request.form.get('client_secret')

        authPayload = {
            'client_id': client_id,
            'client_secret': client_secret
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post(authUrl, data=authPayload, headers=headers)
        token = response.json().get('access_token')

        if token:
            user = User()
            user.id = client_id
            login_user(user)
            session[client_id] = True
            flash('Authenticated successfully!', category='success')
            return redirect(url_for('views.home'))
        else:
            flash('Incorrect credential!', category='error')
    return render_template("authenticate.html", boolean=True)

@auth.route('/logout')
@login_required
def logout():
    user_id = current_user.get_id()
    session.pop(user_id, None)
    logout_user()
    return redirect(url_for('auth.authenticate'))
