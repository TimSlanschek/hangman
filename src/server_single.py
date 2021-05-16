# server.py
import socket
import sys
import random
import threading
import time 
import signal

global numConn
ip_addr = "127.0.0.1"
port = 9012
if (len(sys.argv) == 3):
        ip_addr = sys.argv[1]
        port = int(sys.argv[2])
elif (len(sys.argv) > 1):
        print("Too many input args to program.")
        sys.exit()



def signal_handler(sig, frame):
        print("\nSigint received")
        try:
                for cs in allCS:
                        cs.shutdown(socket.SHUT_RDWR)
                        cs.close()
                serverSocket.close()
        except:
                sys.exit()
        sys.exit()

path = '../words.txt'

wordFile = open(path, 'r')
wordArray = wordFile.readlines()
wordArray = [word.rstrip('\n') for word in wordArray]
wordFile.close()

def chooseWord():
        wordNum = random.randint(0, len(wordArray) - 1)
        word = wordArray[wordNum]
        return word

def graceful_end(clientsocket, addr):
        msg = "server-overloaded"
        byteArr = bytes([len(msg)]) +  msg.encode('ascii')
        clientsocket.sendall(byteArr)
        clientsocket.close()

def new_connection(clientsocket, addr):
        global numConn
        global allCS
        currWord = chooseWord()
        print(currWord) # keep this in here. It's actually required
        guessedCorrectLetters = []
        guessedIncorrectLetters = []
        finishGame = False
        while not(finishGame):
                currMsg = clientsocket.recv(1024)
                if (currMsg != b''):
                        if currMsg[0] == 0:
                                byteArr = bytes([0, len(currWord), 0])
                                for letter in currWord:
                                        byteArr = byteArr + "_".encode('ascii')
                                clientsocket.send(byteArr)
                        elif currMsg[0] == 1:
                                asciiRet = currMsg[1:len(currMsg)].decode('ascii')
                                if asciiRet in currWord:
                                        for letter in currWord:
                                                if asciiRet == letter:
                                                        guessedCorrectLetters.append(asciiRet)
                                else:
                                        guessedIncorrectLetters.append(asciiRet)
                                byteArr = bytes([0, len(currWord), len(guessedIncorrectLetters)])
                                for letter in currWord:
                                        if letter in guessedCorrectLetters:
                                                byteArr = byteArr + letter.encode('ascii')
                                        else:
                                                byteArr = byteArr + "_".encode('ascii')
                                for elem in guessedIncorrectLetters:
                                        byteArr = byteArr + elem.encode('ascii')
                                clientsocket.sendall(byteArr)
                        elif currMsg[0] == 2:
                                if (len(guessedCorrectLetters) == len(currWord)):
                                        byteArr = bytes([8]) + "You Win!".encode('ascii')  
                                        clientsocket.sendall(byteArr)
                                if (len(guessedIncorrectLetters) == 6):
                                        byteArr = bytes([9]) + "You Lose!".encode('ascii') 
                                        clientsocket.sendall(byteArr)
                                finishGame = True                  
                        else:
                                print("Invalid client message received")
                                finishGame = True
        
        allCS.remove(clientsocket)
        clientsocket.close()
        numConn = numConn - 1


serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

serverSocket.bind((ip_addr, port))  

serverSocket.listen(6)

signal.signal(signal.SIGINT, signal_handler)

numConn = 0

allCS = []

while True:
        try:
                clientsocket, clientaddr = serverSocket.accept()
                if (numConn < 3):
                        allCS.append(clientsocket)
                        t = threading.Thread(target=new_connection, args=(clientsocket, clientaddr))
                        t.start()
                        numConn = numConn + 1
                else:
                        t = threading.Thread(target=graceful_end, args=(clientsocket, clientaddr))
                        t.start()
        except:
                try:
                        for cs in allCS:   
                                cs.shutdown(socket.SHUT_RDWR)
                                cs.close()
                        serverSocket.close()
                except:
                        sys.exit()
                sys.exit()

