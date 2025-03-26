from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from app.models import User, UserPreference, Source, db
from app.utils.article_utils import ArticleFetcher, PerplexityAPI
import logging
import requests
import json

logger = logging.getLogger(__name__)
main = Blueprint('main', __name__)

@main.route('/')
def home():
    # Get current user's preferences
    user = User.query.first()
    if not user or not user.preferences:
        logger.info("No user preferences found, redirecting to preferences page")
        return redirect(url_for('main.preferences'))
    
    # Get the latest preference
    preference = user.preferences[-1]
    logger.info(f"Found user preference - Area: {preference.area_of_interest}, Timeframe: {preference.timeframe}")
    
    # Get all sources for this preference
    sources = Source.query.filter_by(preference_id=preference.id).all()
    
    if not sources:
        logger.warning("No sources found for the current preference")
        flash('No sources found. Please add some sources in your preferences.', 'warning')
        return redirect(url_for('main.preferences'))
    
    source_urls = [source.url for source in sources]
    logger.info(f"Processing {len(source_urls)} sources: {source_urls}")
    
    # Initialize article fetcher
    fetcher = ArticleFetcher(current_app.config.get('PERPLEXITY_API_KEY'))
    
    # Fetch and summarize articles
    try:
        logger.info(f"Starting article processing for area: {preference.area_of_interest}")
        articles = fetcher.process_articles(
            source_urls, 
            preference.area_of_interest,
            preference.timeframe
        )
        
        if not articles:
            logger.warning("No articles found for the given preferences")
            flash('No articles found for your preferences. Try different sources or topics.', 'warning')
        else:
            logger.info(f"Successfully processed {len(articles)} summaries")
    except Exception as e:
        logger.error(f"Error processing articles: {str(e)}", exc_info=True)
        articles = []
        flash('Error fetching articles. Please try again later.', 'error')
    
    return render_template('home.html', 
                         articles=articles, 
                         preference=preference,
                         sources=sources)

@main.route('/preferences', methods=['GET', 'POST'])
def preferences():
    if request.method == 'POST':
        try:
            # Get form data
            area_of_interest = request.form.get('area_of_interest')
            timeframe = request.form.get('timeframe')
            sources = request.form.getlist('sources')  # Get multiple URLs
            
            # Basic validation
            if not all([area_of_interest, timeframe]) or not sources:
                flash('Please fill in all required fields', 'error')
                return redirect(url_for('main.preferences'))
            
            # Get or create user (in a real app, use proper user authentication)
            user = User.query.first()
            if not user:
                user = User(username='default_user')
                db.session.add(user)
                db.session.flush()
            
            # Create new preference
            preference = UserPreference(
                user_id=user.id,
                area_of_interest=area_of_interest,
                timeframe=timeframe
            )
            db.session.add(preference)
            db.session.flush()
            
            # Add sources
            for url in sources:
                if url.strip():  # Skip empty URLs
                    source = Source(
                        preference_id=preference.id,
                        url=url.strip()
                    )
                    db.session.add(source)
            
            db.session.commit()
            flash('Preferences saved successfully!', 'success')
            return redirect(url_for('main.home'))
            
        except Exception as e:
            logger.error(f"Error saving preferences: {str(e)}")
            db.session.rollback()
            flash(f'Error saving preferences: {str(e)}', 'error')
            return redirect(url_for('main.preferences'))
    
    # For GET request, show the form
    return render_template('input.html')

@main.route('/update_timeframe', methods=['POST'])
def update_timeframe():
    try:
        timeframe = request.form.get('timeframe')
        preference_id = request.form.get('preference_id')
        
        logger.info(f"Updating timeframe to {timeframe} for preference {preference_id}")
        
        preference = UserPreference.query.get(preference_id)
        if preference:
            preference.timeframe = timeframe
            db.session.commit()
            
            # Fetch new articles
            sources = Source.query.filter_by(preference_id=preference.id).all()
            source_urls = [s.url for s in sources]
            
            logger.info(f"Processing {len(source_urls)} sources after timeframe update")
            
            fetcher = ArticleFetcher(current_app.config.get('PERPLEXITY_API_KEY'))
            articles = fetcher.process_articles(
                source_urls,
                preference.area_of_interest,
                preference.timeframe
            )
            
            if not articles:
                logger.warning("No articles found after timeframe update")
                return jsonify({
                    'success': False,
                    'error': 'No articles found for the updated timeframe'
                })
            else:
                logger.info(f"Successfully processed {len(articles)} summaries after timeframe update")
                
            return jsonify({
                'success': True,
                'articles': articles
            })
        else:
            logger.error(f"Preference with ID {preference_id} not found")
            return jsonify({
                'success': False,
                'error': 'Preference not found'
            })
    except Exception as e:
        logger.error(f"Error updating timeframe: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        })

@main.route('/verify_api')
def verify_api():
    api_key = current_app.config.get('PERPLEXITY_API_KEY')
    
    # Basic request with simplified sonar model format
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "user",
                "content": "Give me a one-sentence test response."
            }
        ],
        "max_tokens": 200
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload
        )
        
        # Return detailed debug info
        return jsonify({
            'status_code': response.status_code,
            'api_key_format': api_key[:7] + '...' if api_key else None,
            'response_text': response.text,
            'headers_sent': dict(headers),
            'payload_sent': payload
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'api_key_format': api_key[:7] + '...' if api_key else None
        })