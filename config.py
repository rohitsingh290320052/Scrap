class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:1234@localhost/flask_scraper_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "secret123"
