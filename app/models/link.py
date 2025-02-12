from app.configs.database import db

class Link(db.Model):
    __tablename__ = 'links'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    originalLink = db.Column(db.String, nullable=False)
    shortlink = db.Column(db.String, nullable=False, unique=True)
    qrcode = db.Column(db.String, nullable=False, unique=True)
    createdat = db.Column(db.String, nullable=False,)
    clicks = db.Column(db.Integer, nullable=False, default= 0)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    @property
    def json(self):
        return {'id': self.id,'originalLink': self.originalLink, 'shortlink': self.shortlink, 'qrcode': self.qrcode, 'createdat': self.createdat, 'clicks': self.clicks, 'user_id': self.user_id}
