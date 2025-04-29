Jumia Chess is a checkers game featuring singleplayer against an AI model, local multiplayer and online gameplay
with a simple and user-friendly design

To launch the game execute the game_launcher.py (make sure the working directory is the project directory "Projet-reseau-DRL-main")

A main menu will pop up and the player can choose their preferred gamemode.

AI opponent in singleplayer is trained using MaskablePPO with Stable_Baselines3
It uses a custom feature extractor to combine the board state and action mask with
a fully implemented draw logic to stabilize training and ensure realistic outcomes.

the training is managed using :train_visualization.py-checkers_env.py


Notes:
- singleplayer.py may take a few seconds to launch as it is loading the model.
-numpy and sb3_contrib libraries are required to run SinglePlayer mode.

The online multiplayer feature in the game is built using Python’s standard 
libraries—socket for TCP connections, pickle for data serialization, and threading for
handling multiple clients. It follows a client-server model where one player hosts a 
server and the other joins by entering the host's IP. The server listens for two clients,
and once connected, relays moves between them in real-time. Each move made by one player 
is serialized and sent to the server, which then forwards it to the other client, allowing
both game states to stay synchronized. The network system is lightweight, does not rely on
any external dependencies, and is designed to be simple yet robust for peer-to-peer gameplay.

online is managed by these files in the network folder:network.py-host.py-join.py in the network folder

to use online the player must press the "host online game" button and wait for the opponent to join.
the opponent must open the game while connected to the same WiFi network as the player and click "join online game" button.

Note:
-some latency may be noticeable during online play

This project was made by Oussema Boulila L1BCG6TP1,Mohamed Yassine Rached L1BCG5,AmenAllah Benali L1BCG6TP2

DEVELOPMENT TEAM

    Gameplay Programming & AI Systems: Oussema Boulila

    Network Programming (Client/Server Architecture): Yassine Rached

    UI/UX Design & Media Integration (Main Menu Systems): Amen Allah Ben Ali

