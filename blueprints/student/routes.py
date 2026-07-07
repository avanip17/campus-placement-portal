import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models import PlacementDrive, Application

student_bp = Blueprint("student", __name__, url_prefix="/student")

@student_bp.route('/dashboard')
@login_required
def dashboard():
    student = current_user.student_profile
   
    available_drives = PlacementDrive.query.filter_by(status='Approved').all()
    my_applications = Application.query.filter_by(student_id=student.id).all()
    
   
    applied_drive_ids = [app.drive_id for app in my_applications]

    return render_template("student/student_dashboard.html", 
                           student=student,
                           drives=available_drives,
                           my_applications=my_applications,
                           applied_drive_ids=applied_drive_ids)

@student_bp.route('/apply/<int:drive_id>', methods=['POST'])
@login_required
def apply_to_drive(drive_id):
    student = current_user.student_profile
    drive = PlacementDrive.query.get_or_404(drive_id)

    
    if drive.status != 'Approved':
        flash("This drive is not currently accepting applications.", "danger")
        return redirect(url_for('student.dashboard'))

   
    existing_app = Application.query.filter_by(student_id=student.id, drive_id=drive.id).first()
    if existing_app:
        flash("You have already applied for this drive.", "warning")
        return redirect(url_for('student.dashboard'))

   
    new_app = Application(
        student_id=student.id,
        drive_id=drive.id,
        status='Applied'
    )
    db.session.add(new_app)
    db.session.commit()
    
    flash(f"Successfully applied to {drive.company.name} for {drive.job_title}!", "success")
    return redirect(url_for('student.dashboard'))

@student_bp.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    student = current_user.student_profile
    if request.method == "POST":
        student.name = request.form['name']
        student.department = request.form['department']
        student.cgpa = request.form['cgpa']
        student.contact = request.form['contact']
        
       
        file = request.files.get('resume')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
          
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            student.resume_file = filename

        db.session.commit()
        flash("Profile and Resume Updated", "success")
        return redirect(url_for('student.dashboard'))
        
    return render_template("student/update_profile.html", student=student)