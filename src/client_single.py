# client.py
import socket
import sys

ip_addr = sys.argv[1]
port = int(sys.argv[2])

while True:
    userInput = input("Ready to start game? (y/n): ")
    if userInput == "y": 
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        clientSocket.connect((ip_addr, port))
        msg = bytes([0])
        clientSocket.sendall(msg)
        guessedLetters = []
        cont = True
        while True:
            recvBuf = clientSocket.recv(1024)
            if (recvBuf != b''):

                # display output
                decodedBuf = recvBuf.decode('ascii')
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
                    print()
                    print()
                if (("_" not in decodedBuf[3: 3 + recvBuf[1]]) or (recvBuf[2] >= 6)):
                    clientSocket.sendall(bytes([2]))
                    cont = False
                if cont:
                    correctInput = False
                    userLetter = ""
                    while not(correctInput):
                        userLetter = input("Letter to guess: ")
                        if ((len(userLetter) > 1) or not(userLetter.isalpha())):
                            print("Error! Please guess one letter.\n")
                        elif (userLetter.lower() in guessedLetters):
                            s = "Error! Letter " + userLetter.lower() + " has been guessed before, please guess another letter."
                            print(s)
                        else:
                            correctInput = True

                    clientSocket.sendall(bytes([1]) + userLetter.lower().encode('ascii'))
                    guessedLetters.append(userLetter.lower())


    elif userInput == "n":
        sys.exit()
    else:
        print("Please enter either 'y' or 'n' as a response. All other characters are invalid.\n")
