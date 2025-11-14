# models.py
from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


# ----------------------
# Scraped Data Model
# ----------------------
class ScrapedData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(512))
    url = db.Column(db.String(1024))
    meta_description = db.Column(db.Text)
    meta_keywords = db.Column(db.Text)
    first_image = db.Column(db.String(1024))
    images = db.Column(db.Text)
    headings = db.Column(db.Text)
    links_count = db.Column(db.Integer)
    domain = db.Column(db.String(255))
    content_snippet = db.Column(db.Text)
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'meta_description': self.meta_description,
            'meta_keywords': self.meta_keywords,
            'first_image': self.first_image,
            'images': self.images,
            'headings': self.headings,
            'links_count': self.links_count,
            'domain': self.domain,
            'content_snippet': self.content_snippet,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None
        }


# ----------------------
# User Model (Fixed)
# ----------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)

    # FIXED — enough length for scrypt hash
    password_hash = db.Column(db.String(500), nullable=False)

    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        # using scrypt (stronger)
        self.password_hash = generate_password_hash(password, method="scrypt")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
