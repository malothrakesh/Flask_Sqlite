from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.book import Book
from flask_login import login_required, current_user
from math import ceil
from sqlalchemy import or_
book_bp = Blueprint('book_bp', __name__)
from app.models.forms import BookForm


@book_bp.route('/')
def home():
    return render_template('home.html')

@book_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Add logic to check credentials here
        if not username or not password:  # Example check
            error = "Invalid credentials, please try again."
        else:
            # Logic for successful login
            return redirect(url_for('book_bp.book_list'))
    return render_template('login.html', error=error)

@book_bp.route('/books')
def book_list():
    page = int(request.args.get('page', 1))
    per_page = 5
    next_page = page + 1
    search = request.args.get('search', '').strip()

    query = Book.query

    if search:
        search_filter = or_(
            Book.title.ilike(f'%{search}%'),
            Book.author.ilike(f'%{search}%'),
            Book.genre.ilike(f'%{search}%')
        )
        query = query.filter(search_filter)

    total_books = query.count()
    total_pages = ceil(total_books / per_page)
    books = db.paginate(query, page=page, per_page=per_page)

    return render_template(
        'book_list.html',
        books=books.items,
        page=page,
        next_page=next_page,
        total_pages=total_pages,
        search=search
    )

@book_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_book():
    form = BookForm()

    if request.method == 'POST' and form.validate_on_submit():
        if not current_user.is_admin:
            flash('Only admins can add books.')
            return redirect(url_for('book_bp.book_list'))

        new_book = Book(
            title=form.title.data,
            author=form.author.data,
            genre=form.genre.data
        )
        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully!')
        return redirect(url_for('book_bp.book_list'))

    return render_template('add_book.html', form=form)


@book_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    book = Book.query.get_or_404(id)
    form = BookForm()
    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']

        db.session.commit()
        flash('Book updated successfully!')
        return redirect(url_for('book_bp.book_list'))

    return render_template('edit_book.html', book=book, form= form)


@book_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    book = Book.query.get_or_404(id)

    db.session.delete(book)
    db.session.commit()

    flash('Book deleted successfully!')
    return redirect(url_for('book_bp.book_list'))
