import sys
import requests
from urllib3 import disable_warnings
import json
from time import sleep
import platform
import psutil
import base64
from os import system, name
from lcu_driver import Connector
from riotwatcher import LolWatcher, ApiError
import urllib.parse
import webbrowser

disable_warnings()

# global variables

api_key = '<YOUR_API_KEY>'
watcher = LolWatcher(api_key)
my_region = 'euw1'
#silent = no chat messages
silent=False;
#send multisearch
friendly=True;

app_port = None
auth_token = None
riotclient_auth_token = None
riotclient_app_port = None
region = None
lcu_name = None  # LeagueClientUx executable name
showNotInChampSelect = True

# functions


def getLCUName():
    '''
    Get LeagueClient executable name depending on platform.
    '''
    global lcu_name
    if platform.system() == 'Windows':
        lcu_name = 'LeagueClientUx.exe'
    elif platform.system() == 'Darwin':
        lcu_name = 'LeagueClientUx'
    elif platform.system() == 'Linux':
        lcu_name = 'LeagueClientUx'


def LCUAvailable():
    '''
    Check whether a client is available.
    '''
    return lcu_name in (p.name() for p in psutil.process_iter())


def getLCUArguments():
    global auth_token, app_port, region, riotclient_auth_token, riotclient_app_port
    '''
    Get region, remoting-auth-token and app-port for LeagueClientUx.
    '''
    if not LCUAvailable():
        sys.exit('No ' + lcu_name + ' found. Login to an account and try again.')

    for p in psutil.process_iter():
        if p.name() == lcu_name:
            args = p.cmdline()

            for a in args:
                if '--region=' in a:
                    region = a.split('--region=', 1)[1].lower()
                if '--remoting-auth-token=' in a:
                    auth_token = a.split('--remoting-auth-token=', 1)[1]
                if '--app-port' in a:
                    app_port = a.split('--app-port=', 1)[1]
                if '--riotclient-auth-token=' in a:
                    riotclient_auth_token = a.split('--riotclient-auth-token=', 1)[1]
                if '--riotclient-app-port=' in a:
                    riotclient_app_port = a.split('--riotclient-app-port=', 1)[1]

                    
def clear():
    # for windows
    if name == 'nt':
        _ = system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')


connector = Connector()
@connector.ready

async def connect(connection):
    
    global showNotInChampSelect

    getLCUName()

    getLCUArguments()

    lcu_api = 'https://127.0.0.1:' + app_port
    riotclient_api = 'https://127.0.0.1:' + riotclient_app_port

    lcu_session_token = base64.b64encode(
        ('riot:' + auth_token).encode('ascii')).decode('ascii')

    riotclient_session_token = base64.b64encode(
        ('riot:' + riotclient_auth_token).encode('ascii')).decode('ascii')

    lcu_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Basic ' + lcu_session_token
    }

    riotclient_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'LeagueOfLegendsClient',
        'Authorization': 'Basic ' + riotclient_session_token
    }

    get_current_summoner = lcu_api + '/lol-summoner/v1/current-summoner'

    r = requests.get(get_current_summoner, headers=lcu_headers, verify=False)
    r = json.loads(r.text)
    print("Welcome to LobbyReveal Masters+! :)")
    print('Connected: ' + r['displayName'])

    try :
        checkForLobby = True
        while True:
            playernames = []
            get_champ_select = lcu_api + '/lol-champ-select/v1/session'
            r = requests.get(get_champ_select, headers=lcu_headers, verify=False)
            r = json.loads(r.text)
            if 'errorCode' in r:
                checkForLobby = True
                if showNotInChampSelect:
                    print('Not in champ select. Waiting for game...')
                    showNotInChampSelect = False
            else:
                if checkForLobby:
                    clear()
                    print('\n* Found lobby. *\n')
                    while 1:
                        try:
                            get_lobby = riotclient_api + '/chat/v5/participants/champ-select'
                            r = requests.get(get_lobby, headers=riotclient_headers, verify=False)
                            r = json.loads(r.text)
                        except:
                            print("la route n'existe plus, logiciel obselète")
                        playernames = [] 
                        playernamesUrlencoded = []
                        ranked_stats = []
                        nbPlayers = 5
                        try:
                            getChat = await connection.request('get', "/lol-chat/v1/conversations")
                            chat = await getChat.json()
                        except KeyError:
                            print("error in get conversation")
                        for i in range(len(chat)):
                            if chat[i]['type'] == "championSelect":
                                try:
                                    lobbyID = chat[i]["id"]
                                except KeyError:
                                    print("error in get lobby id")
                                headers = {'Content-type': 'application/json'}
                                messageRequestEndpoint = "/lol-chat/v1/conversations/" + str(lobbyID) + "/messages"
                                for x in r['participants']:
                                    playernames.append(x['game_name'])
                                    playernamesUrlencoded.append(urllib.parse.quote(x['game_name']))
                                if(len(playernames) > 1):
                                    if(len(playernames) != nbPlayers):
                                        print("Unable to fetch " + str(nbPlayers - len(playernames)) + " players!:c");
                                        if not silent:
                                            await connection.request('post', messageRequestEndpoint, headers=headers, data={"type":"chat", "body": "Unable to fetch " + str(nbPlayers - len(playernames)) + " players!:c"})
                                    for i in range(len(playernames)):
                                        try:
                                            user_id = watcher.summoner.by_name(my_region, playernames[i])['id']
                                            try: 
                                                ranked_stats = watcher.league.by_summoner(my_region, user_id)
                                                #search for solo duo stats
                                                for j in range(len(ranked_stats)):
                                                    try:
                                                        if ranked_stats[j]['queueType'] == "RANKED_SOLO_5x5":
                                                            tier = ranked_stats[j]['tier']
                                                            division = ranked_stats[j]['rank']
                                                            wins = ranked_stats[j]['wins']
                                                            losses = ranked_stats[j]['losses']
                                                            lp = ranked_stats[j]['leaguePoints']
                                                            gameCount = wins + losses
                                                            winrate = wins / gameCount * 100
                                                            elo = "";
                                                            if tier not in ["MASTER", "GRANDMASTER", "CHALLENGER"]:
                                                                elo = str(tier)[:1].lower()
                                                                match division:
                                                                    case "IV":
                                                                        elo += str(4);
                                                                    case "III":
                                                                        elo += str(3);
                                                                    case "II":
                                                                        elo += str(2);
                                                                    case "I":
                                                                        elo += str(1);
                                                                    case _:
                                                                        elo += " " + division;
                                                            else:
                                                                elo = str(lp) + "LP"
                                                            playerInfoMessage = str(playernames[i]) + ": " + elo + " " + str(round(winrate,1)) + "% in " + str(gameCount);
                                                            print(playerInfoMessage);
                                                    except KeyError:
                                                        print("keyerror");
                                                if not silent:
                                                    await connection.request('post', messageRequestEndpoint, headers=headers, data={"type":"chat", "body": playerInfoMessage})
                                            except ApiError:
                                                print("error in get ranked stats")
                                        except ApiError:
                                            print("error in get user id. check your api key ?")
                                    pregame = "https://porofessor.gg/pregame/" + my_region[:-1] + "/";
                                    for player in playernamesUrlencoded:
                                        pregame += player + ","
                                    pregame = pregame[:-1] + "/soloqueue"
                                    if not silent:
                                        if friendly:
                                            await connection.request('post', messageRequestEndpoint, headers=headers, data={"type":"chat", "body": pregame})
                                        await connection.request('post', messageRequestEndpoint, headers=headers, data={"type":"chat", "body": "lobby seems sussy ඞ"})
                                    print(pregame);
                                    webbrowser.open(pregame, new=2, autoraise=False)
                                    print("\r\nCreated by \r\nGitHub: NoeMoyen");
                                    print("Forked by\r\nhttps://mayiflex.dev");
                                    showNotInChampSelect = True
                                    checkForLobby = True 
                                    exit(0)
    except KeyboardInterrupt:
        print('\n\n* Exiting... *')
        sys.exit(0)

connector.start()