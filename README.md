# KamenozrutServer
This is a server side code for multiplayer in my implementation of game Kamenozrut. Client side code can be found [here](https://github.com/Johnny974/Kamenozrut)

## Basic functions 
This server handles connection of clients through sockets, can receive and handle more message types depending on specific JSON format, also stores important data into its own sqlite database and validates that data. Simple matchmaking is also implemented in this code.

## Future work
Currently, I am working on multiplayer match. I am building on the matchmaking foundation, now I just need to add the exchange of moves and game updates. 
