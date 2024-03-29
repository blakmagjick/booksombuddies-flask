import models

from flask import Blueprint, request, jsonify, session, redirect
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user, login_required
from playhouse.shortcuts import model_to_dict

from auth import can_update, unauthorized

users = Blueprint('users', 'users')

@users.route('/', methods=['GET'])
@login_required
def get_users():
    result =  models.User.select()

    user_dicts = [model_to_dict(user) for user in result]

    return jsonify (
        data=user_dicts,
        message=f"Successfully found {len(user_dicts)} users",
        status=200
    ), 200

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
            password=pw_hash,
            profilemade=False
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
    print(payload)
    payload['username'] = payload['username'].lower()

    try:
        user = models.User.get(models.User.username == payload['username'])

        user_dict = model_to_dict(user)

        password_is_good = check_password_hash(user_dict['password'], payload['password'])

        if (password_is_good):
            session.permanent = True
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

@users.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()

    return jsonify (
        data={},
        message='Successfully logged out',
        status=200
    ), 200

#DELETE ROUTE
@users.route('/<id>', methods=['DELETE'])
def delete_user(id):
    delete_user = models.User.delete().where(models.User.id == id).execute()

    return jsonify (
        data={},
        message=f"Successfully deleted user",
        status=200
    ), 200

#FOR TESTING
@users.route('/who_is_logged_in', methods=['GET'])
def who_is_logged_in():
    print(current_user)
    if not current_user.is_authenticated:
        return jsonify (
            data={},
            message='No user is currently logged in',
            status=401
        ), 401
    else: 
        user_dict = model_to_dict(current_user)
        user_dict.pop('password')

        return jsonify (
            data=user_dict,
            message=f"Currently logged in as user: {user_dict['username']}",
            status=200
        ), 200

#ALL USER PROFILES
@users.route('/profiles', methods=['GET'])
@login_required
def all_profiles():
    result = models.UserProfile.select()
    profile_dicts = [model_to_dict(profile) for profile in result]

    for profile_dict in profile_dicts:
        profile_dict['username'].pop('password')
    
    return jsonify (
        data=profile_dicts,
        message=f"Successfully found {len(profile_dicts)} profiles",
        status=200
    ), 200

#USER PROFILE CREATE
@users.route('/profile/new', methods=['POST'])
@login_required
def new_profile():
    payload = request.get_json()

    new_profile = models.UserProfile.create(**payload, username=current_user.id)
    user_to_update = new_profile.username.id
    models.User.get_by_id(user_to_update).update(profilemade=True).execute()

    profile_dict = model_to_dict(new_profile)
    profile_dict['username'].pop('password')

    return jsonify (
        data=profile_dict,
        message='Successfully created new profile!',
        status=201 
    ), 201

#USER PROFILE SHOW
@users.route('/profile/<id>', methods=['GET'])
@login_required
def get_profile(id):
    profile = models.UserProfile.get_by_id(id)
    return jsonify (
        data=model_to_dict(profile),
        message='*party emoji*',
        status=200
    ), 200
        
#USER PROFILE EDIT
@users.route('/profile/<id>', methods=['PUT'])
@login_required
def edit_profile(id):
    payload = request.get_json()

    # if not can_update(id):
    #     return unauthorized()

    models.UserProfile.update(**payload).where(models.UserProfile.id == id).execute()

    return jsonify (
        data=model_to_dict(models.UserProfile.get_by_id(id)),
        message='User profile has been updated',
        status=200
    ), 200

#USER PROFILE DELETE
@users.route('/profile/<id>', methods=['DELETE'])
@login_required
def delete_profile(id):

    if not can_update(id):
        return unauthorized()
        
    delete_profile = models.UserProfile.delete().where(models.UserProfile.id == id).execute()
    update_user = models.User.update(profilemade=False).where(models.User.id == id).execute()

    return jsonify (
        data={},
        message=f"Successfully deleted user profile",
        status=200
    ), 200