import socket
import sys
import time
import urllib.parse as urlparse
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST_NAME = 'localhost'
PORT_NUMBER = 9000

def loadMap():
    board = open(sys.argv[2],"r")
    spaces = board.read().split("\n")
    Matrix  = [["_" for x in range(10)] for y in range(10)]
    for y in range(0,9):
        for x in range(0,9):
            if(list(spaces[x])[y] != "_"):
                Matrix[x][y] = list(spaces[x])[y]
    return Matrix

def buildOpponent():
    Matrix  = [["_" for x in range(10)] for y in range(10)]
    return Matrix

print("own board:")
loadedMap = loadMap()
print(loadedMap)
print("opponent board:")
opponentMap = buildOpponent()
print(opponentMap)

def checkHit(board, x, y):
    currentBoard = board
    returnedVal = [0]
    isHit = 0
    if(currentBoard[x][y] != "_" and currentBoard[x][y] != "M"):
        isHit = 1
        returnedVal = [isHit, currentBoard[x][y]]
        ship = checkSunk(board, currentBoard[x][y], x, y)
        if(ship != 1):
            print("Ship Sunk")
            returnedVal = [isHit, currentBoard[x][y], ship]
    elif(currentBoard[x][y] == "M"):
        returnedVal = [isHit, "M"]
    else:
        currentBoard[x][y] = "M"
    if(isHit == 1):
        print("Hit")
    else:
        opponentMap[x][y] = "M"
        print("Miss")
        
    loadedMap = currentBoard
    return returnedVal

def checkSunk(board, typeShip, xCoord, yCoord):
    board[xCoord][yCoord] = "X"
    opponentMap[xCoord][yCoord] = "X"
    isFound = typeShip
    for x in range(0,9):
        for y in range(0,9):
            if(board[x][y] == typeShip):
                print("x: " + str(x) + " y: " + str(y))
                print(board[x][y] + " EQUALS " + typeShip)
                isFound = 1
    return isFound

def checkOutBounds(x,y):
    if(x > 9 or x < 0 or y > 9 or y < 0):
        return 1
    else:
        return 0

def checkMalformed(x,y):
    if(x is None or y is None):
        return 1 
    else:
        return 0

def reformatMap(inputMap):
    rtnStr = ""
    for x in range(0,9):
        rtnStr += (''.join(inputMap[x])) + "\n"
    return rtnStr
    
class BattleShipServer(BaseHTTPRequestHandler):
    def do_GET(self):
        print(self.client_address)
        self.send_response(200);
        self.send_header("hit", "done")
        self.end_headers()
        newMap = ""
        if(self.path == "/own_board.html"):
            newMap = reformatMap(loadedMap)
        if(self.path == "/opponent_board.html"):
            newMap = reformatMap(opponentMap)
        self.wfile.write(bytes(newMap,"utf-8"))
    def do_POST(self):
        parsed = urlparse.urlparse(self.path)
        x = urlparse.parse_qs(parsed.query)['x']
        y = urlparse.parse_qs(parsed.query)['y']
        if(checkOutBounds(int(x[0]),int(y[0]))==1):
            self.send_response(404)
            self.end_headers()
        elif(checkMalformed(x,y)):
            self.send_response(400)
            self.end_headers()
        else:
            shot = checkHit(loadedMap, int(x[0]), int(y[0]))
            if(len(shot) > 1):
                if((shot[1] == "X" or shot[1] == "M") and len(shot) < 3):
                    self.send_response(410)
                    self.end_headers()
                else:
                    self.send_response(200);
                    self.send_header("hit",str(shot[0]))
                    if(len(shot) > 2):
                        self.send_header("sunk", shot[2])
                    self.end_headers()
            else:
                self.send_response(200);
                self.send_header("hit",str(shot[0]))
                self.end_headers()
httpd = HTTPServer((HOST_NAME, PORT_NUMBER), BattleShipServer)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
httpd.server_close()
