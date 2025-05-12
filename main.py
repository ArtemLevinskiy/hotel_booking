from datetime import datetime
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

    def book_room(self, n):
        if self._room_available >= n:
            self._room_available -= n
            return True
        else:
            return f"Вільних номерів немає"

    def calculate_price(self, nights):
        return self._price * nights


class BookingManager:
    def __init__(self, bot, hotel: Hotel, room_data: list):
        self.bot = bot
        self.hotel = hotel
        self.room_data = room_data
        self.selected_room = {}

    def send_room_list(self, message):
        for room in self.room_data:
            with open(room["photo_path"], 'rb') as photo:
                caption = f"<b><u>{room['title']}</u></b>\n{room['description']}"
                self.bot.send_photo(message.chat.id, photo, caption=caption, parse_mode='html')
        self.ask_for_booking(message)

    def ask_for_booking(self, message):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Так. Забронювати номер", callback_data="book_now"))
        self.bot.send_message(message.chat.id, 'Хочете забронювати номер?', reply_markup=markup)

    def choose_room(self, call):
        markup = types.InlineKeyboardMarkup()
        buttons = [types.InlineKeyboardButton(room["title"], callback_data=f"room_{room['title']}") for room in self.room_data]
        for i in range(0, len(buttons), 2):
            markup.row(*buttons[i:i + 2])
        self.bot.send_message(call.message.chat.id, 'Виберіть номер.', reply_markup=markup)

    def confirm_room(self, call, room_title):
        self.selected_room[call.from_user.id] = room_title
        self.bot.send_message(call.message.chat.id, f"Чудовий вибір!\nВи обрали {room_title}.")
        self.send_calendar(call.message, "checkin")

    def send_calendar(self, message, prefix):
        now = datetime.now()
        markup = create_calendar(now.year, now.month, prefix)
        self.bot.send_message(message.chat.id, f"Виберіть дату {'заїзду' if prefix == 'checkin' else 'виїзду'}:", reply_markup=markup)

    def handle_calendar(self, call, prefix):
        parts = call.data.split("_")
        action = parts[1]

        if action in ("prev", "next"):
            year, month = int(parts[2]), int(parts[3])
            if action == "prev":
                month -= 1
                if month == 0:
                    month = 12
                    year -= 1
            elif action == "next":
                month += 1
                if month == 13:
                    month = 1
                    year += 1
            markup = create_calendar(year, month, prefix)
            self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)

        elif action == "day":
            day, month, year = int(parts[2]), int(parts[3]), int(parts[4])
            date_str = f"{day:02d}.{month:02d}.{year}"
            self.bot.edit_message_text(f"Дата {'заїзду' if prefix == 'checkin' else 'виїзду'}: {date_str}",
                                       call.message.chat.id, call.message.message_id)
            if prefix == "checkin":
                self.send_calendar(call.message, "checkout")
            else:
                self.bot.send_message(call.message.chat.id, "✅ Бронювання завершено!")

def create_calendar(year: int, month: int, prefix: str) -> types.InlineKeyboardMarkup:
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
            row.append(types.InlineKeyboardButton(" " if day == 0 else str(day),
                                                  callback_data="ignore" if day == 0 else f"{prefix}_day_{day}_{month}_{year}"))
        markup.row(*row)
    return markup

h1 = Hotel("Київська Хатка", "вул. Хрещатик, 1, Київ", 4.0,
           3, 1000, "+380111111111", "info@kyivhatka.ua")

room_data = [
    {
        "photo_path": "img/room_image.jpg",
        "title": "№1 Двохмісний номер",
        "description": "Комфортний номер з одним двоспальним ліжком. У номері є все необхідне: телевізор, санвузол, безкоштовний інтернет. Чудовий вибір для пари."
    },
    {
        "photo_path": "img/image.jpg",
        "title": "№2 Двохмісниий номер",
        "description": "Невеличкий номер для двох осіб. Підійде для двох друзів. Є кондиціонер, ванна кімната, безкоштовний Wi-Fi."
    },
    {
        "photo_path": "img/photo2.jpg",
        "title": "№3 Одномісний номер",
        "description": "Затишний номер для одного гостя з односпальним ліжком, базовими зручностями та Wi-Fi. Ідеально підходить для короткотривалого відпочинку чи ділової поїздки."
    }
]

booking_manager = BookingManager(bot, h1, room_data)


bot.polling(none_stop=True)
