from flask_restful import Resource,reqparse
class TestAPI(Resource):
    def get(self):
        ## Use this to get req.query
        parser = reqparse.RequestParser()
        parser.add_argument('q', type=str)
        q=parser.parse_args()
        return {"status":"get success", "query":q}
    def post(self):
        ## Use this to get req.body
        parser = reqparse.RequestParser()
        parser.add_argument('data', location="json")
        data=parser.parse_args()
        return {"status":"get success", "data":data}