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

    def book_room(self, n):
        if self._room_available >= n:
            self._room_available -= n
            return True
        else:
            return f"Вільних номерів немає"

    def calculate_price(self, nights):
        return self._price * nights

user_data = {}
user_step = {}
class Client:
    def __init__(self, first_name, last_name, phone_number, email):
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.email = email

        @bot.message_handler(commands=['book'])
        def start_booking(message):
            user_id = message.from_user.id
            user_step[user_id] = 'first_name'
            bot.send_message(message.chat.id, "Введіть ваше ім'я:")

        @bot.message_handler(func=lambda message: message.from_user.id in user_step)
        def handle_client_info(message):
            user_id = message.from_user.id
            step = user_step[user_id]

            if user_id not in user_data:
                user_data[user_id] = {}

            if step == 'first_name':
                user_data[user_id]['first_name'] = message.text
                user_step[user_id] = 'last_name'
                bot.send_message(message.chat.id, "Введіть ваше прізвище:")

            elif step == 'last_name':
                user_data[user_id]['last_name'] = message.text
                user_step[user_id] = 'phone'
                bot.send_message(message.chat.id, "Введіть ваш номер телефону:")

            elif step == 'phone':
                user_data[user_id]['phone_number'] = message.text
                user_step[user_id] = 'email'
                bot.send_message(message.chat.id, "Введіть ваш email:")

            elif step == 'email':
                user_data[user_id]['email'] = message.text

                data = user_data[user_id]
                client = Client(data['first_name'], data['last_name'], data['phone_number'], data['email'])

                del user_step[user_id]
                del user_data[user_id]
                bot.send_message(message.chat.id, f"Дякуємо! Ваші дані збережено:\n{client}")

    def __str__(self):
        return f"{self.first_name} {self.last_name}\nТелефон: {self.phone_number}\nEmail: {self.email}"


class BookingManager:
    def __init__(self, bot, hotel: Hotel, room_data: list):
        self._bot = bot
        self._hotel = hotel
        self._room_data = room_data
        self._selected_room = {}
        self._checkin_date = {}

    def send_room_list(self, message):
        for room in self._room_data:
            with open(room["photo_path"], 'rb') as photo:
                caption = f"<b><u>{room['title']}</u></b>\n{room['description']}"
                self._bot.send_photo(message.chat.id, photo, caption=caption, parse_mode='html')
        self.ask_for_booking(message)

    def ask_for_booking(self, message):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Так. Забронювати номер", callback_data="book_now"))
        self._bot.send_message(message.chat.id, 'Хочете забронювати номер?', reply_markup=markup)

    def choose_room(self, call):
        markup = types.InlineKeyboardMarkup()
        buttons = [types.InlineKeyboardButton(room["title"], callback_data=f"room_{room['title']}") for room in self._room_data]
        for i in range(0, len(buttons), 2):
            markup.row(*buttons[i:i + 2])
        self._bot.send_message(call.message.chat.id, 'Виберіть номер.', reply_markup=markup)

    def confirm_room(self, call, room_title):
        self._selected_room[call.from_user.id] = room_title
        self._bot.send_message(call.message.chat.id, f"Чудовий вибір!\nВи обрали {room_title}.")
        self.send_calendar(call.message, "checkin")

    def send_calendar(self, message, prefix):
        now = datetime.now()
        user_id = message.chat.id

        if prefix == "checkin":
            min_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            checkin_str = self._checkin_date.get(user_id)
            if not checkin_str:
                self._bot.send_message(message.chat.id, "Спочатку оберіть дату заїзду.")
                return
            checkin_date = datetime.strptime(checkin_str, "%d.%m.%Y")
            min_date = checkin_date + timedelta(days=1)

        markup = create_calendar(now.year, now.month, prefix, min_date)
        self._bot.send_message(message.chat.id, f"Виберіть дату {'заїзду' if prefix == 'checkin' else 'виїзду'}:",
                              reply_markup=markup)

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
            self._bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
        elif action == "day":
            day, month, year = int(parts[2]), int(parts[3]), int(parts[4])
            date_str = f"{day:02d}.{month:02d}.{year}"
            self._bot.edit_message_text(f"Дата {'заїзду' if prefix == 'checkin' else 'виїзду'}: {date_str}",
                                       call.message.chat.id, call.message.message_id)
            if prefix == "checkin":
                self._checkin_date[call.from_user.id] = date_str
                self.send_calendar(call.message, "checkout")
            else:
                self._bot.send_message(call.message.chat.id, "Бронювання завершено!")


room_data = []

class Room:
    def __init__(self, photo, title, description):
        self._photo = photo
        self._title = title
        self._description = description

        room_data.append({
            "photo_path": self._photo,
            "title": self._title,
            "description": self._description
        })

r1 = Room("img/room_image.jpg", "№1 Двохмісний номер", "Комфортний номер з одним двоспальним ліжком. У номері є все необхідне: телевізор, санвузол, безкоштовний інтернет. Чудовий вибір для пари.")
r2 = Room("img/image.jpg", "№2 Двохмісниий номер", "Невеличкий номер для двох осіб. Підійде для двох друзів. Є кондиціонер, ванна кімната, безкоштовний Wi-Fi.")
r3 = Room("img/photo2.jpg", "№3 Одномісний номер", "Затишний номер для одного гостя з односпальним ліжком, базовими зручностями та Wi-Fi. Ідеально підходить для короткотривалого відпочинку чи ділової поїздки.")

c1 = Client('Валерія', 'Шульга', '+380999999999', 'shelg@gmail.com')

h1 = Hotel("Київська Хатка", "вул. Хрещатик, 1, Київ", 4.0,
           3, 1000, "+380111111111", "info@kyivhatka.ua")
bm = BookingManager(bot, h1, room_data)


def create_calendar(year: int, month: int, prefix: str, min_date: datetime = None) -> types.InlineKeyboardMarkup:
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
            if day == 0:
                row.append(types.InlineKeyboardButton(" ", callback_data="ignore"))
                continue
            btn_date = datetime(year, month, day)
            if min_date and btn_date < min_date:
                row.append(types.InlineKeyboardButton(" ", callback_data="ignore"))
            else:
                row.append(types.InlineKeyboardButton(str(day), callback_data=f"{prefix}_day_{day}_{month}_{year}"))
        markup.row(*row)
    return markup



@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'Вас вітає готель <b>"{h1._name}"</b>\n', parse_mode='html')
    markup = types.InlineKeyboardMarkup()
    btn2 = types.InlineKeyboardButton("Огляд номерів", callback_data="Огляд номерів")
    markup.row(btn2)
    bot.send_message(message.chat.id, f'Адреса: {h1._address}\nРейтинг: {h1._rating}⭐️\nКонтакти: \n'
                                      f'{h1._phone}\n {h1._email}', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "Огляд номерів")
def handle_room_overview(call):
    bm.send_room_list(call.message)

@bot.callback_query_handler(func=lambda call: call.data == "book_now")
def handle_booking_now(call):
    bm.choose_room(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("room_"))
def handle_room_selection(call):
    room_title = call.data.replace("room_", "")
    bm.confirm_room(call, room_title)

@bot.callback_query_handler(func=lambda call: call.data.startswith("checkin_"))
def handle_checkin_calendar(call):
    bm.handle_calendar(call, "checkin")

@bot.callback_query_handler(func=lambda call: call.data.startswith("checkout_"))
def handle_checkout_calendar(call):
    bm.handle_calendar(call, "checkout")


bot.polling(none_stop=True)
