import telebot
from telebot import types;
import json
import random
import uuid

BOT = telebot.TeleBot("")
USERS = {}
GAMES = {}


try:
    with open("database.json", "r") as dbfile:
        all_lines = dbfile.readlines()
        joined_lines = "".join(all_lines)
        USERS = json.loads(joined_lines)
except:
    pass

try:
    with open("database2.json", "r") as dbfile:
        all_lines = dbfile.readlines()
        joined_lines = "".join(all_lines)
        GAMES = json.loads(joined_lines)
except:
    pass

@BOT.message_handler(content_types=['text'])
def on_message(message):
    user_id = str(message.from_user.id)
    if (message.text == '/start') or (message.text == '/help') or (message.text == '/play') or (message.text == '/mystats')  or (message.text == '/topwinners') or (message.text == '/topgamers') or (message.text == '/gamerlist') or (message.text.find('/play @')>(-1)):
        if message.text == '/start':
            nick = message.from_user.username
            if not user_id in USERS :
                USERS[user_id] = {"nick": nick, "games": 0, "wins": 0}
                write_json()
                BOT.send_message(user_id, "Registration successful!\n This bot have a few commands. Check them by writing /help")
            else:    
                BOT.send_message(user_id, "This bot have a few command. Check them by write /help")
        if message.text == "/play":
            init_game(user_id)
        if message.text == "/help":
            BOT.send_message(user_id, "Command list with description:\n\n/start - registration\n/help - list of commands\n/mystats - your statisctics\n/gamerlist - list of all registered gamers\n/topwinners - list of top winners\n/topgamers - list of top gamers\n/play - play with RANDOM REGISTERED user\n/play @*someone* - play with a CERTAIN REGISTERED user")
        if message.text == '/mystats':
            mystats(user_id)
        if message.text == '/topwinners':
            topwinners(message)
        if message.text == '/topgamers':
            topgamers(message)
        if message.text == '/gamerlist':
            gamer_list(message)
        if message.text.find('/play @')>(-1):
            items = message.text.split('@')
            p2_nick = items[1]
            init_game2(user_id, p2_nick)
    else:
        BOT.send_message(user_id, "I don't understand you")

def init_game(p1_id):
    p1_nick=USERS[p1_id]['nick']
    all_ids=set(USERS.keys())
    all_ids.remove(p1_id)

    p2_id=random.choice(list(all_ids))
    p2_nick=USERS[p2_id]['nick']
    
    game_id=str(uuid.uuid4())

    GAMES[game_id] = {'p1_id':p1_id, 'p2_id' : p2_id, 'p1_move' : None, 'p2_move' : None}
    print(f"Game created: {game_id} / {p1_nick} / {p2_nick}")

    BOT.send_message(p1_id, f'You will play with @{p2_nick}', reply_markup=keyboard(game_id, p1_id))
    BOT.send_message(p2_id, f'You will play with @{p1_nick}', reply_markup=keyboard(game_id, p2_id))

def init_game2(p1_id, p2_nick):
    p1_nick=USERS[p1_id]['nick']
    all_ids=set(USERS.keys())
    all_ids.remove(p1_id)
    p2_id = None
    if p2_nick == p1_nick:
        '''BOT.send_message(p1_id, 'По-моему ты что-то перепутал')'''
        data = open('1.mp4','rb')
        BOT.send_video(p1_id, data)
        data.close()
    else:
        for (key, value) in USERS.items():
            if value ['nick'] == p2_nick:
                p2_id = key

                game_id=str(uuid.uuid4())

                GAMES[game_id] = {'p1_id':p1_id, 'p2_id' : p2_id, 'p1_move' : None, 'p2_move' : None}
                print(f"Game created: {game_id} / {p1_nick} / {p2_nick}")

                BOT.send_message(p1_id, f'You will play with @{p2_nick}', reply_markup=keyboard(game_id, p1_id))
                BOT.send_message(p2_id, f'You will play with @{p1_nick}', reply_markup=keyboard(game_id, p2_id))
        if p2_id == None:
            BOT.send_message(p1_id, 'This user is not registrated!')

def keyboard(game_id, p_id):
    keyboard = types.InlineKeyboardMarkup(); 
    rock = types.InlineKeyboardButton(text='rock', callback_data=f"{game_id}_{p_id}_r")
    paper = types.InlineKeyboardButton(text='paper', callback_data=f"{game_id}_{p_id}_p")
    scissors = types.InlineKeyboardButton(text='scissors', callback_data=f"{game_id}_{p_id}_s")
    keyboard.add(rock) 
    keyboard.add(paper)
    keyboard.add(scissors)

    return keyboard


@BOT.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    items = call.data.split("_")
    game_id, p_id, move = items
    nick = USERS[p_id]["nick"]
    print(f"{game_id} {nick} {move}")
    BOT.edit_message_reply_markup(p_id, call.message.id, reply_markup=None)
    process_game(game_id, p_id, move)


def process_game(game_id, p_id, move):
    game = GAMES.get(game_id)
    if game is None:
        BOT.send_message(p_id, "Sorry, game info was lost somehow! Pls /play again")
    else:
        if p_id == game['p1_id'] and game['p1_move']== None:
            game['p1_move']  = move
            write_json2()
        if p_id == game['p2_id'] and game['p2_move']== None:
            game['p2_move']  = move
            write_json2()
        check_game(game_id)

def check_game(game_id):
    game = GAMES[game_id]
    p1_id = game['p1_id']
    p2_id = game['p2_id']
    p1_nick = USERS[p1_id]['nick']
    p2_nick = USERS[p2_id]['nick']

    if game['p1_move'] == None or game['p2_move'] == None:
        return
    
    if game['p1_move'] == game['p2_move']:
        BOT.send_message(p1_id, f"Draw with @{USERS[p2_id]['nick']}")
        BOT.send_message(p2_id, f"Draw with @{USERS[p1_id]['nick']}")

        game["p1_move"] = None
        game["p2_move"] = None

        BOT.send_message(p1_id, f"Rematch with @{p2_nick}", reply_markup=keyboard(game_id, p1_id))
        BOT.send_message(p2_id, f"Rematch with @{p1_nick}", reply_markup=keyboard(game_id, p2_id))
    else:
        first_wins = (("r", "s"), ("s", "p"), ("p", "r"))
        winner_id = None
        loser_id = None
        
        if (game["p1_move"], game["p2_move"]) in first_wins:
            winner_id = p1_id
            loser_id = p2_id
        else:
            winner_id = p2_id
            loser_id = p1_id

        BOT.send_message(winner_id, f"You win! @{USERS[loser_id]['nick']} Lost!")
        BOT.send_message(loser_id, f"Loser! @{USERS[winner_id]['nick']} dominates!")

        USERS[winner_id]["games"] = USERS[winner_id]["games"] + 1
        USERS[loser_id]["games"] = USERS[loser_id]["games"] + 1

        USERS[winner_id]["wins"] = USERS[winner_id]["wins"] + 1
        write_json()
    
def write_json():
    with open('database.json', 'w') as file:
        json_line =  json.dumps(USERS, indent=4, ensure_ascii=False)
        file.write(json_line)
def write_json2():
    with open('database2.json', 'w') as file:
        json_line =  json.dumps(GAMES, indent=4, ensure_ascii=False)
        file.write(json_line)
    
def mystats(user_id):
    wins = USERS[user_id]['wins']
    games = USERS[user_id]['games']
    BOT.send_message(user_id, f'Your states:\nwins - {wins}\ngames - {games}')

def topwinners (message):
    rate = []
    user_id=message.from_user.id
    for key, value in USERS.items():
        rate.append([value["wins"], value["nick"]])
    rate.sort(reverse=True)
    output = []
    for line in rate:
        output.append(f"@{line[1]} has won {line[0]} games")
    final_output = "\n".join(output)
    BOT.send_message(user_id, 'Top winners\n\n' + final_output)

def topgamers (message):
    rate = []
    user_id=message.from_user.id
    for key, value in USERS.items():
        rate.append([value["games"], value["nick"]])
    rate.sort(reverse=True)
    output = []
    for line in rate:
        output.append(f"@{line[1]} has played {line[0]} games")
    final_output = "\n".join(output)
    BOT.send_message(user_id, 'Top players\n\n' + final_output)

def gamer_list(message):
    rate = []
    output = []
    user_id=message.from_user.id
    for key, value in USERS.items():
        rate.append(value["nick"])
    for line in rate:
        output.append(f"@{line}")
    final_output = "\n".join(output)
    BOT.send_message(user_id, 'Gamer list:\n\n' + final_output)
    
BOT.polling(none_stop=True)
