# ClockWork
#### Video Demo:  <[ClockWork](https://www.youtube.com/watch?v=Ewos94aemK8&t=6s)>
### ClockWork is a clock-in/clock-out management system, designed to streamline employee attendance tracking for small businesses. Built with Flask, SQLAlchemy, and HTML/CSS, this project serves as a straightforward solution for monitoring employee hours, including manager oversight and role-based access.


# Features
## Employee Clock-In/Clock-Out
### Employees can easily log their work hours by clocking in and out. Only authorized employees can clock in, ensuring that each clock-in is manager-approved for added security.

## Manager/Admin Roles

### Admin Role: Only one admin/manager can register, making this a unique account with privileges to manage Workers, simply allowing or not-allowing. Managers/admin can clock in and out without requiring authorization and can approve other employees’ requests to access the system.

# Dashboard Views
## Each role has a tailored dashboard:

### Employee Dashboard: Displays hours worked in a user-friendly format.
### Manager/admin Dashboard: Includes hours worked by each team member, **with hours formatted correctly**.
### Managers are responsible for authorizing employees to ensure that only approved personnel to clock-in.


## Usage
### Register an Admin: Create a unique admin account, which will have exclusive access.
### Employee Clock-In/Clock-Out: Employees can clock in only if a manager has authorized them, providing a secure way to track attendance.

## Future Plans
### This project is currently a functional prototype, with plans to expand it into a comprehensive attendance tracking system:

### Mobile Application: Transforming ClockWork into a cross-platform mobile app for easier access.
### Advanced Reporting: Adding options for exporting data and generating reports.
### Enhanced Roles and Permissions: Additional roles, such as Supervisor or HR, with specific access permissions.

# Contributing
## Contributions are welcome! If you have ideas or find any issues, feel free to open a pull request or file an issue.