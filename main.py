import asyncio
import logging
import sys
import random
import json
import time

from aiogram.filters.command import Command
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message, BotCommand
from aiogram.types.user import User
from aiogram.utils.markdown import hbold
from aiogram.utils.formatting import TextMention
from aiogram.client.session.aiohttp import AiohttpSession

session = AiohttpSession(proxy='http://proxy.server:3128')
bot = Bot('6860653852:AAGUPOMLGQwwPoGwa8pxMif-SDdl12hGDQo', session=session)
dp = Dispatcher()

name = ""
ev = {\
    "\n\n🎁 Вы нашли древнюю вазу с квасом 🍺🏺! (+0,1 к множителю)":{"chance":0.1,"item":"🕹 Геймпад (0,1 к множителю)","changes":{"multiplier":0.1}},\
    "\n\n💎 Вы обнаружили святыню блоба🌭! (+1000 л)":{"chance":0.002,"changes":{"score":1000}},\
    "\n\n🎁 Вам подарили пивоварню🍾🍾🍾! (+1 к множителю)":{"chance":0.01,"item":"🖥 Компьютер (1 к множителю)","changes":{"multiplier":1}}}
max_vals = {"multiplier":2^64,"wait_time":700}
min_vals = {"multiplier":0,"wait_time":5}

player_sample = {"score":0,"name":"Sample_Name","multiplier":1,"next_ability":0,"wait_time":3600,"items":{}}

players = {}
players = json.load(open("players.json"))

print(players)

def chance(c):
    return random.random()<=c

def check_for_events(ID):
    st = ""
    for i in ev.items():
        if (chance(i[1]["chance"])):
            st+=i[0]
            for j in i[1]["changes"].items():
                players[ID][j[0]]+=j[1]
                players[ID][j[0]]=max(min(max_vals[j[0]],players[ID][j[0]]),min_vals[j[0]])
            if ("item" in i[1]):
                if (i[1]["item"] in players[ID]["items"]):
                    players[ID]["items"][i[1]["item"]]=players[ID]["items"][i[1]["item"]]+1
                else:
                    players[ID]["items"][i[1]["item"]]=1
    return st

def to_time(t):
    t=max(t,0)
    s=t%60
    m=int(t/60)%60
    h=int(t/3600)%24
    d=int(t/86400)
    return (min(d,1)*f"{d} д ")+(min(h,1)*f"{h} ч ")+(min(m,1)*f"{m} мин ")+f"{s} сек"

async def save():
    global players
    players = {k: v for k, v in sorted(players.items(), key=lambda item: -item[1]["score"])}
    for i in player_sample.items():
        for j in players.items():
            if not (i[0] in j[1]):
                players[j[0]][i[0]]=i[1]
    json.dump(players,open("players.json","w"))

async def play(ID,chat):
    if players[ID]["next_ability"]<=time.time():
        adscore = int(((players[ID]["score"]+500)*players[ID]["multiplier"]*(random.random()+0.5))//250)
        players[ID]["score"]=players[ID]["score"]+adscore
        events = check_for_events(ID)
        players[ID]["next_ability"]=int(time.time()+players[ID]["wait_time"])
        await bot.send_message(chat_id=chat,text="🍺 {5} захлебнул {1}л \n\n🍺 Всего выпито: {2}л 🪙\n\n⏱ До следующей партии кваса: {3} {4}".format(ID,adscore,players[ID]["score"],to_time(int(players[ID]["next_ability"]-time.time()+1)),events,players[ID]["name"]).replace(".",","))
        await save()
    else:
        await bot.send_message(chat_id=chat,text="⏱ До следующей партии кваса: {0} ".format(to_time(int(players[ID]["next_ability"]-time.time()+1))))


async def check_reg(user_id,chat_id,usern):
    if (str(user_id) in players.keys()):
        await play(str(user_id),chat_id)
    else:
        players[str(user_id)]=player_sample
        players[str(user_id)]["name"]=usern
        await play(str(user_id),chat_id)

commands = {"квас": check_reg}

@dp.message(Command("kvass"))
async def playit(message: types.Message):
    await check_reg(message.from_user.id,message.chat.id,message.from_user.full_name)

@dp.message(Command("help"))
async def help(message: types.Message):
    await bot.send_message(chat_id=message.chat.id,text="КВААААААААААААААААААААААААААААААААААААААААААС🍺🍻🍺🍻🍺🍻🍺")

@dp.message(Command("start"))
async def help(message: types.Message):
    await bot.send_message(chat_id=message.chat.id,text="КВААААААААААААААААААААААААААААААААААААААААААС🍺🍻🍺🍻🍺🍻🍺")

@dp.message(Command("stata"))
async def stats(message: types.Message):
    plr = players[str(message.from_user.id)]
    players[str(message.from_user.id)]["name"]=message.from_user.full_name
    await bot.send_message(chat_id=message.chat.id,text="📈 Статистика игрока {0} \n🍻 Кваса выпито: {2}л 🍺  \n 🌭 Множитель: {3} \n⏱ Время работы пивоварни: {4} \n⏱ До следующей партии кваса: {5} ".format(plr["name"],str(message.from_user.id),plr["score"],round(plr["multiplier"],1),to_time(plr["wait_time"]),to_time(int(plr["next_ability"]-time.time()))).replace(".",","))

@dp.message(Command("top"))
async def top(message: types.Message):
    await save()
    top = "🏆 Топ игроков 🏆\n\n"
    j=1
    for i in players.items():
        top = top + f"{j} {i[1]['name']} - {i[1]['score']} \n"
        if (j==10):
            top = top + "..."
            break
        j=j+1
    if list(players.keys()).index(str(message.from_user.id))+1>j:
        top = top + f"\n{list(players.keys()).index(str(message.from_user.id))+1} {players[str(message.from_user.id)]['name']} - {players[str(message.from_user.id)]['score']} 🪙\n"
    await bot.send_message(chat_id=message.chat.id,text=top)

@dp.message()
async def tokenize(message: types.Message):
    mes = message.text.replace("\n"," ").lower().split()
    if (mes[0] in commands):
        await commands[mes[0]](message.from_user.id,message.chat.id,message.from_user.full_name)

async def main() -> None:
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
