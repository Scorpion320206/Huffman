class Node:
    def __init__(self, name, freq, code, loc, used, parent):
        self.name = name
        self.freq = freq
        self.code = code
        self.used = used
        self.parent = parent
        self.loc = loc