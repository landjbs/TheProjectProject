from flask import request, redirect, url_for, render_template, flash
from flask_login import login_required, current_user

from ..badge import badge
