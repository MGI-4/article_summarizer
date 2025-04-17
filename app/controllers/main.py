from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.preference import Preference
from app.utils.perplexity_api import get_article_summaries
from app import db
from datetime import datetime

# Create a Blueprint for main routes
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Redirect to home page if logged in, otherwise to login page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    return redirect(url_for('auth.login'))

@main_bp.route('/home')
@login_required
def home():
    """Handle home page with article summaries"""
    
    # Get user's most recent preference
    preference = Preference.query.filter_by(user_id=current_user.id).order_by(Preference.updated_at.desc()).first()
    
    # If no preferences exist, redirect to input page
    if not preference:
        flash('Please set your article preferences first.', 'info')
        return redirect(url_for('main.input'))
    
    # Get article summaries based on user preferences
    summaries = get_article_summaries(preference)
    
    return render_template('main/home.html', preference=preference.to_dict(), summaries=summaries)

@main_bp.route('/input', methods=['GET', 'POST'])
@login_required
def input():
    """Handle input page for setting preferences"""
    
    # Get user's existing preference if any
    existing_preference = Preference.query.filter_by(user_id=current_user.id).order_by(Preference.updated_at.desc()).first()
    
    # Process form submission
    if request.method == 'POST':
        area_of_interest = request.form.get('area_of_interest')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        sources = request.form.getlist('source')  # Get all sources as list
        
        # Validate form data
        if not area_of_interest or not start_date or not end_date or not sources:
            flash('Please fill out all fields', 'error')
            return render_template('main/input.html', preference=existing_preference)
        
        try:
            # Convert string dates to date objects
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # Validate date range
            if start_date > end_date:
                flash('Start date cannot be after end date', 'error')
                return render_template('main/input.html', preference=existing_preference)
            
        except ValueError:
            flash('Invalid date format', 'error')
            return render_template('main/input.html', preference=existing_preference)
        
        if existing_preference:
            # Update existing preference
            existing_preference.area_of_interest = area_of_interest
            existing_preference.start_date = start_date
            existing_preference.end_date = end_date
            existing_preference.set_sources(sources)
            db.session.commit()
            flash('Preferences updated successfully!', 'success')
        else:
            # Create new preference
            new_preference = Preference(
                user_id=current_user.id,
                area_of_interest=area_of_interest,
                start_date=start_date,
                end_date=end_date,
                sources=sources
            )
            db.session.add(new_preference)
            db.session.commit()
            flash('Preferences saved successfully!', 'success')
        
        return redirect(url_for('main.home'))
    
    # Render input form for GET request
    return render_template('main/input.html', preference=existing_preference.to_dict() if existing_preference else None)

@main_bp.route('/update_timeframe', methods=['POST'])
@login_required
def update_timeframe():
    """Update the timeframe for a preference"""
    
    preference_id = request.form.get('preference_id')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    
    # Validate input
    if not preference_id or not start_date or not end_date:
        flash('Missing required fields', 'error')
        return redirect(url_for('main.home'))
    
    # Get the preference
    preference = Preference.query.get(preference_id)
    
    # Check if preference exists and belongs to current user
    if not preference or preference.user_id != current_user.id:
        flash('Preference not found', 'error')
        return redirect(url_for('main.home'))
    
    try:
        # Convert string dates to date objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Validate date range
        if start_date > end_date:
            flash('Start date cannot be after end date', 'error')
            return redirect(url_for('main.home'))
        
        # Update preference
        preference.start_date = start_date
        preference.end_date = end_date
        db.session.commit()
        
        flash('Timeframe updated successfully!', 'success')
    except ValueError:
        flash('Invalid date format', 'error')
    
    return redirect(url_for('main.home'))