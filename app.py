from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from data_models import db, Author, Book
import os

app = Flask(__name__)

cwd = os.getcwd()
db_file = os.path.join(cwd, "data", "library.sqlite")

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_file}'
#app.config['SQLALCHEMY_ECHO'] = True
db.init_app(app)


@app.route('/', methods=['GET'])
def home():
  sort = request.args.get('sort', 'title')
  q_text = request.args.get('q', '').strip()
  q = Book.query.join(Book.author)

  if q_text:
    pattern = f"%{q_text}%"
    q = q.filter(Book.title.ilike(pattern))

  if sort == 'author':
    q = q.order_by(Author.name.asc(), Book.title.asc())
  else:
    q = q.order_by(Book.title.asc(), Author.name.asc())

  books = q.all()

  for book in books:
    book.cover_url = f"https://covers.openlibrary.org/b/isbn/{book.isbn}-M.jpg"

  message = None
  if q_text and not books:
    message = f'No books found matching "{q_text}".'

  return render_template('home.html',
                         books=books,
                         message=message)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
  if request.method == 'GET':
    return render_template("add_author.html")

  name = request.form.get('name')
  birth_date = request.form.get('birthdate')
  date_of_death = request.form.get('date_of_death')

  if not date_of_death:
    date_of_death = None

  try:
    author = Author(
      name=name,
      birth_date=birth_date,
      date_of_death=date_of_death
    )

    db.session.add(author)
    db.session.commit()

    data = {
      'message': f'added author {author}'
    }
  except Exception as e:
    data = {
      'message': f'error: {e}'
    }

  return render_template("add_author.html", **data)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'GET':
      authors = Author.query.all()
      return render_template('add_book.html', authors=authors)

    isbn = request.form.get('isbn')
    title = request.form.get('title')
    publication_year = request.form.get('publication_year')
    author_id = request.form.get('author_id')

    try:
      book = Book(
        isbn=isbn,
        title=title,
        publication_year=publication_year,
        author_id=author_id
      )

      db.session.add(book)
      db.session.commit()

      data = {
        'message': f'added book {book}'
      }
    except Exception as e:
      data = {
        'message': f'error: {e}'
      }

    authors = Author.query.all()
    return render_template('add_book.html', **data, authors=authors)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book is None:
      return render_template("home.html", message=f'no book with id {book_id} found')

    author = book.author

    db.session.delete(book)
    db.session.commit()

    if not author.books:
        db.session.delete(author)
        db.session.commit()
        message = (f"Deleted book “{book.title}” and author “{author.name}” (no remaining books).", "success")
    else:
        message = (f"Deleted book “{book.title}”.", "success")

    return render_template("home.html", message=message)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)



# with app.app_context():
#   db.create_all()