from flask import Flask, render_template, redirect, url_for
from config import Config
from extensions import db, login_manager
from models import User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from blueprints.auth.routes import auth_bp
    from blueprints.admin.routes import admin_bp
    from blueprints.company.routes import company_bp
    from blueprints.student.routes import student_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)

    @app.route("/")
    def index():
        return render_template("home.html")


    with app.app_context():
        db.create_all()

        if not User.query.filter_by(email="admin@institute.edu").first():
            admin = User(email="admin@institute.edu", role="admin")
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            print("Created default admin -> admin@institute.edu / admin123")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)