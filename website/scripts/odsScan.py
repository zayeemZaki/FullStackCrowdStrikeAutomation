from flask import Blueprint, render_template, flash, session, redirect, url_for, request, send_file
from flask_login import login_required, current_user
import requests
from datetime import datetime, timezone
import pandas as pd
import io

odsScan = Blueprint('odsScan', __name__)

@odsScan.route('/ods_scan', methods=['GET', 'POST'])
@login_required
def ods_scan():
    return render_template("odsScan/odsScan.html", user=current_user)