#!/usr/bin/env python

import select
import socket
import sys
import pickle
from player import Player
from monster import Monster
from party import Party


DATA_SIZE = 1024 * 10 #10 kilobytes max per message

def create_server_sock(port=50000, host='', backlog=5):
  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  server.bind((host, port))
  server.listen(backlog)
  return server

def start_game(sockets):
  for sock in sockets:
    sock.sendall(pickle.dumps('start'))

def main():
  inputs = []
  player_sockets = []
  player_data = {}

  server = create_server_sock()

  inputs.append(server)
  inputs.append(sys.stdin)
  running = True
  game_started = False

  while running:
    input_ready, output_ready, except_ready = select.select(inputs + player_sockets, [], [])
    
    for s in input_ready:
      if s == server:
        client, address = server.accept()
        if len(player_sockets) < 2:
          print('Received connection from {}.'.format(address))
          player_sockets.append(client)
          player_data[client] = Player(client)
          if len(player_sockets) == 2:
            start_game(player_sockets)
        else:
          print('Rejecting connection from {}.'.format(address))
          client.sendall(b'too many players\n')
          client.close()

      elif s == sys.stdin:
        #handle standard input
        junk = sys.stdin.readline().strip()
        if junk == 'quit':
          print('Closing server.')
          running = False

      else:
        #handle other sockets
        try:
          data = s.recv(DATA_SIZE)
        except (ConnectionResetError, TimeoutError) as e:
          #count as closed if other connection terminated early
          data = None
        print(data)
        if not data:
          #this socket closed or handle_message returned False
          print("Connection {} closed remotely.".format(player_data[s].name))
          player_sockets.remove(s)
          del player_data[s]
          s.close()
        else:
          data = pickle.loads(data)
          if type(data) is Party:
            print('Received party info: {}.'.format(data.party))
            player_data[s].party = data

            for sock in player_sockets:
              print(s, sock)
              if sock != s:
                print('did it')
                active = player_data[s].party.active
                sock.sendall(pickle.dumps(active))

  server.close()


if __name__ == '__main__':
  main()
