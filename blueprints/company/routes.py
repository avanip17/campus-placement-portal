from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from extensions import db
from models import PlacementDrive, Application

company_bp = Blueprint("company", __name__, url_prefix="/company")

@company_bp.route('/dashboard')
@login_required
def dashboard():
    company = current_user.company_profile
    drives = PlacementDrive.query.filter_by(company_id=company.id).order_by(PlacementDrive.id.desc()).all()
    return render_template("company/company_dashboard.html", company=company, drives=drives)

@company_bp.route('/create_drive', methods=['GET', 'POST'])
@login_required
def create_drive():
    if request.method == 'POST':
        new_drive = PlacementDrive(
            company_id=current_user.company_profile.id,
            job_title=request.form['job_title'],
            description=request.form['description'],
            eligibility=request.form['eligibility'],
            application_deadline=request.form['deadline'],
            status='Pending' 
        )
        db.session.add(new_drive)
        db.session.commit()
        flash("Placement Drive created! Pending admin approval.", "success")
        return redirect(url_for('company.dashboard'))
    return render_template("company/create_drive.html")

@company_bp.route('/drive/<int:drive_id>/applications')
@login_required
def view_applications(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
   
    if drive.company_id != current_user.company_profile.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('company.dashboard'))
    
    applications = Application.query.filter_by(drive_id=drive.id).all()
    return render_template("company/view_applications.html", drive=drive, applications=applications)

@company_bp.route('/application/<int:app_id>/update_status', methods=['POST'])
@login_required
def update_application_status(app_id):
    application = Application.query.get_or_404(app_id)
   
    if application.drive.company_id != current_user.company_profile.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for('company.dashboard'))
    
    new_status = request.form.get('status')
    if new_status in ['Shortlisted', 'Selected', 'Rejected']:
        application.status = new_status
        db.session.commit()
        flash(f"Application marked as {new_status}.", "success")
        
    return redirect(url_for('company.view_applications', drive_id=application.drive_id))