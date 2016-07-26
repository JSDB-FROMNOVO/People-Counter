from __future__ import absolute_import
from flask import Blueprint
from flask_restful import Api

api = Blueprint('api', __name__, url_prefix='/api')

rest_api = Api(api)

from . import vnc
