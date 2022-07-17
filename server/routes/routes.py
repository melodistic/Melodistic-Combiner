from .generator import Generator
def initialize_routes(api):
    api.add_resource(Generator, '/api/generate')