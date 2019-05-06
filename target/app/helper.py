
from validate_email import validate_email

from models import User, Product, Comment
from target.settings.comment_filter import check_bad_comment
from flask import g


class DBUtility(object):
    def __init__(self, session):
        self.session = session

    def register_user(self, data):
        if UserValidator(data).check_user_data():
            user = User(data['email'], data['first_name'], data['last_name'], data['password'])
            self.session.add(user)
            self.session.flush()
            return user

    def get_users(self, user_id=None):
        filter_params = {}
        if user_id:
            filter_params['id'] = user_id
        return self.session.query(User).filter_by(**filter_params).all()

    def delete_user(self, user_id):
        user = self.session.query(User).filter(User.id==user_id).one()
        self.session.delete(user)

    def update_user(self, user_id, data):
        if not g.user_id == user_id:
            raise Exception('Only logged In user can update user related info')
        db_query = self.session.query(User).filter(User.id == user_id)
        return db_query.update(data)

    def register_product(self, data):
        product = Product(**data)
        self.session.add(product)
        self.session.flush()
        return product

    def get_products(self, product_id=None):
        filter_params = {}
        if product_id:
            filter_params['id'] = product_id
        return self.session.query(Product).filter_by(**filter_params).all()

    def update_product(self, product_id, data):
        return self.session.query(Product).filter(Product.id == product_id).update(data)

    def add_comment(self, comment, product_id):
        if not product_id:
            raise AssertionError('Missing product_id')
        comment['product_id'] = product_id
        if comment.get('description', None):
            if check_bad_comment(comment.get('description')):
                raise Exception('Commment contains the bad words')
        com = Comment(**comment)
        self.session.add(com)
        self.session.flush()
        return com

    def get_comments(self, product_id, comment_id=None, user_id=None):
        filter_params = {}
        if product_id:
            filter_params['product_id'] = product_id
        if comment_id:
            filter_params['id'] = comment_id
        if user_id:
            filter_params['created_by'] = user_id
        return self.session.query(Comment).filter_by(**filter_params).all()

    def update_comment(self, product_id, comment_id, data):
        if data.get('description', None):
            if check_bad_comment(data.get('description')):
                raise Exception('Commment contains the bad words')
        return self.session.query(Comment).filter_by(product_id=product_id, id=comment_id).update(data)


class UserValidator(object):
    def __init__(self, data):
        self.data = data

    def check_required_data(self, required_keys):
        return list(set(required_keys) - set(self.data.keys()))

    def check_email(self, email):
        return validate_email(email)

    def check_user_data(self):
        required_fields = ['email','first_name', 'last_name', 'password']
        missing_fields = self.check_required_data(required_fields)
        if missing_fields:
            raise AssertionError('Missing fields: {}'.format(" and ".join(missing_fields)))

        if not self.check_email(self.data['email']):
            raise AssertionError("Incorrect Email Address")
        return True