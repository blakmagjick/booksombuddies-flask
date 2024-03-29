import models
import openlibrary
from flask import Blueprint, request, jsonify
from playhouse.shortcuts import model_to_dict
from flask_login import current_user, login_required

books = Blueprint('books', 'books')

# #INDEX ROUTE
# @books.route('/', methods=['GET'])
# @login_required
# def books_index():
#     result = models.Book.select()

#     book_dicts = [model_to_dict(book) for book in result]

#     current_user_book_dicts = [model_to_dict(book) for book in current_user.books]

#     # for book_dict in current_user_book_dicts:
#     #     book_dict['owner'].pop('password')

#     return jsonify (
#         data=current_user_book_dicts,
#         message=f"Successfully found {len(current_user_book_dicts)} books",
#         status=200
#     ), 200

# #CREATE ROUTE
# @books.route('/', methods=['POST'])
# def create_book():
#     payload = request.get_json()

#     new_book = models.Book.create(**payload)
#     print(new_book)

#     book_dict = model_to_dict(new_book)
#     # book_dict['owner'].pop('password')

#     return jsonify (
#         data=book_dict,
#         message='Successfully added book',
#         status=201
#     ), 201

# #SHOW ROUTE
# @books.route('/<id>', methods=['GET'])
# def show_one_book(id):
#     book = models.Book.get_by_id(id)
#     return jsonify (
#         data=model_to_dict(book),
#         message='*party emoji*',
#         status=200
#     ), 200

# #UPDATE ROUTE
# @books.route('/<id>', methods=['PUT'])
# def update_book(id):
#     payload = request.get_json()

#     models.Book.update(**payload).where(models.Book.id == id).execute()

#     return jsonify (
#         data=model_to_dict(models.Book.get_by_id(id)),
#         message='Book has been successfully updated',
#         status= 200
#     ), 200

# #DELETE ROUTE
# @books.route('/<id>', methods=['DELETE'])
# def delete_book(id):
#     delete_book = models.Book.delete().where(models.Book.id == id).execute()

#     return jsonify (
#         data={},
#         message=f"Successfully deleted book",
#         status=200
#     ), 200

#SEARCH ROUTE
@books.route('/search', methods=['GET'])
def search_title():
    title = request.args.get('title')

    if not title:
        return jsonify(
            data={},
            message=f'Title missing',
            status=400
        ), 400

    books, status = openlibrary.search(title)

    if not books:
        return jsonify(
            data={},
            message=f'Openlibrary failed',
            status=status
        ), 502

    for book in books:
        book['cover'] = openlibrary.cover(book)
        authors = book.get('author_name') #Open Library returns a list of authors
        book['author'] = ", ".join(authors) if authors else "Anonymous"
        book['isbn'] = book['isbn'][0] if book.get('isbn') else '' #Open Library returns a list of isbns

    # make sure all the books have covers
    books = [book for book in books if book['cover']]

    # return only the first 5 items
    books = books[:5]

    return jsonify(
        data={'books': books},
        message='Successfully found book',
        status=200
    ), 200