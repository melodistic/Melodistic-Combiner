import json
import os

class Database:
    def __init__(self):
        self.data = []
        for i in os.listdir("data/"):
            self.data += json.load(open("data/"+i))
    def get_data(self):
        return self.data
    def save_data(self, data):
        all_data = []
        with open("combine-result/data.json", "r") as f:
            all_data = json.load(f)
        all_data.append(data)
        with open("combine-result/data.json", "w") as f:
            json.dump(all_data, f)
        