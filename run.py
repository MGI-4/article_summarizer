from app import create_app, db
from app.models import User, UserPreference, Source

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'UserPreference': UserPreference,
        'Source': Source
    }

def init_db():
    with app.app_context():
        db.create_all()
        
        # Create default user if none exists
        if not User.query.first():
            user = User(username='default_user')
            db.session.add(user)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)