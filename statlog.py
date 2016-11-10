

class statLog():
    def __init__(self):
        self.changedCount = 0
        self.touchedCount = 0
        self.errors = []
        
    def touched(self):
        self.touchedCount += 1
        
    def changed(self):
        self.changedCount += 1
        
    def error(self, msg):
        errors.append(msg)
    
