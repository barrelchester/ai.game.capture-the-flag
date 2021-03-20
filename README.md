# Capture the Flag Video Game

A capture-the-flag video game implemented in pygame and using AI Agents. 


## Goal of the Game

The game is played on a map whose left side is the Blue Team's Territory and the 
right side is the Red Team's Territory. Each Team's Territory has a Flag Area containing
the team's Flag colored appropriately. 

The goal is for a member of one team to get the flag of the other team and return to their
Flag Area with it.


## Game Modes

The game may be run in Observation Mode or Play Mode.

Observation Mode contains only Non-Player Characters (NPCs/Agents).
Play Mode allows a human player and NPCs.


## Players

The number of players on each Team is variable; from 1 to 10.

### Movement
When the game starts the player may move around on the map subject to the constraints 
of the Landscape and subject to any player attributes that affect movement.

### Tagging
If a player is in their home territory and contacts a player of the opposite team ("Opponent"), 
the opponent is "tagged" which renders them Incapacitated.

### Incapacitation
A player may become incapacitated by various means. While incapacitated, the player is unable to move.
A player may cease to be incapacitated either by waiting for their Energy Level to rise above a
minimum threshold, or by being Tagged by a member of their team ("Teammate").

### Capturing the Flag
A player may capture the opposing team's flag by making contact with it. They are then 
Carrying the flag.

If they are incapacitated, the flag is dropped next to them. 
If they reach their Flag Area while Carrying the flag, their team wins and the game is over.


## Player Attributes

Players have several attributes which affect their actions.

### Speed
The player's baseline integer valued Speed. When navigating certain Landscape elements, 
their Speed is reduced.

### Energy
The player's baseline integer valued Energy. Energy affects the player's Speed. 
When Energy is 0, the player is in a state of Incapacitatation. 

Movement reduces Energy. Not moving increases Energy up to the baseline amount.

When a player contacts a Teammate, both have their Energy increased ("Cooperation").


## Map Landscape

### Plains
Default land with no movement restrictions.

### Lakes
No movement is allowed on Lakes, they must be circumnavigated.

### Chasms
No movement is allowed on Chasms except at Bridges.

### Swamps/Hills/Mountains
Speed is reduced by 2, 4, and 6 respectively in Swamps, Hills, and Mountains.


## Map Zones

### Blue Side
The left side of the map. Blue Team players are safe in this zone and may not be tagged
by the opposing team.

### Red Side
The right side of the map. Red Team players are safe in this zone and may not be tagged
by the opposing team.

### Blue Flag Zone
The area surrounding the original position of the Blue Flag. If a Blue team player
enters this zone carrying the Red flag then the Blue team wins.

### Red Flag Zone
The area surrounding the original position of the Red Flag. If a Red team player
enters this zone carrying the Blue flag then the Red team wins.