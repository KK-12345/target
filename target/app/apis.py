from flask import jsonify, Blueprint, make_response, request
from flask.views import MethodView
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from models import User
from target.settings.backend import DBBackend

from decorators import verify_token
from helper import DBUtility

urls = Blueprint('app_urls', __name__)


class ProductAPIView(MethodView):

    @verify_token
    def post(self):
        data = request.get_json()
        session = DBBackend().get_session()
        response = dict()
        response['status'] = 'failure'
        if not data.get('name'):
            response['data'] = "Product name is required."
            return make_response(jsonify(response)), 422
        response['data'] = 'Some error occurred. Please try again.'
        try:
            register_utility = DBUtility(session)
            product = register_utility.register_product(data)
            response['status'] = 'success'
            response['data'] = {"product_id": product.id}
            response_code = 201
            session.commit()
        except KeyError:
            response['data'] = "name missing"
            response_code = 422
        except AssertionError as ae:
            response['data'] = str(ae)
            response_code = 422
        except Exception as ex:
            response['data'] = "Something went wrong"
            response_code = 500
            response['status'] = 'failure'
            session.rollback()
        session.close()
        return make_response(jsonify(response)), response_code

    @verify_token
    def get(self):
        product_id = request.args.get('product_id', None)
        session = DBBackend().get_session()
        response = dict()
        response['status'] = 'failure'
        response_code = 422
        try:
            if product_id:
                product_id = int(product_id)
            register_utility = DBUtility(session)
            response['data'] = [product.serialize for product in register_utility.get_products(product_id)]
            response['status'] = 'success'
            response_code = 200
        except ValueError:
            response['data'] = 'Invalid Product id'
            return make_response(jsonify(response)), response_code
        except Exception as ex:
            response['data'] = "Something went wrong"
            response_code = 500
            response['status'] = 'failure'
        session.close()
        return make_response(jsonify(response)), response_code

    @verify_token
    def put(self):
        data = request.get_json()
        product_id = request.args.get('product_id')
        session = DBBackend().get_session()
        response_code = 422
        response = dict()
        response['status'] = 'failure'
        if not product_id:
            response['data'] = 'Product Id is missing'
            return make_response(jsonify(response)), response_code
        if not data:
            response['data'] = "Please send the json data"
            return make_response(jsonify(response)), response_code
        try:
            product_id = int(product_id)
            register_utility = DBUtility(session)
            if register_utility.update_product(product_id, data):
                products = register_utility.get_products(product_id)
                response['status'] = 'success'
                response_code = 200
                response['data'] = [product.serialize for product in products]
            session.commit()
        except ValueError:
            response['data'] = 'Invalid Product Id'
        except Exception as ex:
            response['data'] = 'Unable to update'
            response_code = 500
            response['status'] = 'failure'
        session.close()
        return make_response(jsonify(response)), response_code


class RegisterUserAPIView(MethodView):

    def post(self):
        data = request.get_json()
        session = DBBackend().get_session()
        response = dict()
        response['status'] = 'failure'
        response['data'] = 'Some error occurred. Please try again.'
        response_code = 500
        try:
            register_utility = DBUtility(session)
            user = register_utility.register_user(data)
            response['status'] = 'success'
            response['data'] = 'Successfully registered.'
            response_code = 201
            session.commit()
        except KeyError:
            response['data'] = "email or password is missing"
            response_code = 422
        except AssertionError as ae:
            response['data'] = str(ae)
            response_code = 422
        except IntegrityError, ie:
            response['data'] = "User is already registered."
            session.rollback()
        except Exception as ex:
            response['data'] = "Something went wrong"
            response_code = 500
            response['status'] = 'failure'
        session.close()
        return make_response(jsonify(response)), response_code


class LoginAPIView(MethodView):

    def post(self):
        data = request.get_json()
        response = dict()
        response['status'] = 'failure'
        response['data'] = 'Some error occurred. Please try again.'
        session = DBBackend().get_session()
        try:
            user = session.query(User).filter_by(email=func.binary(data['email'])).one()
            response['status'] = 'success'
            response['data'] = dict()
            response['data']['user_id'] = user.id
            response['data']['email'] = user.email
            response['data']['auth_token'] = user.encode_token()
            session.add(user)
            session.commit()
            response_code = 200
        except NoResultFound:
            response['data'] = 'User not found.'
            response_code = 401
        except Exception as ex:
            response['data'] = "Error occured : " + str(ex.message)
            response_code = 500
            response['status'] = 'failure'
        session.close()
        return make_response(jsonify(response)), response_code


class UserAPIView(MethodView):

    @verify_token
    def get(self):
        response = dict()
        response_code = 422
        response['status'] = 'failure'
        response['data'] = 'Error occurred. Try again.'
        session = DBBackend().get_session()
        user_id = request.args.get('user_id', None)
        try:
            message = 'Invalid User Id'
            if user_id:
                user_id = int(user_id)
            db_utility = DBUtility(session)
            response['data'] = [user.serialize for user in db_utility.get_users(user_id)]
            response['status'] = 'success'
            response_code = 200
        except ValueError:
            response['data'] = message
        except Exception as ex:
            response['data'] = "Error occured : "+ str(ex.message)
            response_code = 500
            response['status'] = 'failure'
        session.close()
        return make_response(jsonify(response)), response_code

    @verify_token
    def put(self):
        response = dict()
        data = request.get_json()
        user_id = request.args.get('user_id')
        session = DBBackend().get_session()
        response_code = 422
        response['status'] = 'failure'
        if not user_id:
            response['data'] = 'User Id missing'
            return make_response(jsonify(response)), response_code
        if not data:
            response['data'] = "Please send the json data"
            return make_response(jsonify(response)), response_code

        try:
            if user_id:
                message = 'Invalid User Id'
                user_id = int(user_id)
            db_utility = DBUtility(session)
            if db_utility.update_user(user_id, data):
                users = db_utility.get_users(user_id)
                response['status'] = 'success'
                response_code = 200
                response['data'] = [user.serialize for user in users]
            session.commit()
        except ValueError:
            response['data'] = message
        except Exception as ex:
            response['data'] = "Error occured : " + str(ex.message)
            response_code = 500
            response['status'] = 'failure'
        session.close()
        return make_response(jsonify(response)), response_code


class CommentAPIView(MethodView):

    @verify_token
    def post(self):
        response = dict()
        data = request.get_json()
        session = DBBackend().get_session()
        response['data'] = dict()
        response['status'] = 'failure'

        try:
            if not data and not data.get('comment', None):
                response['data'] = {"error": "Comment Data missing"}
                return make_response(jsonify(response)), 422
            comment = data.get('comment')
            db_utility = DBUtility(session)
            product_id = comment.get('product_id', None)
            user_id = comment.get('created_by', None)
            if not product_id:
                response['data']= {'error': 'Product Id needed'}
            try:
                product_id = int(product_id)
                if user_id:
                    user_id = int(user_id)
                comment = db_utility.add_comment(comment, product_id)
                response['data'] = {'comment': comment.serialize}
            except Exception as e:
                response['data'] = {'error': e.message}
            response['status'] = 'success'
            response_code = 201
            session.commit()
        except KeyError:
            response['data'] = {"error": "Key data is missing"}
            response_code = 422
        except AssertionError as ae:
            response['data'] = str(ae)
            response_code = 422
        except Exception as ex:
            response['data'] = {"error": "Error occured" + str(ex.message)}
            response_code = 500
            response['status'] = 'failure'
            session.rollback()
        session.close()
        return make_response(jsonify(response)), response_code

    @verify_token
    def get(self):
        response = dict()
        response_code = 422
        response['status'] = 'failure'
        response['data'] = 'Error occurred. Try again.'
        session = DBBackend().get_session()
        product_id = request.args.get('product_id', None)
        comment_id = request.args.get('comment_id', None)
        user_id = request.args.get('user_id', None)
        if not product_id:
            response['data'] = 'Product Id is missing'
            return make_response(jsonify(response)), response_code
        message = 'Invalid Product Id'
        try:
            if product_id:
                product_id = int(product_id)
            if comment_id:
                message = 'Invalid Comment Id'
                comment_id = int(comment_id)
            if user_id:
                message = 'Invalid User Id'
                user_id = int(user_id)
            db_utility = DBUtility(session)
            comments = [comment.serialize for comment in db_utility.get_comments(product_id, comment_id, user_id)]
            if not comments:
                response['data'] = 'No comments found'
            response['data'] = sorted(comments, key=lambda comment: comment.get('id'))
            response_code = 200
            response['status'] = 'success'
        except ValueError:
            response['data'] = message
        except Exception as ex:
            response['data'] = "Error occured : " + str(ex.message)
            response_code = 500
            response['status'] = 'failure'
        session.close()
        return make_response(jsonify(response)), response_code

    @verify_token
    def put(self):
        response = dict()
        data = request.get_json()
        comment_id = request.args.get('comment_id')
        session = DBBackend().get_session()
        response_code = 422
        response['status'] = 'failure'
        product_id = data.get('product_id', None)
        message = "Unable to update."
        if not comment_id:
            response['data'] = 'Comment Id is missinng'
            return make_response(jsonify(response)), response_code
        if not data:
            response['data'] = "Missing data"
            return make_response(jsonify(response)), response_code
        if not product_id:
            response['data'] = 'Product Id is missing'
            return make_response(jsonify(response)), response_code
        try:
            message = 'Invalid Product Id'
            product_id = int(product_id)
            message = 'Invalid Comment Id'
            comment_id = int(comment_id)
            db_utility = DBUtility(session)
            if db_utility.update_comment(product_id, comment_id, data):
                comments = db_utility.get_comments(product_id, comment_id)
                response['status'] = 'success'
                response_code = 200
                response['data'] = [comment.serialize for comment in comments]
            session.commit()
        except ValueError:
            response['data'] = message
        except Exception as ex:
            response['data'] = 'Error occured : ' + str(ex.message)
            response_code = 500
            response['status'] = 'failure'

        session.close()
        return make_response(jsonify(response)), response_code


urls.add_url_rule('/api/v1/register/', view_func=RegisterUserAPIView.as_view('register-user'))
urls.add_url_rule('/api/v1/login/', view_func=LoginAPIView.as_view('login'))
urls.add_url_rule('/api/v1/user/', view_func=UserAPIView.as_view('user'), methods=['GET', 'POST', 'PUT'])
urls.add_url_rule('/api/v1/product/', view_func=ProductAPIView.as_view('product'), methods=['GET', 'POST', 'PUT'])
urls.add_url_rule('/api/v1/comment/', view_func=CommentAPIView.as_view('comment'), methods=['GET', 'POST', 'PUT'])