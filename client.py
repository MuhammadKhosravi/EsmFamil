import socket

PORT = 8091


def send_message_to_server(message):
    global s
    s.send(bytes(message, 'utf-8'))


def receive_message_from_server():
    message = s.recv(1024).decode('utf-8')
    print(message)


if __name__ == '__main__':
    player_name = ''
    s = socket.socket()

    s.connect((socket.gethostname(), PORT))

    message = s.recv(1024).decode('utf-8')
    print(message)

    while True:
        msg = input()
        send_message_to_server(msg)
        receive_message_from_server()
