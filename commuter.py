class Commuter5:
    def __init__(self,val):
        self.val=val
    def __add__(self,other):
        if isinstance(other, Commuter5):
            other = other.val
        return Commuter5(self.val + other)
    def __radd__(self, other):
        return Commuter5(other + self.val)
    def __str__(self):
        return '<Commuter5: %s>' % self.val
