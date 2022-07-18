from flask import Blueprint

from services import get_cluster
from services.recommendation import get_recommended_cars


car_blueprint = Blueprint('car', __name__)


@car_blueprint.route('/<car_id>', methods=['GET'])
def index(car_id):
    return get_recommended_cars(car_id)
