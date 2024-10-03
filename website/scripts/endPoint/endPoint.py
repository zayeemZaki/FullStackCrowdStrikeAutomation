import concurrent.futures
import requests
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
import pandas as pd

endPoint = Blueprint('endPoint', __name__)


@endPoint.route('/end-point', methods=['GET', 'POST'])
@login_required
def end_point_view():
    return render_template("endPoint/endPointView.html", user=current_user)