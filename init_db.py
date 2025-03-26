from app import create_app, db
from app.models import User, UserPreference, Source

def init_database():
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if we need to create a default user
        if not User.query.first():
            # Create default user
            user = User(username='default_user')
            db.session.add(user)
            db.session.flush()  # This ensures the user has an ID
            
            # Create sample preference
            preference = UserPreference(
                user_id=user.id,
                area_of_interest='Technology',
                timeframe='daily'
            )
            db.session.add(preference)
            db.session.flush()  # This ensures the preference has an ID
            
            # Add sample source
            source = Source(
                preference_id=preference.id,
                url='https://example.com/tech-news'
            )
            db.session.add(source)
            
            # Commit changes
            try:
                db.session.commit()
                print("Database initialized with default data")
            except Exception as e:
                db.session.rollback()
                print(f"Error initializing database: {str(e)}")
        else:
            print("Database already contains data")

if __name__ == '__main__':
    init_database()