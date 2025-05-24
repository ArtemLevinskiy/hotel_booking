from datetime import datetime, timedelta, date
class Hotel:
    def __init__(self, name: str, address: str, rating: float, num_room: int, phone: str, email: str):
        self._name = name
        self._address = address
        self._rating = rating
        self._num_room = num_room
        self._phone = phone
        self._email = email
        self._room_available = num_room

        if type(rating) != float or type(num_room) != int:
            raise TypeError("Дані повинні бути числовим значенням")
        if rating < 1 or num_room < 1:
            raise ValueError("Значення не можуть бути від'ємними")
        if type(name) != str or type(address) != str or type(phone) != str or type(email) != str:
            raise TypeError("Дані повинні бути строковим значенням")

    def __str__(self):
        return f"{self._name.title()}, {self._address}, рейтинг: {self._rating}⭐️"

    def is_available(self):
        return self._room_available > 0

    def book_room(self, count):
        if self._room_available >= count:
            self._room_available -= count
            return True
        return False


class Client:
    def __init__(self, first_name, last_name, phone_number, email):
        self._first_name = first_name
        self._last_name = last_name
        self._phone_number = phone_number
        self._email = email

        if type(first_name) != str or type(last_name) != str or type(phone_number) != str or type(email) != str:
            raise TypeError("Дані повинні бути строковим значенням")
        if phone_number.startswith('+380'):
            if len(phone_number) != 13 or not phone_number[1:].isdigit():
                raise ValueError("Номер введено некоректно")
        elif phone_number.startswith('0'):
            if len(phone_number) != 10 or not phone_number.isdigit():
                raise ValueError("Номер введено некоректно")
        else:
            raise ValueError("Номер введено некоректно")
        if "@" not in email:
            raise ValueError("Адрес електроної пошти введено некоректно")
        if "." not in email:
            raise ValueError("Адрес електроної пошти введено некоректно")


    def __str__(self):
        return f"{self._first_name.title()} {self._last_name.title()}\nТелефон: {self._phone_number}\nEmail: {self._email}"


class Room:
    def __init__(self,title, description, price, photo):
        self._title = title
        self._description = description
        self._price = price
        self._photo = photo


class Booking:
    def __init__(self, client: Client, hotel: Hotel, room: Room, nights: int, rooms_count: int = 1):
        self._client = client
        self._hotel = hotel
        self._room = room
        self._nights = nights
        self._rooms_count = rooms_count
        self._total_price = room._price * nights * rooms_count

        self._checkin_date = datetime.strptime(checkin_date, "%d.%m.%Y").date()
        self._checkout_date = self._checkin_date + timedelta(days=nights)


        if nights < 1:
            raise ValueError("Кількість ночей має бути більше 0")

        if not hotel.is_available():
            raise ValueError("Немає доступних номерів у готелі")

        if rooms_count > hotel._room_available:
            raise ValueError("Недостатньо доступних номерів для бронювання")

        if not hotel.book_room(rooms_count):
            raise ValueError("Не вдалося забронювати потрібну кількість номерів")

    def __str__(self):
        return (f"Бронювання для {self._client._first_name.title()} {self._client._last_name.title()}:\n"
                f"Готель: {self._hotel._name.title()}\n"
                f"Номер: {self._room._title}\n"
                f"Кількість ночей: {self._nights}\n"
                f"Кількість номерів: {self._rooms_count}\n"
                f"Дата заїзду: {self._checkin_date.strftime('%d.%m.%Y')}\n"
                f"Дата виїзду: {self._checkout_date.strftime('%d.%m.%Y')}\n"
                f"Загальна ціна: {self._total_price} грн\n")

class Notification:
    def __init__(self, booking: Booking):
        self._booking = booking

    def send_reminder(self):
        today = date.today()
        checkin = self._booking._checkin_date
        days_left = (checkin - today).days

        if days_left > 1:
            message = (
                f"🔔 Нагадування: до вашого заїзду в готель залишилось {days_left} днів.\n"
                f"Готель: {self._booking._hotel._name.title()}\n"
                f"Дата заїзду: {checkin.strftime('%d.%m.%Y')}\n"
                f"Ми чекаємо на вас!"
            )
        elif days_left == 1:
            message = (
                f"🔔 Нагадування: ваш заїзд в готель вже завтра!\n"
                f"Готель: {self._booking._hotel._name.title()}\n"
                f"Номер: {self._booking._room._title}\n"
                f"Дата заїзду: {checkin.strftime('%d.%m.%Y')}"
            )
        elif days_left == 0:
            message = (
                f"🏨 Сьогодні ваш заїзд у готель \"{self._booking._hotel._name.title()}\"!\n"
                f"Будь ласка, не забудьте документи для поселення.\n"
                f"Чекаємо вас з нетерпінням! 🛎"
            )
        elif days_left < 0:
            message = f"❗️ Дата заїзду ({checkin.strftime('%d.%m.%Y')}) вже минула."

        print(message)
        return message


h1 = Hotel("КиЇвська ХАтка", "вул. Хрещатик, 1, Київ", 4.0, 3, "+380111111111", "info@kyivhatka.ua")

c1 = Client("aRtem", "LEVinskiy", "+380978517087", "levinskiy2306@gmail.com")
c2 = Client("MalANa", "MELL", "+380978517087", "levinskiy2306@gmail.com")
c3 = Client("AliNA", "LEVinskaya", "+380978517087", "levinskiy2306@gmail.com")

rooms = [
    Room("№1 Двохмісний номер", "Комфортний номер з двоспальним ліжком.", 1000, "img/room_image.jpg"),
    Room("№1 Двохмісний номер", "Комфортний номер з двоспальним ліжком.", 1300, "img/image.jpg"),
    Room("№3 Одномісний номер", "Номер для одного гостя.", 2000, "img/photo2.jpg")
]

b1 = Booking(c1, h1, rooms[0], 3, 1)
b2 = Booking(c2, h1, rooms[0], 3, 1)
b3 = Booking(c3, h1, rooms[2], 3, 1)
print(b1)
print(b2)
print(b3)

b1 = Booking(c1, h1, rooms[0], 3, "26.05.2025", 1)
n1 = Notification(b1)
n1.send_reminder()
