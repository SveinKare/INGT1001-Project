# INGT1001-Project
This repository contains the two files used to make a chess-robot using EV3 Lego Mindstorm hardware. The robot is operated from the ChessClient.py file, which creates an SSH terminal via bluetooth to send commands to the brick. The commands are strings formatted using a self-defined protocol where the first two symbols designate the square to move from, the next two symbols are the square to move to, and the last two symbols describe whether the move is of a special type (capture, passant capture, castle etc.). The main.py file is run by the brick. 
