from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

from app.models.bookmodels import rentals


class Author(db.Model):
    __tablename__ = 'authors'

    author_id = db.Column(db.Integer, primary_key=True)
    author_data = db.Column(db.String(50), nullable=False)
    books_authored = db.Column(db.Integer, nullable=False)

    books = db.relationship('Book', backref='author', lazy=True)

    def __init__(self, details):
        self.author_data = details
        self.books_authored = 0

    def save(self):
        db.session.add(self)
        db.session.commit()


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)

    books = db.relationship('Book', secondary=rentals,
                            backref=db.backref('users', lazy='dynamic'))

    def __init__(self, first_name, last_name, username, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email
        self.is_admin = False
        self.password_hash = generate_password_hash(password)

    def save(self):
        """
        Add user to database
        """
        db.session.add(self)
        db.session.commit()

    @property
    def password(self):
        """
        Prevent pasword from being accessed
        """
        raise AttributeError('password is not a readable attribute.')

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User: {}>'.format(self.username)

# Set up user_loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Admin(User):

    def __init__(self, first_name, last_name, username, email, password):
        super().__init__(first_name, last_name, username, email, password)
        self.admin = True

    def save(self):
        super().save()
