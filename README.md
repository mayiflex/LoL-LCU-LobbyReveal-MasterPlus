# !BANNABLE!

Originally made by:
https://github.com/NoeMoyen/LoL-LCU-LobbyReveal

## Differences to the original version:
* Generally abbreviated the player stats chat messages to make them oneliners
* Abbreviated tier to only 1 letter (d for Diamond, p for Platinum)
* Changed romanian division numbers to good numbers 👍🏻
* Shows LP count for Master+ instead of div+tier
* Removed a lot of unecessary chat output
* Added silent mode to disable chat output
* Added unfriendly mode to disable multisearch chat message (still prints it in the console)
* Changed op.gg multisearch to porofessor pregame

# LoL-LCU-LobbyReveal
Python script that get the name of eatch memeber of the team in a ranked champ select, get the elo, winrate, and rank of eatch player, and print all the necessary information in the chat. 

## How to use
requirements: python
```
pip install lcu_driver
pip install riotwatcher
```
create a Riot Api key
https://developer.riotgames.com/
you need to past your api key line 20
```
api_key = '<RIOT API KEY>'
```

for create a LobbyReveal.exe 
```
pip install PyInstaller # if you don't have it
python3 -O -m PyInstaller LobbyReveal.py  --onefile -n LobbyReveal
``` 
the LobbyReveal.exe must be in ./dist/LobbyReveal.exe

or run normaly with python
```
python3 LobbyReveal.py
```
