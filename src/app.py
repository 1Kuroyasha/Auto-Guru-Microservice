from dotenv import load_dotenv

from flask import Flask
from api import car_blueprint, user_blueprint

from flask_cors import CORS

app = Flask(__name__)

CORS(app)

app.register_blueprint(car_blueprint, url_prefix='/api/car')
app.register_blueprint(user_blueprint, url_prefix='/api/user')

if __name__ == "__main__":
    load_dotenv()
    app.run()
