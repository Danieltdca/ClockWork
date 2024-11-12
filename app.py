import re
from datetime import datetime
from flask import Flask, render_template, redirect, request, session, url_for, flash
from flask_session import Session
from models import db, User, ClockRecord
from werkzeug.security import check_password_hash, generate_password_hash
from utils import login_required, calculate_current_hours, role_required, calculate_hours_worked


app = Flask(__name__)

# Configure SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clock_work.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initializing SQLAlchemy
db.init_app(app)

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def home():
    session.clear()
    return render_template("home.html")

@app.route("/dashboard")
@login_required
def dashboard():
    # Get the user_id from the session
    user_id = session.get("user_id")
    username = session.get("username")
    
    if user_id:
        all_records = ClockRecord.query.filter_by(user_id=user_id).order_by(ClockRecord.clock_in_time.desc()).all()
        current_record = ClockRecord.query.filter_by(user_id=user_id, clock_out_time=None).first()
        
        for record in all_records:
            record.current_hours_worked = calculate_current_hours(record.clock_in_time, record.clock_out_time)[0] if record.clock_out_time else "Still Clocked In"
        
    else:
        all_records = []
        current_record = None
    
    # If user_id exists, fetch the current clock record for the user
    current_record = ClockRecord.query.filter_by(user_id=user_id, clock_out_time=None).first() if user_id else None
    
    # Render the dashboard template with the username and current record
    return render_template(
        "dashboard.html", 
        username=username,
        current_record=current_record,
        all_records=all_records
        )


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Ensure username was submitted.
        if not username:
            flash("Must provide an username.", "error")
            return render_template("login.html")

        # Ensure password was submitted.
        if not password:
            flash("Must provide a password", "error")
            return render_template("login.html") 
        
        # Query the database for username.
        user = User.query.filter_by(username=username).first()
        
        # Ensure username exists and password exist.
        if user is None or not check_password_hash(user.password, password):
            flash("Invalid username and/or password", "error")
            return render_template("login.html") 
        
        # Set session variable
        session["user_id"] = user.id
        session["username"] = username
        session["role"] = user.role
        
        if user.role == "Manager":
            return redirect(url_for("manager_dashboard"))
        else:
            return redirect("/dashboard")
    
    return render_template("login.html")

@app.route("/manager_dashboard")
@role_required("Manager")  
@login_required
def manager_dashboard():
    current_user = User.query.get(session.get('user_id'))
    all_users = User.query.filter(User.role != "Manager").all()

    employees = []
    
    for user in all_users:
        total_hours = 0.0  
        formatted_hours_list = []  # List to hold formatted hours for each record

        # Calculate total hours and formatted hours for the user's clock records
        for record in user.clock_records:
            if record.clock_out_time:  # Ensure there's a clock out time
                raw_hours = calculate_hours_worked(record.clock_in_time, record.clock_out_time)[1]  # Get raw hours
                total_hours += raw_hours  # Accumulate total hours
                formatted_hours_list.append(calculate_hours_worked(record.clock_in_time, record.clock_out_time)[0])  # Append formatted hours

        # If there are no clock-out records, set formatted_hours to "0.00"
        formatted_hours = sum([float(hours) for hours in formatted_hours_list]) if formatted_hours_list else "0.00"
        
        current_record = ClockRecord.query.filter_by(user_id=user.id, clock_out_time=None).first()
        status = "Clocked In" if current_record else "Clocked Out"
        
        employees.append({
            "id": user.id,
            "name": user.username,
            "role": user.role,
            "hours_worked": formatted_hours,  # Use the total formatted hours
            "status": status
        })

    unauthorized_users = User.query.filter_by(is_authorized=False).filter(User.id != current_user.id).all()

    return render_template('manager_dashboard.html', username=current_user.username, employees=employees, unauthorized_users=unauthorized_users)


@app.route("/register", methods=["POST", "GET"])
def register():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        role = request.form.get("role")

        # Basic checks for form inputs
        if not username or not password or not confirmation:
            flash("Need input fields.", "error")
            return render_template("registration.html")

        if password != confirmation:
            flash("Password or confirm password are mismatch.", "error")
            return render_template("registration.html")

        if not re.match(r"^[a-zA-Z0-9]{3,20}$", username):
            flash("Username must be 3-20 characters long and contain only letters and numbers.", "error")
            return render_template("registration.html")

        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return render_template("registration.html")

        if not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password) or not re.search(r"\d", password) or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            flash("Password must contain uppercase, lowercase, digit, and special character.", "error")
            return render_template("registration.html")

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists.", "error")
            return render_template("registration.html")
        
        # Check unique admim.
        if role == "Manager":
            unique_admin = User.query.filter_by(role="Manager").first()
            if unique_admin:
                flash("This section already has a Admin.", "error")
                return render_template("registration.html")

        # Hash the password and add new user
        hash_password = generate_password_hash(password)
        new_user = User(username=username, password=hash_password, role=role, is_authorized=False)
        

        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("dashboard"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred. Please try again.", "error")
            return render_template("registration.html")

    return render_template("registration.html")
  

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/clock_in", methods=["POST"])
@login_required
def clock_in():
    # Get user ID from the session
    user_id = session.get("user_id")
    
    # Check if the user is logged in
    if not user_id:
        flash("You need to log in.")
        return redirect("/login")
    # Retrieve the user from the database
    
    user = User.query.get(user_id)
    
    # Allow clock-in for Manager without authorization
    if user.role != "Manager" and not user.is_authorized:
        flash("You are not authorized to clock in.", "error")
        return redirect("/dashboard")
    
    
    # Check for an active clock-in record
    active_record = ClockRecord.query.filter_by(user_id=user_id, clock_out_time=None).first()
    
    # Handle active clock-in
    if active_record:
        flash("You are already clocked in.", "Sucess")
        return redirect("/dashboard")
    
    # Create a new ClockRecord with the current time
    new_record = ClockRecord(user_id=user_id, clock_in_time=datetime.now())  # Use datetime object, not isoformat
    db.session.add(new_record)
    db.session.commit()
    
    flash("Clocked in successfully!", "Sucess")
    return redirect("/dashboard")


@app.route("/clock_out", methods=["POST"])
@login_required
def clock_out():
    user_id = session.get("user_id")
    
    if not user_id:
        return redirect("/login")
    
    # Find the active clock-in record for the user
    active_record = ClockRecord.query.filter_by(user_id=user_id, clock_out_time=None).first()
    
    if not active_record:
        flash("You need to clock in first.")
        return redirect("/dashboard")
    
    # Set Clock-Out Time.
    active_record.clock_out_time = datetime.now()
    db.session.commit()
    
    flash("Clocked out successfully!")
    return redirect("/dashboard")

@app.route("/authorize_user/<int:user_id>", methods=["POST"])
@role_required("Manager")
@login_required
def authorize_user(user_id):
    user = User.query.get(user_id)
    
    # Ensure the user is an employee
    if user and user.role != "Manager":  
        user.is_authorized = True
        db.session.commit()
        flash("User authorized successfully.")
    else:
        flash("User not found or not an employee.")
    
    return redirect(url_for("manager_dashboard"))

@app.route("/not_authorize_user/<int:user_id>", methods=["POST"])
@role_required("Manager")
@login_required
def not_authorize_user(user_id):
    user = User.query.get(user_id)
    # Ensure the user is an employee
    if user and user.role != "Manager":  
        user.is_authorized = False
        db.session.commit()
        flash("User Not authorized successfully.")
    else:
        flash("User not found or not an employee.")
    
    return redirect(url_for("manager_dashboard"))

@app.route("/deleting_user/<int:user_id>", methods=["POST"])
@role_required("Manager")
@login_required
def deleting_user(user_id):
    delete_user = User.query.get(user_id)
    
    if not delete_user:
        flash("User not found.")
        return redirect(url_for("manager_dashboard"))

    try:
        # Delete the user's associated clock records first
        ClockRecord.query.filter_by(user_id=user_id).delete()
        
        # Now delete the user from the database
        db.session.delete(delete_user)
        db.session.commit()
        
        flash("User deleted successfully.")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while trying to delete the user.")
    
    return redirect(url_for("manager_dashboard"))


    
if __name__ == "__main__":
    with app.app_context():
        ###db.drop_all()    # This will drop the db.
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)  # Enable debug mode for easier debugging
    
