# server.py
import socket
import sys
import random
import threading
import time
import signal

numConn = 0
numMult = 0
allCS = []
ip_addr = "127.0.0.1"
port = 9012

if (len(sys.argv) == 3):
    ip_addr = sys.argv[1]
    port = int(sys.argv[2])
elif (len(sys.argv) > 1):
    print("Too many input args to program.")
    sys.exit()

path = '../words.txt'
wordFile = open(path, 'r')
wordArray = wordFile.readlines()
wordArray = [word.rstrip('\n') for word in wordArray]
wordFile.close()

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind((ip_addr, port))
serverSocket.listen(6)

# Function definitions

# Signal handler
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

# Choosing random word
def chooseWord():
    wordNum = random.randint(0, len(wordArray) - 1)
    word = wordArray[wordNum]
    return word

# Decline/shut down client because max is reached
def graceful_end(clientsocket, addr):
    msg = "server-overloaded"
    byteArr = bytes([len(msg)]) + msg.encode('ascii')
    clientsocket.sendall(byteArr)
    clientsocket.close()

# Handle singleplayer game
def start_single(clientsocket, addr):
    global numConn
    currWord = chooseWord()
    print(currWord)                         # Keep this in here. It's actually required.
    guessedCorrectLetters = []
    guessedIncorrectLetters = []
    finishGame = False
    # Sending underlines for empty letters
    byteArr = bytes([0, len(currWord), 0])
    for letter in currWord:
        byteArr = byteArr + "_".encode('ascii')
    clientsocket.send(byteArr)
    while not (finishGame):
        currMsg = clientsocket.recv(1024)
        if (currMsg != b''):
            # Accepting one-length message and checking for correctness
            if currMsg[0] == 1:
                asciiRet = currMsg[1:len(currMsg)].decode('ascii')
                # Letter is correct
                if asciiRet in currWord:
                    for letter in currWord:
                        if asciiRet == letter:
                            guessedCorrectLetters.append(asciiRet)
                # Letter is incorrect
                else:
                    guessedIncorrectLetters.append(asciiRet)
                byteArr = bytes(
                    [0, len(currWord),
                     len(guessedIncorrectLetters)])
                for letter in currWord:
                    if letter in guessedCorrectLetters:
                        byteArr = byteArr + letter.encode('ascii')
                    else:
                        byteArr = byteArr + "_".encode('ascii')
                for elem in guessedIncorrectLetters:
                    byteArr = byteArr + elem.encode('ascii')
                clientsocket.sendall(byteArr)
            # Send win or lose message
            elif currMsg[0] == 2:
                if (len(guessedCorrectLetters) == len(currWord)):
                    byteArr = bytes([8]) + "You Win!".encode('ascii')
                    clientsocket.sendall(byteArr)
                if (len(guessedIncorrectLetters) == 6):
                    byteArr = bytes([9]) + "You Lose!".encode('ascii')
                    clientsocket.sendall(byteArr)
                finishGame = True
            # Invalid message        
            else:
                print("Invalid client message received")
                finishGame = True

    allCS.remove(clientsocket)
    clientsocket.close()
    numConn -= 1

# Handle multiplayer game
def start_multiplayer(P1, P2):
    global numConn
    global numMult
    currWord = chooseWord()
    print(currWord)                     # Keep this in here. It's actually required.
    guessedCorrectLetters = []
    guessedIncorrectLetters = []
    finishGame = False
    # Sending underlines for empty letters
    byteArr = bytes([0, len(currWord), 0])
    for each in currWord:
        byteArr = byteArr + "_".encode('ascii')
    time.sleep(1)
    P1.sendall(byteArr)
    P2.sendall(byteArr)
    while not (finishGame):
        # Send message so the clients know when their turn is
        if not finishGame:
            time.sleep(1)
            P1.sendall(bytes([5]))
            P2.sendall(bytes([4]))          # Just not 5, 5 means it's this player's turn
            finishGame = doTurn(P1, P2, guessedCorrectLetters, guessedIncorrectLetters, currWord)
        if not finishGame:
            # Send message so the clients know when their turn is
            time.sleep(1)
            P2.sendall(bytes([5]))
            P1.sendall(bytes([4]))      # Just not 5, 5 means it's this player's turn
            finishGame = doTurn(P2, P1, guessedCorrectLetters, guessedIncorrectLetters, currWord)

    allCS.remove(P1)
    allCS.remove(P2)
    P1.close()
    P2.close()
    numConn -= 2
    numMult -= 2

# Handles a turn for both players
# Active player is the one sending a guess
# Passive player is the one waiting
def doTurn(active, passive, correctArr, incorrectArr, currWord):
    currMsg = active.recv(1024)
    if (currMsg != b''):
        # Accepting one-length message and checking for correctness
        if currMsg[0] == 1:
            asciiRet = currMsg[1:len(currMsg)].decode('ascii')
            if asciiRet in currWord:
                for letter in currWord:
                    if asciiRet == letter:
                        correctArr.append(asciiRet)
            else:
                incorrectArr.append(asciiRet)
            byteArr = bytes(
                [0, len(currWord),
                len(incorrectArr)])
            for letter in currWord:
                if letter in correctArr:
                    byteArr = byteArr + letter.encode('ascii')
                else:
                    byteArr = byteArr + "_".encode('ascii')
            for elem in incorrectArr:
                byteArr = byteArr + elem.encode('ascii')
            time.sleep(1)
            active.sendall(byteArr)
            passive.sendall(byteArr)
        # Send win or lose message
        elif currMsg[0] == 2:
            print("2")
            if (len(correctArr) == len(currWord)):
                byteArr = bytes([8]) + "You Win!".encode('ascii')
                time.sleep(1)
                active.sendall(byteArr)
                passive.sendall(byteArr)
                print("You win")
            if (len(incorrectArr) == 6):
                byteArr = bytes([9]) + "You Lose!".encode('ascii')
                time.sleep(1)
                active.sendall(byteArr)
                passive.sendall(byteArr)
                print("You lose")
            finishGame = True
            return finishGame
        # Invalid message        
        else:
            print("Invalid client message received")
            finishGame = True
            return finishGame

# Main loop
while True:
    try:
        clientsocket, clientaddr = serverSocket.accept()
        if (numConn < 3):
            allCS.append(clientsocket)
            numConn = numConn + 1
            currMsg = clientsocket.recv(1024)
            if (currMsg != b''):
                if currMsg[0] == 0:             # Singleplayer game
                    t = threading.Thread(target=start_single,
                                        args=(clientsocket, clientaddr))
                    t.start()
                elif currMsg[0] == 3:           # Multiplayer game
                    numMult += 1
                    if numMult == 1:            # Wait for second player
                        P1 = clientsocket
                    elif numMult == 2:          # Start game
                        P2 = clientsocket
                        t = threading.Thread(target=start_multiplayer,
                                            args=(P1, P2))
                        t.start()
                    if numMult == 3:            # Better way to handle this than exit?
                        msg = "No multiplayer instance available."
                        print(msg)
                        byteArr = bytes([len(msg)]) + msg.encode('ascii')
                        clientsocket.sendall(byteArr)
                        allCS.remove(clientsocket)
                        clientsocket.close()
                        numConn -= 1
                else:                           # Invalid message     
                    print("Invalid client message received")
                    allCS.remove(clientsocket)
                    clientsocket.close()
                    numConn -= 1
        else:
            t = threading.Thread(target=graceful_end,
                                 args=(clientsocket, clientaddr))
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