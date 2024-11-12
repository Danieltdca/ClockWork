from functools import wraps
from flask import session, request, redirect, url_for, flash
from models import ClockRecord

#Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Manager Decorator.
def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("You need to log in first.")
                return redirect(url_for('login'))
            
            user_role = session.get('role')
            if user_role != required_role:
                flash("You do not have permission to access this page.")
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def calculate_current_hours(clock_in_time, clock_out_time):
    if clock_in_time and clock_out_time:
        # Calculate the duration in total seconds
        duration = (clock_out_time - clock_in_time).total_seconds()
        # Split in hours and minutes for a better UI.
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)

        # Return both formatted string and total hours as float
        total_hours = duration / 3600 
        formatted_hours = f"{hours}:{minutes:02d}"
        return formatted_hours, total_hours
    return "0:00", 0.0

def calculate_hours_worked(clock_in_time, clock_out_time):
    if clock_in_time and clock_out_time:
        duration = clock_out_time - clock_in_time
        total_hours = duration.total_seconds() / 3600  # Convert to hours
        formatted_hours = '{:.2f}'.format(total_hours)  # Format to two decimal places
        return formatted_hours, total_hours  # Return both formatted and raw hours
    return "0.00", 0  # Return "0.00" for formatted hours and 0 for total hours if not clocked out
