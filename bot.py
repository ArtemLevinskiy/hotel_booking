import calendar
from datetime import datetime, timedelta, date
import telebot
from telebot import types
from booking import Hotel, Room, Client, Booking, h1, rooms

bot = telebot.TeleBot('7645087026:AAG202f9vc5_tQHJvwW1CRmOQ5E0Pc-Q8H8')

user_step = {}
user_data = {}

class BotManager:
    def __init__(self, bot, hotel, rooms):
        self._bot = bot
        self._hotel = hotel
        self._rooms = rooms
        self._selected_room = {}
        self._checkin_date = {}
        self._checkout_date = {}

    def send_room_list(self, chat_id):
        for room in self._rooms:
            with open(room._photo, 'rb') as photo:
                caption = f"<b><u>{room._title}</u></b>\n{room._description}\nЦіна: {room._price} грн/доба"
                self._bot.send_photo(chat_id, photo, caption=caption, parse_mode='html')
        self.ask_for_booking(chat_id)

    def ask_for_booking(self, chat_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Так. Забронювати номер", callback_data="book_now"))
        self._bot.send_message(chat_id, 'Хочете забронювати номер?', reply_markup=markup)

    def choose_room(self, chat_id):
        markup = types.InlineKeyboardMarkup()
        for i in range(0, len(self._rooms), 2):
            row = [types.InlineKeyboardButton(room._title, callback_data=f"room_{room._title}") for room in
                   self._rooms[i:i + 2]]
            markup.row(*row)
        self._bot.send_message(chat_id, 'Виберіть номер:', reply_markup=markup)

    def confirm_room(self, user_id, chat_id, room_title):
        self._selected_room[user_id] = room_title
        self._bot.send_message(chat_id, f"Ви обрали {room_title}.")
        self.send_calendar(chat_id, "checkin")

    def send_calendar(self, chat_id, prefix):
        now = datetime.now()
        min_date = now.replace(hour=9, minute=0, second=0, microsecond=0)

        if prefix == "checkout":
            checkin_str = self._checkin_date.get(chat_id)
            if not checkin_str:
                self._bot.send_message(chat_id, "Спочатку оберіть дату заїзду.")
                return
            min_date = datetime.strptime(checkin_str, "%d.%m.%Y") + timedelta(days=1)

        markup = self.create_calendar(now.year, now.month, prefix, min_date)
        self._bot.send_message(chat_id, f"Виберіть дату {'заїзду' if prefix == 'checkin' else 'виїзду'}:",
                               reply_markup=markup)

    def handle_calendar(self, call, prefix):
        parts = call.data.split("_")
        action = parts[1]

        if action in ("prev", "next"):
            year, month = int(parts[2]), int(parts[3])
            month += 1 if action == "next" else -1
            if month == 0:
                month = 12
                year -= 1
            elif month == 13:
                month = 1
                year += 1
            markup = self.create_calendar(year, month, prefix)
            self._bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)

        elif action == "day":
            day, month, year = map(int, parts[2:5])
            date_str = f"{day:02d}.{month:02d}.{year}"
            self._bot.edit_message_text(f"Дата {'заїзду' if prefix == 'checkin' else 'виїзду'}: {date_str}",
                                        call.message.chat.id, call.message.message_id)
            if prefix == "checkin":
                self._checkin_date[call.from_user.id] = date_str
                self.send_calendar(call.message.chat.id, "checkout")
            else:
                self._checkout_date[call.from_user.id] = date_str
                book_client(call.message.chat.id, call.from_user.id)

    def create_calendar(self, year, month, prefix, min_date=None):
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("⬅️", callback_data=f"{prefix}_prev_{year}_{month}"),
            types.InlineKeyboardButton(f"{calendar.month_name[month]} {year}", callback_data="ignore"),
            types.InlineKeyboardButton("➡️", callback_data=f"{prefix}_next_{year}_{month}")
        )
        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]
        markup.row(*[types.InlineKeyboardButton(day, callback_data="ignore") for day in days])

        for week in calendar.monthcalendar(year, month):
            row = []
            for day in week:
                if day == 0 or (min_date and datetime(year, month, day) < min_date):
                    row.append(types.InlineKeyboardButton(" ", callback_data="ignore"))
                else:
                    row.append(types.InlineKeyboardButton(str(day), callback_data=f"{prefix}_day_{day}_{month}_{year}"))
            markup.row(*row)
        return markup

manager = BotManager(bot, h1, rooms)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'Вас вітає готель <b>"{h1._name.title()}"</b>', parse_mode='html')
    info = f"Адреса: {h1._address}\nРейтинг: {h1._rating}⭐️\nКонтакти:\n{h1._phone}\n{h1._email}"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Огляд номерів", callback_data="view_rooms"))
    bot.send_message(message.chat.id, info, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "view_rooms")
def view_rooms(call):
    manager.send_room_list(call.message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "book_now")
def book_now(call):
    manager.choose_room(call.message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("room_"))
def room_selected(call):
    room_title = call.data.replace("room_", "")
    manager.confirm_room(call.from_user.id, call.message.chat.id, room_title)

@bot.callback_query_handler(func=lambda call: call.data.startswith("checkin_"))
def calendar_checkin(call):
    manager.handle_calendar(call, "checkin")

@bot.callback_query_handler(func=lambda call: call.data.startswith("checkout_"))
def calendar_checkout(call):
    manager.handle_calendar(call, "checkout")

def book_client(chat_id, user_id):
    user_step[user_id] = 'first_name'
    bot.send_message(chat_id, "Введіть ваше ім'я:")

@bot.message_handler(func=lambda msg: msg.from_user.id in user_step)
def handle_steps(message):
    user_id = message.from_user.id
    step = user_step[user_id]
    if user_id not in user_data:
        user_data[user_id] = {}

    if step == 'first_name':
        if not message.text.isalpha():
            bot.send_message(message.chat.id, "Ім'я має містити лише літери. Спробуйте ще раз:")
            return
        user_data[user_id]['first_name'] = message.text
        user_step[user_id] = 'last_name'
        bot.send_message(message.chat.id, "Введіть ваше прізвище:")
    elif step == 'last_name':
        if not message.text.isalpha():
            bot.send_message(message.chat.id, "Прізвище має містити лише літери. Спробуйте ще раз:")
            return
        user_data[user_id]['last_name'] = message.text
        user_step[user_id] = 'phone'
        bot.send_message(message.chat.id, "Введіть номер телефону:")
    elif step == 'phone':
        phone_number = message.text
        if phone_number.startswith('+380'):
            if len(phone_number) != 13 or not phone_number[1:].isdigit():
                bot.send_message(message.chat.id, "Номер введено некоректно. Спробуйте ще раз:")
                return
        elif phone_number.startswith('0'):
            if len(phone_number) != 10 or not phone_number.isdigit():
                bot.send_message(message.chat.id, "Номер введено некоректно. Спробуйте ще раз:")
                return
        else:
            bot.send_message(message.chat.id, "Номер введено некоректно. Спробуйте ще раз:")
            return
        user_data[user_id]['phone'] = phone_number
        user_step[user_id] = 'email'
        bot.send_message(message.chat.id, "Введіть email:")


    elif step == 'email':
        email = message.text
        if "@" not in email or "." not in email:
            bot.send_message(message.chat.id, "Адрес електронної пошти введено некоректно. Спробуйте ще раз:")
            return
        user_data[user_id]['email'] = email


        data = user_data[user_id]
        client = Client(data['first_name'], data['last_name'], data['phone'], data['email'])
        checkin = manager._checkin_date[user_id]
        checkout = manager._checkout_date[user_id]
        nights = (datetime.strptime(checkout, "%d.%m.%Y") - datetime.strptime(checkin, "%d.%m.%Y")).days
        selected_room_title = manager._selected_room[user_id]
        selected_room = next(room for room in rooms if room._title == selected_room_title)
        booking = Booking(client, h1, selected_room, nights, checkin)

        bot.send_message(message.chat.id, f"Успішне бронювання:\n{booking}")
        del user_step[user_id]
        del user_data[user_id]

bot.polling(none_stop=True)