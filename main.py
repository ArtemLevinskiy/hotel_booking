import re
from datetime import datetime, timedelta
import calendar
import telebot
from telebot import types
bot = telebot.TeleBot('7645087026:AAG202f9vc5_tQHJvwW1CRmOQ5E0Pc-Q8H8')

class Hotel:
    def __init__(self, name: str, address: str, rating: float, num_room: int, price: int, phone: str, email: str):
        self._name = name
        self._address = address
        self._rating = rating
        self._num_room = num_room
        self._price = price
        self._phone = phone
        self._email = email
        self._room_available = num_room

        if type(rating) != float or type(num_room) != int or type(price) != int:
            raise TypeError("Дані повинні бути числовим значенням")
        if rating < 1 or num_room < 1 or price < 1:
            raise ValueError("Значення не можуть бути від'ємними")
        if type(name) != str or type(address) != str or type(phone) != str or type(email) != str:
            raise TypeError("Дані повинні бути строковим значенням")

    def get_info(self):
        return f"{self._name}, {self._address}, рейтинг: {self._rating}⭐️, ціна за ніч: {self._price}грн"
    def is_available(self):
        return self._room_available > 0

    def book_room(self, count):
        if self._room_available >= count:
            self._room_available -= count
            return True
        return False

    def calculate_price(self, nights):
        return self._price * nights


class Client:
    def __init__(self, first_name, last_name, phone_number, email):
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.email = email

    def __str__(self):
        return f"{self.first_name} {self.last_name}\nТелефон: {self.phone_number}\nEmail: {self.email}"


class Room:
    def __init__(self, photo, title, description):
        self.photo = photo
        self.title = title
        self.description = description


class Booking:
    def __init__(self, bot, hotel, rooms):
        self._bot = bot
        self._hotel = hotel
        self._rooms = rooms
        self._selected_room = {}
        self._checkin_date = {}

    def send_room_list(self, chat_id):
        for room in self._rooms:
            with open(room.photo, 'rb') as photo:
                caption = f"<b><u>{room.title}</u></b>\n{room.description}"
                self._bot.send_photo(chat_id, photo, caption=caption, parse_mode='html')
        self.ask_for_booking(chat_id)

    def ask_for_booking(self, chat_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Так. Забронювати номер", callback_data="book_now"))
        self._bot.send_message(chat_id, 'Хочете забронювати номер?', reply_markup=markup)

    def choose_room(self, chat_id):
        markup = types.InlineKeyboardMarkup()
        for i in range(0, len(self._rooms), 2):
            row = [types.InlineKeyboardButton(room.title, callback_data=f"room_{room.title}") for room in self._rooms[i:i+2]]
            markup.row(*row)
        self._bot.send_message(chat_id, 'Виберіть номер:', reply_markup=markup)

    def confirm_room(self, user_id, chat_id, room_title):
        self._selected_room[user_id] = room_title
        self._bot.send_message(chat_id, f"Ви обрали {room_title}.")
        self.send_calendar(chat_id, "checkin")

    def send_calendar(self, chat_id, prefix):
        now = datetime.now()
        min_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

        if prefix == "checkout":
            checkin_str = self._checkin_date.get(chat_id)
            if not checkin_str:
                self._bot.send_message(chat_id, "Спочатку оберіть дату заїзду.")
                return
            min_date = datetime.strptime(checkin_str, "%d.%m.%Y") + timedelta(days=1)

        markup = self.create_calendar(now.year, now.month, prefix, min_date)
        self._bot.send_message(chat_id, f"Виберіть дату {'заїзду' if prefix == 'checkin' else 'виїзду'}:", reply_markup=markup)


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
                self._bot.send_message(call.message.chat.id, "Бронювання завершено!")
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


rooms = [
    Room("img/room_image.jpg", "№1 Двохмісний номер", "Комфортний номер з двоспальним ліжком."),
    Room("img/image.jpg", "№2 Двохмісниий номер", "Номер для двох друзів."),
    Room("img/photo2.jpg", "№3 Одномісний номер", "Номер для одного гостя.")
]

hotel = Hotel("Київська Хатка", "вул. Хрещатик, 1, Київ", 4.0, 3, 1000, "+380111111111", "info@kyivhatka.ua")
manager = Booking(bot, hotel, rooms)

user_data = {}
user_step = {}


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'Вас вітає готель <b>"{hotel._name}"</b>', parse_mode='html')
    info = f"Адреса: {hotel._address}\nРейтинг: {hotel._rating}⭐️\nКонтакти:\n{hotel._phone}\n{hotel._email}"
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
        user_data[user_id]['first_name'] = message.text.title()
        user_step[user_id] = 'last_name'
        bot.send_message(message.chat.id, "Введіть ваше прізвище:")
    elif step == 'last_name':
        if not message.text.isalpha():
            bot.send_message(message.chat.id, "Прізвище має містити лише літери. Спробуйте ще раз:")
            return
        user_data[user_id]['last_name'] = message.text.title()
        user_step[user_id] = 'phone'
        bot.send_message(message.chat.id, "Введіть ваш номер телефону:")
    elif step == 'phone':
        if not re.fullmatch(r"\+?\d{10,15}", message.text):
            bot.send_message(message.chat.id,
                             "Некоректний номер телефону. Приклад: +380501234567. Спробуйте ще раз:")
            return
        user_data[user_id]['phone_number'] = message.text
        user_step[user_id] = 'email'
        bot.send_message(message.chat.id, "Введіть ваш email:")
    elif step == 'email':
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", message.text):
            bot.send_message(message.chat.id, "Некоректний email. Спробуйте ще раз:")
            return
        user_data[user_id]['email'] = message.text

        data = user_data[user_id]
        client = Client(data['first_name'], data['last_name'], data['phone_number'], data['email'])

        del user_step[user_id]
        del user_data[user_id]
        bot.send_message(message.chat.id, f"Дякуємо! Ваші дані збережено:\n{client}")


bot.polling(none_stop=True)
