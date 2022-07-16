import random


class Game:
    def __init__(self, players):
        self.letter = ''
        self.players = players

    def choose_random_letter(self):
        all_letters ='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.letter = random.choice(all_letters)
        return self.letter

