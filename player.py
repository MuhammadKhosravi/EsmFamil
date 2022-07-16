class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.socket = None
        self.game_info = {'name': '', 'color': '', 'city': '', 'food': ''}

    def __repr__(self):
        return f'"Player <{self.name}>"'
