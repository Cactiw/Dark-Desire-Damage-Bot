

class Castle_report:

    def __init__(self, castle, status, damage, warning = ""):
        self.castle = castle
        self.status = status
        self.damage = damage
        self.warning = warning

    def __eq__(self, other):
        return self.castle == other.castle