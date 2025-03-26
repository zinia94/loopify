from flask import Flask
from app.models.user import User
from app.config import get_config
from .routes import init_routes 
from app.database.db import db, init_db
from app.database.seed import insert_db_samples
from app.database.manager import DatabaseManager

def create_app():
    app = Flask(__name__)
    
    # Load config from config folder
    app.config.from_object(get_config())

    # Initialize extensions
    init_db(app)
    
    app.db = DatabaseManager()

    with app.app_context():
        db.create_all()
        
        # Check if the database is empty and insert sample data
        if db.session.query(db.exists().where(User.id == 1)).scalar() == False:
            insert_db_samples()
    
    init_routes(app)

    return app
