from flask import Blueprint
patient_bp = Blueprint("patient", __name__, url_prefix="/patient", template_folder="../../templates/patient")
from . import routes
