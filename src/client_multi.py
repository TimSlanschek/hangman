# client.py
import socket
import sys

ip_addr = sys.argv[1]
port = int(sys.argv[2])
multiplayer = False
cont = True

def singleplayer_client():
    guessedLetters = []
    cont = True
    while True:
        recvBuf = clientSocket.recv(1024)
        if (recvBuf != b''):
            # Display output
            decodedBuf = recvBuf.decode('ascii')
            # Cases: Error, Win, Loss
            if (recvBuf[0] == 17) or (recvBuf[0] == 8) or (recvBuf[0] == 9): # Does this prevent words with length 8,9,17 of being used???
                print(decodedBuf[1:])
                clientSocket.close()
                sys.exit()
            else:
                for index in range(0, recvBuf[1]):
                    print(decodedBuf[index + 3], end=" ")
                print()
                print("Incorrect Guesses:", end=" ")
                for index2 in range(0, recvBuf[2]):
                    print(decodedBuf[index2 + 3 + recvBuf[1]], end=" ")
                print(" ")
                print()
            # Send Win or Lost signal
            if (("_" not in decodedBuf[3: 3 + recvBuf[1]]) or (recvBuf[2] >= 6)):
                clientSocket.sendall(bytes([2]))
                cont = False
            # Continue with the game
            if cont:
                correctInput = False
                userLetter = ""
                while not(correctInput):
                    userLetter = input("Make your guess: ")
                    if ((len(userLetter) > 1) or not(userLetter.isalpha())):
                        print("Error! Please guess one letter.\n")
                    elif (userLetter.lower() in guessedLetters):
                        s = "Error! Letter " + userLetter.lower() + " has been guessed before, please guess another letter."
                        print(s)
                    else:
                        correctInput = True
                clientSocket.sendall(bytes([1]) + userLetter.lower().encode('ascii'))
                guessedLetters.append(userLetter.lower())


def multiplayer_client():
    global cont
    guessedLetters = []
    # Receive initial blank lines
    recvBuf = clientSocket.recv(1024)
    decodedBuf = recvBuf.decode('ascii')
    cont = True
    if (recvBuf != b''):
        for index in range(0, recvBuf[1]):
            print(decodedBuf[index + 3], end=" ")
        print()
        print("Incorrect Guesses:", end=" ")
        for index2 in range(0, recvBuf[2]):
            print(decodedBuf[index2 + 3 + recvBuf[1]], end=" ")
        print()
    while True:
        recvBuf = clientSocket.recv(1024)
        # If recv is not empty
        if (recvBuf != b''):
            # Game over check
            if (recvBuf[0] == 17) or (recvBuf[0] == 8) or (recvBuf[0] == 9):
                decodedBuf = recvBuf.decode('ascii')
                print(decodedBuf[1:])
                clientSocket.close()
                sys.exit()
            # Which turn
            if recvBuf[0] == 5:
                activeTurn(guessedLetters, cont)
            elif recvBuf[0] == 4:
                passiveTurn()
            else:
                print("No active/passive assignment")

# This player's turn
def activeTurn(guessedLetters, cont):
    if cont:
        correctInput = False
        userLetter = ""
        while not(correctInput):
            userLetter = input("Make your guess: ")
            if ((len(userLetter) > 1) or not(userLetter.isalpha())):
                print("Error! Please guess one letter.\n")
            elif (userLetter.lower() in guessedLetters):
                s = "Error! Letter " + userLetter.lower() + " has been guessed before, please guess another letter."
                print(s)
            else:
                correctInput = True
        # Send guess
        clientSocket.sendall(bytes([1]) + userLetter.lower().encode('ascii'))
        guessedLetters.append(userLetter.lower())
    recvBuf = clientSocket.recv(1024)
    # Display output
    decodedBuf = recvBuf.decode('ascii')
    if (recvBuf != b''):
        # Cases: Error, Win, Loss
        if (recvBuf[0] == 17) or (recvBuf[0] == 8) or (recvBuf[0] == 9):
            print(decodedBuf[1:])
            clientSocket.close()
            sys.exit()
        else:
            for index in range(0, recvBuf[1]):
                print(decodedBuf[index + 3], end=" ")
            print()
            print("Incorrect Guesses:", end=" ")
            for index2 in range(0, recvBuf[2]):
                print(decodedBuf[index2 + 3 + recvBuf[1]], end=" ")
            print(" ")
            print()
        # Send Win or Lost signal
        if (("_" not in decodedBuf[3: 3 + recvBuf[1]]) or (recvBuf[2] >= 6)):
            clientSocket.sendall(bytes([2]))
            print("2")
            cont = False
    return cont

# Only displays the output of the game without sending input, as it is not this player's turn
def passiveTurn():
    print("Teammate's turn. Wait.")
    recvBuf = clientSocket.recv(1024)
    # Display output
    decodedBuf = recvBuf.decode('ascii')
    # Cases: Error, Win, Loss
    if (recvBuf[0] == 17) or (recvBuf[0] == 8) or (recvBuf[0] == 9):
        print(decodedBuf[1:])
        clientSocket.close()
        sys.exit()
    else:
        for index in range(0, recvBuf[1]):
            print(decodedBuf[index + 3], end=" ")
        print()
        print("Incorrect Guesses:", end=" ")
        for index2 in range(0, recvBuf[2]):
            print(decodedBuf[index2 + 3 + recvBuf[1]], end=" ")
        print(" ")
        print("Your turn.")
        print()

# Main loop
while True:
    userInput = input("Ready to start game? (y/n): ")
    if userInput == "y":
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        clientSocket.connect((ip_addr, port))
        userInput = input("Do you want to play twoplayer (y/n): ")
        if userInput == "y" or userInput == "n":
            if userInput == "y":
                multiplayer = True
                # Send "multiplayer" signal
                msg = bytes([3])
                clientSocket.sendall(msg)
                multiplayer_client()
            elif userInput == "n":
                msg = bytes([0])
                clientSocket.sendall(msg)
                singleplayer_client() 
        else:
            print("Please enter either 'y' or 'n' as a response. All other characters are invalid.\n")
    elif userInput == "n":
        sys.exit()
    else:
        print("Please enter either 'y' or 'n' as a response. All other characters are invalid.\n")
