from .generator import Generator
from .test import TestAPI
def initialize_routes(api):
    api.add_resource(Generator, '/api/generate')