from app import db
import pymysql
from flask import current_app
import os

def init_db():
    """
    Initialize the database by creating tables if they don't exist.
    This function should be called when the application starts.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create all tables defined in models
        db.create_all()
        return True
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        return False

def get_db_connection():
    """
    Get a direct connection to the MySQL database.
    Useful for executing complex queries that aren't easily done with SQLAlchemy.
    
    Returns:
        Connection: A pymysql connection object
    """
    try:
        # Get database configuration from environment variables
        db_username = current_app.config.get('SQLALCHEMY_DATABASE_URI').split(':')[1][2:]
        db_password = current_app.config.get('SQLALCHEMY_DATABASE_URI').split(':')[2].split('@')[0]
        db_host = current_app.config.get('SQLALCHEMY_DATABASE_URI').split('@')[1].split('/')[0]
        db_name = current_app.config.get('SQLALCHEMY_DATABASE_URI').split('/')[-1]
        
        # Create connection
        connection = pymysql.connect(
            host=db_host,
            user=db_username,
            password=db_password,
            database=db_name,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        return connection
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        return None

def execute_query(query, params=None):
    """
    Execute a SQL query directly on the database.
    
    Args:
        query (str): SQL query to execute
        params (tuple, optional): Parameters for the query. Defaults to None.
    
    Returns:
        list: Query results as a list of dictionaries
    """
    connection = get_db_connection()
    results = []
    
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or ())
                results = cursor.fetchall()
            connection.commit()
        except Exception as e:
            print(f"Error executing query: {str(e)}")
        finally:
            connection.close()
    
    return results

def create_database_schema():
    """
    Create the database schema for the application.
    This is useful for initial setup or in a migration script.
    
    Returns:
        bool: True if successful, False otherwise
    """
    connection = None
    try:
        # Get database configuration from environment variables
        db_username = os.environ.get('DB_USERNAME', 'root')
        db_password = os.environ.get('DB_PASSWORD', '')
        db_host = os.environ.get('DB_HOST', 'localhost')
        db_name = os.environ.get('DB_NAME', 'article_summarizer')
        
        # Connect to MySQL server without specifying database
        connection = pymysql.connect(
            host=db_host,
            user=db_username,
            password=db_password,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            
            # Use the database
            cursor.execute(f"USE {db_name}")
            
            # Create users table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(64) NOT NULL UNIQUE,
                email VARCHAR(120) NOT NULL UNIQUE,
                password_hash VARCHAR(128) NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME NULL,
                INDEX idx_username (username),
                INDEX idx_email (email)
            ) ENGINE=InnoDB;
            """)
            
            # Create preferences table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                area_of_interest VARCHAR(100) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                sources TEXT NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id)
            ) ENGINE=InnoDB;
            """)
            
        connection.commit()
        return True
    
    except Exception as e:
        print(f"Error creating database schema: {str(e)}")
        return False
    
    finally:
        if connection:
            connection.close()