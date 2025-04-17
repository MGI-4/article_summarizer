from app import app
from app.utils.db_helper import init_db
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the database if needed
init_db()

if __name__ == "__main__":
    # Get port from environment variable or use default 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Start the Flask application
    # In development mode, debug=True enables auto-reload on file changes
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    
    app.run(
        host='0.0.0.0',  # Makes the server accessible from any device on the network
        port=port,
        debug=debug_mode
    )