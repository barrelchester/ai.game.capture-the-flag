# Capture the Flag Video Game

A capture-the-flag video game implemented in pygame and using AI Agents. 


## Goal of the Game

The game is played on a map whose left side is the Blue Team's Territory and the 
right side is the Red Team's Territory. Each Team's Territory has a Flag Area containing
the team's Flag colored appropriately. 

The goal is for a member of one team to get the flag of the other team and return to their
Flag Area with it.



## Players

The human player is on the blue team and is distinguished by a yellow outline. All other players are
intelligent agents using some configured algorithm for planning and movement.


### Movement
Keyboard movement is W=north, S=south, A=west, D=east.

When the game starts the player may move around on the map subject to the constraints 
of the Landscape.

### Tagging
If a player is in their home territory and contacts a player of the opposite team ("Opponent"), 
the opponent is "tagged" which renders them Incapacitated for a period of time.

A player carrying a flag can be tagged anywhere on the map.

### Incapacitation
A player becomes incapacitated and unable to move for a period of time if tagged. 
A player ceases to be incapacitated either by waiting or by being tagged (revived) by a member of their team ("Teammate").

### Capturing the Flag
A player may capture the opposing team's flag by making contact with it. They are then 
Carrying the flag.

If they are incapacitated, the flag is returned to its starting position. 
If they reach their Flag Area while Carrying the flag, their team wins and the game is over.



## Map Landscape

### Plains
Default land with no movement restrictions.

### Lakes
No movement is allowed on Lakes, they must be circumnavigated.

### Swamps/Hills/Mountains
Speed is reduced by 4, 6, and 8 respectively in Swamps, Hills, and Mountains.



## Map Zones

### Blue Side / Red Side
The left and right sides of the map respectively. Players are safe on their side and may not be tagged
by the opposing team unless carrying a flag.

### Blue Flag Zone / Red Flag Zone
The area surrounding the original position of the Flag. If a team player
enters this zone carrying the flag then their team wins.
