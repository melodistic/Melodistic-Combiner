from flask_restful import Resource,reqparse
from controllers.generator import generate
import datetime

class Generator(Resource):
    def get(self):
        return {
            'message': 'pong',
            'timestamp': '{}'.format(datetime.datetime.now())
        }
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('program_name',type=str)
        parser.add_argument('muscle_group',type=str)
        parser.add_argument('sections',type=list,location="json")
        program=parser.parse_args()
        return generate(program)