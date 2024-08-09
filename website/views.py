from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from flask_login import login_required, current_user
import requests
import pandas as pd
from datetime import datetime, timezone
from falconpy import RealTimeResponse

views = Blueprint('views', __name__)



@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)

