from enum import unique

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    birth_date = db.Column(db.String, nullable=False)
    date_of_death = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f"<Author(id={self.id}, name='{self.name}')>"

    def __str__(self):
        life_span = f"{self.birth_date}–{self.date_of_death if self.date_of_death else 'present'}"
        return f"{self.name} ({life_span})"


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)

    author = db.relationship('Author', backref=db.backref('books', lazy=True))

    def __repr__(self):
        return f"<Book id={self.id}, title='{self.title}'>"

    def __str__(self):
        return f"{self.title} ({self.publication_year}) by {self.author.name if self.author else 'Unknown'}"