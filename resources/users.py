import models

from flask import Blueprint, request, jsonify
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user
from playhouse.shortcuts import model_to_dict

users = Blueprint('users', 'users')

@users.route('/register', methods=['POST'])
def register():
    payload = request.get_json()
    payload['email'] = payload['email'].lower()
    payload['username'] = payload['username'].lower()

    try:
        models.User.get(models.User.username == payload['username'])

        return jsonify(
            data = {},
            message=f"A user with the username {payload['username']} already exists",
            status=401
        ), 401

    except models.DoesNotExist:
        pw_hash = generate_password_hash(payload['password'])
        created_user = models.User.create(
            username=payload['username'],
            email=payload['email'],
            password=pw_hash
        )

        login_user(created_user)

        created_user_dict = model_to_dict(created_user)

        created_user_dict.pop('password')

        return jsonify(
            data=created_user_dict,
            message=f"Successfully registered user {created_user_dict['username']}",
            status=201
        ), 201

@users.route('/login', methods=['POST'])
def login():
    payload = request.get_json()
    payload['username'] = payload['username'].lower()

    try:
        user = models.User.get(models.User.username == payload['username'])

        user_dict = model_to_dict(user)

        password_is_good = check_password_hash(user_dict['password'], payload['password'])

        if (password_is_good):
            login_user(user)

            user_dict.pop('password')

            return jsonify (
                data=user_dict,
                message=f"Successfully logged in as {user_dict['username']}",
                status=200
            ), 200
        else:
            print('Email is no good')

            return jsonify (
                data={},
                message='Email or password is incorrect',
                status=401
            ), 401

    except models.DoesNotExist:
        print('Email not found')

        return jsonify(
            data={},
            message='Email or password is incorrect',
            status=401
        ), 401



