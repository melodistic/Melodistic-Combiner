from flask import Response, request
from flask_restful import Resource,reqparse
from controllers.generator import generate
class Generator(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name',type=str)
        parser.add_argument('sections',type=list,location="json")
        program=parser.parse_args()
        return generate(program)