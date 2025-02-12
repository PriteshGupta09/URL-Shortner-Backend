from flask import Flask, jsonify
from app.configs.database import db
from app.services.email import mail
from app.configs.setting import Config
from app.extension import jwt, cors
from app.routes.auth_routes import auth_bp
from app.routes.link_routes import link_gener
from app.models.link import Link

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.configs.setting")
    app.config.from_object(Config)
    # confoigure Send Email
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = "gpritesh9988@gmail.com"
    app.config["MAIL_PASSWORD"] = "uxft vsdw djmv eskw"
    app.config["MAIL_DEFAULT_SENDER"] = "priteshgupta032@gmail.com"
    mail.init_app(app)
    # Initialize database
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, origins=["http://localhost:5173"], supports_credentials=True)  # Allow credentials in CORS requests

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(link_gener, url_prefix="/api/link")

    @app.route('/<shortlink>', methods=['GET'])
    def open_site(shortlink):
        shorturl = f'https://{shortlink}'
        link = Link.query.filter_by(shortlink=shorturl).first()
        link.clicks += 1
        db.session.commit()
        originalLink = link.originalLink
        return jsonify({"message": originalLink}), 201
    
    @app.route("/")
    def hello_world():
        return "<p>Hello, World!</p>"

    return app
