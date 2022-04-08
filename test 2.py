from random import random
import telebot
from telebot import types
import uuid

BOT = telebot.TeleBot("")
USERS = {}
GAMES = {}

@BOT.message_handler(content_types=['text'])
def on_message(message):
    user_id = str(message.from_user.id)
    
    if message.text == '/start':
        nick = message.from_user.username
        USERS[user_id] = {"nick": nick, "games": 0, "wins": 0}
        BOT.send_message(user_id, "Registration successful!")
    
    if message.text == "/play":
        init_game(user_id)

def init_game(p1_id):
    p1_nick = USERS[p1_id]["nick"]
    all_ids = set(USERS.keys())
    all_ids.remove(p1_id)

    p2_id = random.choice(all_ids)
    p2_nick = USERS[p2_id]["nick"]
    
    game_id = uuid.uuid4()

    GAMES[game_id] = {"p1_id": p1_id, "p2_id": p2_id, "p1_move": None, "p2_move": None}

    BOT.send_message(p1_id, f"You will play with {p2_nick}", reply_markup=make_keyboard(game_id, p1_id))
    BOT.send_message(p2_id, f"You will play with {p1_nick}", reply_markup=make_keyboard(game_id, p2_id))

def make_keyboard(game_id, player_id):
    keyboard = types.InlineKeyboardMarkup(); 
    rock= types.InlineKeyboardButton(text='rock', callback_data=f"{game_id}_{player_id}_r")
    paper= types.InlineKeyboardButton(text='paper', callback_data=f"{game_id}_{player_id}_p" )
    scissors= types.InlineKeyboardButton(text='scissors', callback_data=f"{game_id}_{player_id}_s" )
    keyboard.add(rock) 
    keyboard.add(paper)
    keyboard.add(scissors)

    return keyboard


@BOT.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    items = call.data.split("_")
    game_id, player_id, move = items

    process_game(game_id, player_id, move)


def process_game(game_id, player_id, move):
    game = GAMES[game_id]

    if player_id == game["p1_id"] and game["p1_move"] == None:
        game["p1_move"] = move
    
    if player_id == game["p2_id"] and game["p2_move"] == None:
        game["p2_move"] = move
    
    check_game(game_id)


def check_game(game_id):
    game = GAMES[game_id]
    p1_id = game["p1_id"]
    p2_id = game["p2_id"]
    p1_nick = USERS[p1_id]['nick']
    p2_nick = USERS[p2_id]['nick']

    if game["p1_move"] == None or game["p2_move"] == None:
        return
    
    if game["p1_move"] == game["p2_move"]:
        BOT.send_message(p1_id, f"Draw with {USERS[p2_id]['nick']}")
        BOT.send_message(p2_id, f"Draw with {USERS[p1_id]['nick']}")

        game["p1_move"] = None
        game["p2_move"] = None

        BOT.send_message(p1_id, f"Rematch with {p2_nick}", reply_markup=make_keyboard(game_id, p1_id))
        BOT.send_message(p2_id, f"Rematch with {p1_nick}", reply_markup=make_keyboard(game_id, p2_id))
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

        BOT.send_message(winner_id, f"You win! {USERS[loser_id]['nick']} Lost!")
        BOT.send_message(loser_id, f"Loser! {USERS[winner_id]['nick']} dominates!")

        USERS[winner_id]["games"] = USERS[winner_id]["games"] + 1
        USERS[loser_id]["games"] = USERS[loser_id]["games"] + 1

        USERS[winner_id]["wins"] = USERS[winner_id]["wins"] + 1
        

BOT.polling(none_stop=True)
