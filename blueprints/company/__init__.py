from flask import Blueprint
doctor_bp = Blueprint("doctor", __name__, url_prefix="/doctor", template_folder="../../templates/doctor")
from . import routes
