import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def drinks():
    try:
        allDrinks = []
        drinks = Drink.query.all()
        for drink in drinks:
            allDrinks.append(drink.short())
        # short(drinks)
        # print(drink )
        return jsonify({
            "status": 200,
            "drinks": allDrinks
        })
    except:
        abort(404)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks')
def drinks_detail(payload):
    try:
        allDrinks = []
        drinks = Drink.query.all()
        for drink in drinks:
            allDrinks .append(drink.long()) 
        # short(drinks)
        print(drink )
        return jsonify({
            "status": 200,
            "drinks": allDrinks
        })
    except:
        abort(404)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth("post:drinks")
def post_drinks(payload):
    try:
        title = request.get_json()['title']
        recipe = json.dumps(request.get_json()['recipe'])
        print(request.get_json())

        if title is None or recipe is None:
            abort(422)
        drink = Drink(
            title=title,
            recipe=recipe
            )
        drink_list = [ drink.long() ]
        print(drink)
        drink.insert()

        return jsonify({
                'success': True,
                'drinks' : drink_list,
            })
    except:
        abort(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update(payload, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if "title" in request.get_json():
            drink.title = request.get_json()['title']
        if "recipe" in request.get_json():
            drink.recipe = json.dumps(request.get_json()['recipe'])
        drink_list = [ drink.long()]
        drink.update()
        return jsonify({
            'success': True,
            'drinks' : drink_list,
        })
    except:
        abort(422)
'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        # print(drink)
        # if drink is None:
        #     abort(422)
        drink.delete()

        return jsonify({
            'success': True,
            'deleted': drink.id
        })
    except:
        abort(422)

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def resouce_not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def authError(authError):
    return jsonify({
        "success": False,
        "error": authError.status_code,
        "message": authError.error['description']
    }), authError.status_code