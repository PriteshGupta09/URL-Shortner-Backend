from app.configs.database import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    isVerified = db.Column(db.Boolean, unique=False, default=False)
    token = db.Column(db.String(255), unique=True, nullable=True)
    verification_token = db.Column(db.String(64), unique=True, nullable=True)
    verification_token_expiry = db.Column(db.DateTime, nullable=True)
    reset_password_token = db.Column(db.String(64), unique=True, nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    links = db.relationship("Link", backref="user", lazy=True, cascade="all, delete-orphan")
    
    @property
    def json(self):
        return {'id': self.id,'email': self.email, 'isVerified': self.isVerified, 'links': [link.json for link in self.links] if self.links else []}
