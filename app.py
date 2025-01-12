import logging
import asyncio
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes, filters

from telegram import Update
import re
import tgm
import nextgis_connector as nextgis


target_group_id = [-1002394189272, -1002352127143, -1002276105317] # 

forward_group = -1002335708322 # Анапа. Мониторинг координат

thanks_message = "\nСкиньте пожалуйста в чат несколько фотографий."

forward_list = []

with open("__token_sosbird_bot_chat_parser.txt", "r") as f:
    TELEGRAM_BOT_TOKEN = f.read()

def get_r(A, B):
    r = ((A[0] - B[0])**2 + (A[1] - B[1])**2)**0.5
    return r

def get_region(lat, lon):
    anapa = [[44.982265, 37.247752],[45.098649, 36.924302]]
    NR = [[44.7, 37.7],[44.73, 37.42]]
    sochi = [[43.6, 39.71],[44.08, 39.03]]
    anapa.append(get_r(anapa[0], anapa[1]))
    NR.append(get_r(NR[0], NR[1]))
    sochi.append(get_r(sochi[0], sochi[1]))

    if get_r([float(lat), float(lon)], anapa[0]) < anapa[2]:
        return "Анапа"
    if get_r([float(lat), float(lon)], NR[0]) < NR[2]:
        return "Новороссийск"
    if get_r([float(lat), float(lon)], sochi[0]) < sochi[2]:
        return "Сочи"
    return "Иное"



def get_coord_from_text(text):
    latitude_pattern = r"4[2-7]\.\d{5,7}"
    longitude_pattern = r"3[5-9]\.\d{5,7}"
    all_lat = re.findall(latitude_pattern, text.replace(",", "."))
    all_lon = re.findall(longitude_pattern, text.replace(",", "."))
    return all_lat, all_lon

def send_to_gis(query, layer):
    #Check if this comment come from prser user-bot.
    #print(json.dumps(query.to_dict(), indent = 4))
    user_message_part = query["message"]["reply_to_message"]["text"]
    system_message_part = query["message"]["text"].split("-"*25)[1]
    message = query["message"]
    tg_link = None
    if user_message_part[:4] == "2025" and user_message_part.split("\n")[2][:12] == "https://t.me":
        # Message from our chat-parser user bot
        print("[..] Bot message")
        tg_link = user_message_part.split("\n")[2] 
        user_message_part = "\n".join(user_message_part.split("\n")[3:])
    else:
        # Normal message
        print("[..] User message")
        tg_link = f'https://t.me/c/{str(message["chat"]["id"])[4:]}/{message["reply_to_message"]["message_id"]}'
    
    prio = 0
    if "срочно" in str(message):
        prio = 1

    comment = system_message_part + "\n" + user_message_part
    lat_list, lon_list = get_coord_from_text(query["message"]["text"])
    lat = lat_list[0].strip()
    lon = lon_list[0].strip()

    nextgis.add_point(
            lat = lat, 
            lon = lon, 
            comment = comment, #query["message"]["text"].split("-"*25)[0], 
            dtime = message["date"],
            tg_link = tg_link, 
            layer_name = layer, 
            prio = prio, region = get_region(lat, lon)
    )


keyboard_text_node_main = {
        "edge1_bird":"Грязная птица. Нужен отлов!",
        "edge2_bird_catch":"Птица поймана. Заберите!",
        "edge3_oil":"Загрязнение",
        "edge4_dead_animal":"Мертвое животное",
        "edge5_cancel":"Закрыть"
}
keyboard_text_node1X = {
        "edge11_bird_one":"Меньше 3",
        "edge12_bird_three":"3..5",
        "edge13_bird_many":"Больше 5",
        "edge14_back":"Назад"
}
keyboard_text_node1XX = {
        "edge1X1_bird_far_in_sea":"Далеко в море", 
        "edge1X2_bird_three":"Около берега", 
        "edge1X3_bird_many":"На берегу",
        "edge1X4_back":"Назад"
}
keyboard_text_node1XXX = {
        "edge1XX1_bird_Active":"Активная", 
        "edge1XX2_bird_weak":"Чистится, убегает", 
        "edge1XX3_bird_weak":"Чистится, не убегает", 
        "edge1XX4_bird_urgent":"Еле живая (срочно!)",
        "edge1XX5_back":"Назад"
}
keyboard_text_node1XXXX = {
        "edge1XXX1_done":"Готово", 
        "edge1XXX2_cancel":"Отмена",
        "edge1XXX3_back":"Назад"
}

keyboard_text_node2X = {
        "edge21_bird_one":"Меньше 3",
        "edge22_bird_three":"3..5",
        "edge23_bird_many":"Больше 5",
        "edge24_back":"Назад"
}
keyboard_text_node2XX = {
        "edge2X1_done":"Готово", 
        "edge2X2_cancel":"Отмена",
        "edge2X3_back":"Назад"
}

keyboard_text_node3X = {
        "edge31_bags50":"Мешки до 50",
        "edge32_bags100":"Мешки до 50-100",
        "edge33_bags200":"Мешки до >100",
        "edge34_oil":"Мазут",
        "edge35_back":"Назад"
}
keyboard_text_node3XX = {
        "edge3X1_done":"Готово", 
        "edge3X2_cancel":"Отмена",
        "edge3X3_back":"Назад",
}

keyboard_text_node4X = {
        "edge41_dolphin":"Дельфин",
        "edge42_bird":"Птица",
        "edge43_other":"Другое",
        "edge44_back":"Назад",
}
keyboard_text_node4XX = {
        "edge4X1_done":"Готово", 
        "edge4X2_cancel":"Отмена",
        "edge4X3_back":"Назад"
}

def keyboard_text_node1_handler(query):
    text = f'{query["message"]["text"]}\n{"-"*25}\n{keyboard_text_node_main[query.data]}'
    keyboard = None
    if query.data == "edge1_bird":
        keyboard = tgm.make_inline_keyboard(keyboard_text_node1X)
    if query.data == "edge2_bird_catch":
        keyboard = tgm.make_inline_keyboard(keyboard_text_node2X)
    if query.data == "edge3_oil":
        keyboard = tgm.make_inline_keyboard(keyboard_text_node3X)
    if query.data == "edge4_dead_animal":
        keyboard = tgm.make_inline_keyboard(keyboard_text_node4X)
    if query.data == "edge5_cancel":
        keyboard = None
    return text, keyboard

def keyboard_text_node1X_handler(query):
    if query.data == "edge14_back":
        text = query["message"]["text"]
        text = text[:text.rfind('\n')]
        text = text[:text.rfind('\n')] # Remove to lines (----) also.
        keyboard = tgm.make_inline_keyboard(keyboard_text_node_main)
    else:
        text = f'{query["message"]["text"]}\n{keyboard_text_node1X[query.data]}'
        keyboard = tgm.make_inline_keyboard(keyboard_text_node1XX)
    return text, keyboard    

def keyboard_text_node1XX_handler(query):
    if query.data == "edge1X4_back":
        text = query["message"]["text"]
        text = text[:text.rfind('\n')]
        keyboard = tgm.make_inline_keyboard(keyboard_text_node1X)
    else:
        text = f'{query["message"]["text"]}\n{keyboard_text_node1XX[query.data]}'
        keyboard = tgm.make_inline_keyboard(keyboard_text_node1XXX)
    return text, keyboard 

def keyboard_text_node1XXX_handler(query):
    if query.data == "edge1XX5_back":
        text = query["message"]["text"]
        text = text[:text.rfind('\n')]
        keyboard = tgm.make_inline_keyboard(keyboard_text_node1XX)
    else:
        text = f'{query["message"]["text"]}\n{keyboard_text_node1XXX[query.data]}'
        keyboard = tgm.make_inline_keyboard(keyboard_text_node1XXXX)
    return text, keyboard 

def keyboard_text_node1XXXX_handler(query):
    keyboard = None
    if query.data == "edge1XXX3_back":
        text = query["message"]["text"]
        text = text[:text.rfind('\n')]
        keyboard = tgm.make_inline_keyboard(keyboard_text_node1XXX)
    else:    
        text = f'{query["message"]["text"]}\n{keyboard_text_node1XXXX[query.data]}'
        if query.data == "edge1XXX1_done":
            print("[OK] Approved. Sending bird to gis.....")
            send_to_gis(query, 'bird')
            text = text + thanks_message
            global forward_list
            forward_list.append(query["message"]["reply_to_message"]["text"])
    return text, keyboard 

def keyboard_text_node2X_handler(query):
    if query.data == "edge24_back":
        text = query["message"]["text"]
        text = text[:text.rfind('\n')]
        text = text[:text.rfind('\n')] # Remove to lines (----) also.
        keyboard = tgm.make_inline_keyboard(keyboard_text_node_main)
    else:
        text = f'{query["message"]["text"]}\n{keyboard_text_node2X[query.data]}'
        keyboard = tgm.make_inline_keyboard(keyboard_text_node2XX)
    return text, keyboard 

def keyboard_text_node2XX_handler(query):
    keyboard = None
    if query.data == "edge2X3_back":
        text = query["message"]["text"]
        text = text[:text.rfind('\n')]
        keyboard = tgm.make_inline_keyboard(keyboard_text_node2X)
    else:
        text = f'{query["message"]["text"]}\n{keyboard_text_node2XX[query.data]}'
        if query.data == "edge2X1_done":
            print("[OK] Approved. Sending bird (pick) to gis.....")
            send_to_gis(query, 'bird')
            text = text + thanks_message
            global forward_list
            forward_list.append(query["message"]["reply_to_message"]["text"])

    return text, keyboard 

def keyboard_text_node3X_handler(query):
    if query.data == "edge35_back":
        text = query["message"]["text"]
        text = text[:text.rfind('\n')]
        text = text[:text.rfind('\n')] # Remove to lines (----) also.
        keyboard = tgm.make_inline_keyboard(keyboard_text_node_main)
    else:
        text = f'{query["message"]["text"]}\n{keyboard_text_node3X[query.data]}'
        keyboard = tgm.make_inline_keyboard(keyboard_text_node3XX)
    return text, keyboard 

def keyboard_text_node3XX_handler(query):
    keyboard = None
    if query.data == "edge3X3_back":
        text = query["message"]["text"]
        text = text[:text.rfind('\n')]
        keyboard = tgm.make_inline_keyboard(keyboard_text_node3X)
    else:    
        text = f'{query["message"]["text"]}\n{keyboard_text_node3XX[query.data]}'
        if query.data == "edge3X1_done":
            print("[OK] Approved. Sending oil to gis.....")
            send_to_gis(query, 'oil')
            text = text + thanks_message
    return text, keyboard 

def keyboard_text_node4X_handler(query):
    if query.data == "edge44_back":
        text = query["message"]["text"]
        text = text[:text.rfind('\n')]
        text = text[:text.rfind('\n')] # Remove to lines (----) also.
        keyboard = tgm.make_inline_keyboard(keyboard_text_node_main)
    else:    
        text = f'{query["message"]["text"]}\n{keyboard_text_node4X[query.data]}'
        keyboard = tgm.make_inline_keyboard(keyboard_text_node4XX)
    return text, keyboard 

def keyboard_text_node4XX_handler(query):
    keyboard = None
    if query.data == "edge4X3_back":
        text = query["message"]["text"]
        text = text[:text.rfind('\n')]
        keyboard = tgm.make_inline_keyboard(keyboard_text_node4X)
    else:       
        text = f'{query["message"]["text"]}\n{keyboard_text_node4XX[query.data]}'
        if query.data == "edge4X1_done":
            text = text + thanks_message
            print("[OK] Approved. Sending :-( animal point to gis.....")
            send_to_gis(query, 'dead')

    return text, keyboard 

edges = {
    "edge1_bird":keyboard_text_node1_handler,
    "edge2_bird_catch":keyboard_text_node1_handler,
    "edge3_oil":keyboard_text_node1_handler,
    "edge4_dead_animal":keyboard_text_node1_handler,
    "edge5_cancel":keyboard_text_node1_handler,

    "edge11_bird_one":keyboard_text_node1X_handler,
    "edge12_bird_three":keyboard_text_node1X_handler,
    "edge13_bird_many":keyboard_text_node1X_handler,
    "edge14_back":keyboard_text_node1X_handler,

    "edge1X1_bird_far_in_sea":keyboard_text_node1XX_handler,
    "edge1X2_bird_three":keyboard_text_node1XX_handler,
    "edge1X3_bird_many":keyboard_text_node1XX_handler,
    "edge1X4_back":keyboard_text_node1XX_handler,

    "edge1XX1_bird_Active":keyboard_text_node1XXX_handler,
    "edge1XX2_bird_weak":keyboard_text_node1XXX_handler,
    "edge1XX3_bird_weak":keyboard_text_node1XXX_handler,
    "edge1XX4_bird_urgent":keyboard_text_node1XXX_handler,
    "edge1XX5_back":keyboard_text_node1XXX_handler,

    "edge1XXX1_done":keyboard_text_node1XXXX_handler,
    "edge1XXX2_cancel":keyboard_text_node1XXXX_handler,
    "edge1XXX3_back":keyboard_text_node1XXXX_handler,

    "edge21_bird_one":keyboard_text_node2X_handler,
    "edge22_bird_three":keyboard_text_node2X_handler,
    "edge23_bird_many":keyboard_text_node2X_handler,
    "edge24_back":keyboard_text_node2X_handler,

    "edge2X1_done":keyboard_text_node2XX_handler,
    "edge2X2_cancel":keyboard_text_node2XX_handler,
    "edge2X3_back":keyboard_text_node2XX_handler,

    "edge31_bags50":keyboard_text_node3X_handler,
    "edge32_bags100":keyboard_text_node3X_handler,
    "edge33_bags200":keyboard_text_node3X_handler,
    "edge34_oil":keyboard_text_node3X_handler,
    "edge35_back":keyboard_text_node3X_handler,

    "edge3X1_done" : keyboard_text_node3XX_handler,
    "edge3X2_cancel" : keyboard_text_node3XX_handler,
    "edge3X3_back" : keyboard_text_node3XX_handler,

    "edge41_dolphin":keyboard_text_node4X_handler,
    "edge42_bird":keyboard_text_node4X_handler,
    "edge43_other":keyboard_text_node4X_handler,
    "edge44_back":keyboard_text_node4X_handler,

    "edge4X1_done":keyboard_text_node4XX_handler,
    "edge4X2_cancel":keyboard_text_node4XX_handler,
    "edge4X3_back":keyboard_text_node4XX_handler

}

async def cb_reaction_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    chat_id = query["message"]["chat"]["id"]
    if int(chat_id) not in target_group_id:
        #print(json.dumps(update.to_dict(), indent = 4))
        print("[!!] Wrong chat id, why so??")
        return
    #print(json.dumps(update.to_dict(), indent = 4))
    coordinate_sender = query["message"]["text"].split(" ")[0][1:-1]
    replier = query["from"]["username"]
    print(f"Coordinate sender {coordinate_sender}. Replier {replier}. Query: {query.data}")
#    if coordinate_sender != replier:
#        return None
    if query.data in edges.keys():
        text, keyboard = edges[query.data](query)
        if keyboard:
            await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text(text=text)
    else:
        print(f"[!!] Got unexpected argument: {query.data}")
    return

async def cb_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("message")
    if update["message"] is None:
        print(json.dumps(update.to_dict(), indent = 4))
        return None
    text = json.dumps(update.to_dict())
    all_lat, all_lon = get_coord_from_text(text)
    message_text = update["message"]["text"]
    if message_text is None: 
        message_text = ""
    if len(all_lat) and len(all_lon) and len(message_text) < 500:# and "message" in update:
        coordinates = f"{all_lat[0]}, {all_lon[0]}"
        print(coordinates)
        text = f"""\
@{update["message"]["from"]["username"]}. Спасибо за кординаты ({coordinates}).
Отправляем в штаб и на карту, заполните пожалуста подробности:
"""
        keyboard = tgm.make_inline_keyboard(keyboard_text_node_main)
        await update.message.reply_text(f'{text}', reply_markup=InlineKeyboardMarkup(keyboard))
    return None

async def main() -> None:
    """Run the bot."""
    global application
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    #application.add_handler(MessageHandler(filters.LOCATION, cb_user_location))
    application.add_handler(MessageHandler(filters.ALL, cb_message))
    #application.add_handler(CommandHandler("r", cb_reaction_button))
    application.add_handler(CallbackQueryHandler(cb_reaction_button))
    await application.initialize()
    await application.start()
    await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    print("[OK] Bot enabled")
    while True:
        await asyncio.sleep(2)
        global forward_list
        #for m in forward_list:
        #    await application.bot.send_message(forward_group, m)
        forward_list = []
        #nextgis.get_history()
    await application.updater.stop()
    print("[OK] Bot disabled")

    await application.shutdown()

if __name__ == "__main__":
    asyncio.run(main())