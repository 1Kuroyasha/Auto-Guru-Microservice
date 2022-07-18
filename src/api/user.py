from flask import Blueprint

from services import recommend

user_blueprint = Blueprint('user', __name__)


@user_blueprint.route('/<user_id>', methods=['GET'])
def index(user_id):
    return recommend(user_id)
