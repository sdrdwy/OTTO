import json

class WorldSimulator:
    def __init__(self):
        with open("./config/system.json",'r') as f:
            self.config = json.load(f)
        self.current_day = 0 #current day
        self.current_period = 0 #current event

        with open("./config/map.json",'r') as f:
            self.map = json.load(f)


    def next(self,):
        pass

    def cur(self,):
        pass
