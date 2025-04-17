from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db
from datetime import datetime
from werkzeug.urls import url_parse

# Create a Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    
    # If user is already authenticated, redirect to home page
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    # Process login form submission
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = True if request.form.get('remember_me') else False
        
        # Validate form data
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('auth/login.html')
        
        # Look up user in database
        user = User.query.filter_by(username=username).first()
        
        # Verify user and password
        if user is None or not user.check_password(password):
            flash('Invalid username or password', 'error')
            return render_template('auth/login.html')
        
        # Log in the user
        login_user(user, remember=remember_me)
        
        # Update last login time
        user.update_last_login()
        
        # Redirect to the page the user was trying to access or to home page
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.home')
        
        return redirect(next_page)
    
    # Render login form for GET request
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    
    # If user is already authenticated, redirect to home page
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    # Process registration form submission
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate form data
        if not username or not email or not password or not confirm_password:
            flash('Please fill out all fields', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('auth/register.html')
        
        # Create new user
        user = User(username=username, email=email, password=password)
        
        # Add user to database
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    # Render registration form for GET request
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))