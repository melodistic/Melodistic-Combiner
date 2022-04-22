import json
import os

class Database:
    def __init__(self):
        self.data = []
        for i in os.listdir("data/"):
            self.data += json.load(open("data/"+i))
    def get_data(self):
        return self.data
