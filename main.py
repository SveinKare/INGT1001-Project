#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
from pybricks.messaging import BluetoothMailboxServer, TextMailbox
import sys


ev3 = EV3Brick()
#This motor moves the "bridge"
bridge = Motor(Port.A)
#This motor moves the "trolley"
trolley = Motor(Port.B)
#This motor moves the "hook"
hook = Motor(Port.C)

#Constants used when moving the different parts. 
ONE_ROW = 485
ONE_LANE = -57
DEFAULT_POS = "a1"
CURRENT_POSITION = "a1"
GARBAGE_CAN = "a9"
MOVE_HOOK = 200
#Dictionary to convert between letters and numbers
required_Moves = {
    "a" : 0,
    "b" : 1,
    "c" : 2,
    "d" : 3,
    "e" : 4,
    "f" : 5,
    "g" : 6,
    "h" : 7
}

#Moves the crane into position over a certain square given as a string in the format "e2"
def move_to_square(square):
    global CURRENT_POSITION
    letter = required_Moves[square[0]] - required_Moves[CURRENT_POSITION[0]]
    number = int(square[1]) - int(CURRENT_POSITION[1])
    for i in range(0,abs(number)):
        #Checks if the crane has to move forwards or backwards.
        if number < 0:
            bridge.run_time(-ONE_ROW, 1200)
        else:
            bridge.run_time(ONE_ROW, 1200)
    for i in range(0,abs(letter)):
        #Checks if the trolley has to move left or right
        if letter < 0:
            trolley.run_time(-ONE_LANE, 1200)
        else:
            trolley.run_time(ONE_LANE, 1200)
    CURRENT_POSITION = square

#Runs hook up or down. Negative is down, positive is up
def move_hook(amount):
    hook.run_time(amount, 1500)

#Resets the crane to ensure precision
def park():
    global DEFAULT_POS
    move_to_square(DEFAULT_POS)
    bridge.run_time(-70, 1000)

#Executes a legal chess move.
def move(chessMove):
    global MOVE_HOOK
    moveFrom = chessMove[0:2]
    moveTo = chessMove[2:5]
    #Checks if move is capture
    if (chessMove[5] == "c"):
        #Move is capture
        if (chessMove[4] == "d"):
            #Move is direct capture
            capture(moveTo)
        if (chessMove[4] == "p"):
            #Move is passant capture
            en_passant_capture(chessMove[0:5])

    #Checks if move is castle
    if chessMove[4] == "r":
        castle(chessMove)
    #Picks up piece
    move_to_square(moveFrom)
    trolley.run_time(-40,1000)
    move_hook(-MOVE_HOOK)
    trolley.run_time(40,1000)
    move_hook(MOVE_HOOK)

    #Puts it down.
    move_to_square(moveTo)
    move_hook(-MOVE_HOOK)
    trolley.run_time(-40,1000)
    move_hook(MOVE_HOOK)
    trolley.run_time(40,1000)

#Function for direct capture of a piece
def capture(square):
    global GARBAGE_CAN
    global MOVE_HOOK

    move_to_square(square)
    trolley.run_time(-40,1000)
    move_hook(-MOVE_HOOK)
    trolley.run_time(70,1000)
    move_hook(MOVE_HOOK)
    trolley.run_time(-30,1000)

    move_to_square(GARBAGE_CAN)
    move_hook(-MOVE_HOOK)
    trolley.run_time(-40,1000)
    move_hook(MOVE_HOOK)
    trolley.run_time(40,1000)

#Function for en passant capture
def en_passant_capture(chessMove):
    capture_square = chessMove[2] + chessMove[1]
    capture(capture_square)

def castle(chessMove):
    number = chessMove[1]
    moveFrom = ""
    moveTo = ""
    #Queen side castle
    if chessMove[5] == "q":
        moveFrom = moveFrom + "a"
        moveTo = moveTo + "d"
    #King side castle
    if chessMove[5] == "k":
        moveFrom = moveFrom + "h"
        moveTo = moveTo + "f"
    moveFrom = moveFrom + number
    moveTo = moveTo + number
    castleMove = moveFrom + moveTo + "nn"
    move(castleMove)


#Takes input from user while the client is running. 
while True:
    #User move is executed
    sys.stderr.write("Input your move, or type \"resign\" to give up: \n")
    userMove = input()
    sys.stderr.write("Move registered\n")
    move(userMove)
    park()

    #Stockfish move is executed
    sfMove = input()
    sys.stderr.write("A move is being executed, please wait...\n")
    move(sfMove)
    park()





