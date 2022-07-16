import socket
import re
from player import Player
import threading
from game import Game

PORT = 8091
player_socket_map = {}
current_game = None


def create_socket():
    client_socket, address = s.accept()
    send_message_to_client(client_socket, 'Welcome to this game!')
    create_new_thread_for_user(client_socket)


def listen_for_changes(client_socket):
    while True:
        msg = client_socket.recv(1024).decode('utf-8')
        print(f"message received from client: {msg}")
        message_parser(client_socket, msg)


def create_new_thread_for_user(client_socket):
    thread = threading.Thread(target=lambda: listen_for_changes(client_socket), name=str(client_socket))
    thread.start()


def send_message_to_client(client_socket, msg):
    print(f'sending message to client: {msg}')
    client_socket.send(bytes(msg, 'utf-8'))


def add_user_with_name(client_socket, player_name):
    global users_to_play
    if player_name in users_to_play.keys():
        send_message_to_client(client_socket, 'This name is already taken. please pick another name!')
        return
    new_player = Player(player_name)
    new_player.socket = client_socket
    users_to_play[player_name] = new_player
    send_message_to_client(client_socket, 'Registered successfully!')
    print(f'new user registered with name: {new_player.name}')


def invite_players_to_game(client_socket, player_names):
    global users_to_play
    global current_game
    list_of_players = []
    for player_name in player_names:
        if player_name not in users_to_play.keys():
            send_message_to_client(client_socket, f'user <{player_name}> does not exist')
            return
        list_of_players.append(users_to_play[player_name])
    new_game = Game(list_of_players)
    current_game = new_game
    for player in list_of_players:
        send_message_to_client(player.socket, 'Game successfully created! Press Enter to continue ...')
    chosen_letter = new_game.choose_random_letter()
    for player in list_of_players:
        send_message_to_client(player.socket, f'chosen letter is: {chosen_letter}')


def handle_setting(client_socket, name, attribute):
    sending_user = None
    for user in users_to_play.keys():
        if users_to_play[user].socket == client_socket:
            sending_user = users_to_play[user]
            break
    if str(attribute).startswith(current_game.letter):
        sending_user.game_info[name] = attribute
        send_message_to_client(client_socket, f'Got it! game info: {sending_user.game_info}')
    else:
        send_message_to_client(client_socket, f'Not starting with {current_game.letter}')


def increase_scores(duplicate_guys, all_guys):
    for guy in all_guys:
        if len(duplicate_guys) != 0 and guy not in duplicate_guys[0]:
            users_to_play[guy].score += 10
        else:
            users_to_play[guy].score += 5


def finish_game():
    # check items
    duplicate_guys, all_guys = check_duplicate('name')
    increase_scores(duplicate_guys, all_guys)
    duplicate_guys, all_guys = check_duplicate('city')
    increase_scores(duplicate_guys, all_guys)
    duplicate_guys, all_guys = check_duplicate('food')
    increase_scores(duplicate_guys, all_guys)
    duplicate_guys, all_guys = check_duplicate('city')
    increase_scores(duplicate_guys, all_guys)
    result = ''
    for player in current_game.players:
        result += f"{player.name}: {player.score} \n"
    for player in current_game.players:
        send_message_to_client(player.socket, f'Game finished! results are: {result}')


def check_duplicate(item):
    dictionary = {}
    for player in current_game.players:
        dictionary[player.name] = player.game_info[item]
        rev_multidict = {}
    for key, value in dictionary.items():
        rev_multidict.setdefault(value, set()).add(key)
    duplicate_guys = [values for key, values in rev_multidict.items() if len(values) > 1]
    return duplicate_guys, dictionary


def message_parser(client_socket, message):
    if re.match('register user .+', message):
        player_name = re.findall('register user (.+)', message)[0]
        add_user_with_name(client_socket, player_name)
    elif re.match('start game with .+', message):
        player_names = re.findall('start game with (.+)', message)[0].split(',')
        invite_players_to_game(client_socket, player_names)
    elif re.match('name|city|food|color: .+', message):
        item_name = re.findall('(name|city|food|color): (.+)', message)[0][0]
        item_attribute = re.findall('(name|city|food|color): (.+)', message)[0][1]
        handle_setting(client_socket, item_name, item_attribute)
    elif message == 'done':
        finish_game()
    else:
        send_message_to_client(client_socket, 'malformed message')


if __name__ == '__main__':
    s = socket.socket()

    s.bind((socket.gethostname(), PORT))
    s.listen(5)
    print("socket is listening")

    users_to_play = {}
    while True:
        create_socket()
