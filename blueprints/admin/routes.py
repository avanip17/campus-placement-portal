from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from extensions import db
from models import User, Company, Student, PlacementDrive, Application

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    def wrap(*args, **kwargs):
        if current_user.role != "admin":
            flash("Access denied. Admins only.", "danger")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    return render_template("admin/admin_dashboard.html", 
                           student_count=Student.query.count(),
                           company_count=Company.query.count(),
                           drive_count=PlacementDrive.query.count(),
                           app_count=Application.query.count())

@admin_bp.route('/companies')
@login_required
@admin_required
def manage_companies():
    query = request.args.get('q')
    if query:
        companies = Company.query.filter(Company.name.contains(query)).all()
    else:
        companies = Company.query.all()
    return render_template("admin/manage_companies.html", companies=companies)

@admin_bp.route('/approve_company/<int:id>/<action>')
@login_required
@admin_required
def approve_company(id, action):
    company = Company.query.get_or_404(id)
    if action == 'approve':
        company.approval_status = 'Approved'
        flash(f"{company.name} has been approved.", "success")
    elif action == 'reject':
        company.approval_status = 'Rejected'
        flash(f"{company.name} has been rejected.", "danger")
    db.session.commit()
    return redirect(url_for('admin.manage_companies'))

@admin_bp.route('/drives')
@login_required
@admin_required
def manage_drives():
    drives = PlacementDrive.query.all()
    return render_template("admin/manage_drives.html", drives=drives)

@admin_bp.route('/approve_drive/<int:id>/<action>')
@login_required
@admin_required
def approve_drive(id, action):
    drive = PlacementDrive.query.get_or_404(id)
    if action == 'approve':
        drive.status = 'Approved'
        flash("Placement drive approved.", "success")
    elif action == 'reject':
        drive.status = 'Rejected'
        flash("Placement drive rejected.", "danger")
    db.session.commit()
    return redirect(url_for('admin.manage_drives'))

@admin_bp.route('/students')
@login_required
@admin_required
def manage_students():
    query = request.args.get('q')
    if query:
        students = Student.query.filter(Student.name.contains(query) | Student.department.contains(query)).all()
    else:
        students = Student.query.all()
    return render_template("admin/manage_students.html", students=students)

@admin_bp.route('/toggle_blacklist/<int:user_id>')
@login_required
@admin_required
def toggle_blacklist(user_id):
    user = User.query.get_or_404(user_id)
    
    user.is_blacklisted = not user.is_blacklisted
    status = "Blacklisted" if user.is_blacklisted else "Restored"
    db.session.commit()
    flash(f"User account has been {status}.", "info")
    return redirect(request.referrer)