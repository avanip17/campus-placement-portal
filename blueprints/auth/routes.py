from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User, Student, Company

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']  

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if user.role != role:
                flash(f"Access Denied: You are not registered as a {role.capitalize()}.", "warning")
                return redirect(url_for('auth.login'))
            
           
            if user.is_blacklisted:
                flash("Your account has been deactivated by the Institute Admin.", "danger")
                return redirect(url_for('auth.login'))

           
            if user.role == 'company' and user.company_profile.approval_status != 'Approved':
                flash("Your company account is currently pending Admin approval.", "warning")
                return redirect(url_for('auth.login'))

            login_user(user)
            flash(f"Welcome back!", "success")
            
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'company':
                return redirect(url_for('company.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))
        else:
            flash("Invalid email or password.", "danger")

    return render_template('auth/login.html')

@auth_bp.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        contact = request.form['contact']
        department = request.form['department']
        cgpa = request.form['cgpa']

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "warning")
            return redirect(url_for('auth.register_student'))

        new_user = User(email=email, role='student')
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        new_student = Student(user_id=new_user.id, name=name, contact=contact, department=department, cgpa=cgpa)
        db.session.add(new_student)
        db.session.commit()

        flash("Student Registration successful! You can now login.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/register_student.html')

@auth_bp.route('/register/company', methods=['GET', 'POST'])
def register_company():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        hr_contact = request.form['hr_contact']
        website = request.form['website']

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "warning")
            return redirect(url_for('auth.register_company'))

        new_user = User(email=email, role='company')
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

       
        new_company = Company(user_id=new_user.id, name=name, hr_contact=hr_contact, website=website)
        db.session.add(new_company)
        db.session.commit()

        flash("Company Registered! Please wait for Admin approval to login.", "info")
        return redirect(url_for('auth.login'))

    return render_template('auth/register_company.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for('auth.login'))