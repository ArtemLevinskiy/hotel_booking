from datetime import datetime, timedelta, date
class Hotel:
    """
    Description:
        Клас для представлення готелю
        (Hotel presentation class)
    """
    def __init__(self, name: str, address: str, rating: float, num_room: int, phone: str, email: str):
        """
        Description:
            Ініціалізація готелю з перевірками типів і значень
            (Hotel initialization with type and value checks)
        Args:
            name (str): Назва (Name)
            address (str): Адреса (Address)
            rating (float): Рейтинг (Ratint)
            num_room (int): Кількість кімнат (Number of rooms)
            phone (str): Номер телефону (Phone number)
            email (str): Електронна пошта (E-mail)
        Raise:
            ValueError: Якщо рейтинг, кількість кімнат, номер телефону і електронна пошта введено не правильно
                        (If the rating, number of rooms, phone number and email are entered incorrectly)
            TypeError: Якщо типи переданих даних некоректні
                        (If the types of data transmitted are incorrect)
        """
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
        if phone.startswith('+380'):
            if len(phone) != 13 or not phone[1:].isdigit():
                raise ValueError("Номер введено некоректно")
        elif phone.startswith('0'):
            if len(phone) != 10 or not phone.isdigit():
                raise ValueError("Номер введено некоректно")
        else:
            raise ValueError("Номер введено некоректно")
        if "@" not in email:
            raise ValueError("Адрес електронної пошти введено некоректно")
        if "." not in email:
            raise ValueError("Адрес електронної пошти введено некоректно")

    def __str__(self):
        """
        Description:
            Повертає рядковий опис готелю (Returns a string description of the hotel)
        Return:
            str: У форматі: Name, Address, рейтинг: rating (In the format: Name, Address, rating: rating)
        """
        return f"{self._name.title()}, {self._address.title()}, рейтинг: {self._rating}⭐️"

    def is_available(self):
        """
        Description:
            Перевіряє наявність вільних номерів у готелі (Checks availability of hotel rooms)
        Return:
            True, якщо є вільні номери.False, якщо немає (True if there are free numbers.False if there are not)
        """
        return self._room_available > 0

    def book_room(self, count):
        """
        Description:
            Бронює вказану кількість номерів, якщо вони доступні (Reserves the specified number of rooms, if available)

        Args:
            count (int): Кількість номерів для бронювання (Number of rooms to book)

        Return:
            bool: True, якщо бронювання успішне; False, якщо ні (True if the booking is successful; False if not)
        """
        if self._room_available >= count:
            self._room_available -= count
            return True
        return False


class Client:
    """
    Description:
        Клас для представлення клієнта (Class to represent the client)
    """
    def __init__(self, first_name : str, last_name : str, phone_number : str, email : str):
        """
        Description:
            Ініціалізує нового клієнта з перевірками (Initializes a new client with checks)
        Args:
            first_name (str): Ім'я (First name)
            last_name (str): Прізвище (Last name)
            phone_number (str): Номер телефону (Phone number)
            email (str): Електронна пошта (E-mail)
        Raise:
            ValueError: Якщо номер телефону або email мають неправильний формат
                        (If the phone number or email is in the wrong format)
            TypeError: Якщо типи значень некоректні (If the value types are incorrect)
        """
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
            raise ValueError("Адрес електронної пошти введено некоректно")
        if "." not in email:
            raise ValueError("Адрес електронної пошти введено некоректно")


    def __str__(self):
        """
        Description:
            Повертає інформацію про клієнта (Returns client information)
        Return:
            str: У форматі: First_name, Last_name
                            Телефон: phone_number
                            Email: email
        """
        return f"{self._first_name.title()} {self._last_name.title()}\nТелефон: {self._phone_number}\nEmail: {self._email}"


class Room:
    """
    Description:
        Клас для представлення номера в готелі (Class for representing a hotel room)
    """
    def __init__(self, title : str, description : str, price : int, photo : str = ""):
        """
        Description:
            Ініціалізує номер готелю з перевірками (Initializes the hotel room with checks)
        Args:
            title (str): Короткий опис (Наприклад: кількість ліжок) (Brief description (e.g., bed count))
            description (str): Повний опис (Full description)
            price (int): Вартість  номеру за добу (Room rate per day)
            photo (str): Фото (Для тг бота) (Photo (For tg bot))
        Raise:
            ValueError: Якщо ціна менша або дорівнює 0 (If the price is less than or equal to 0)
            TypeError: Якщо типи переданих даних некоректні (If the types of data transmitted are incorrect)
        """
        self._title = title
        self._description = description
        self._price = price
        self._photo = photo

        if type(title) != str or type(description) != str or type(photo) != str or type(price) != int:
            raise TypeError("Опис кімнати повинен бути рядком")
        if price <= 0:
            raise ValueError("Ціна за добу не може бути менше 0")

    def __str__(self):
        """
        Description:
            Повертає інформацію про номер (Provides information about the room)
        Return:
            str: У форматі: title
                            description
                            Ціна: price грн/доба
        """
        return f"{self._title}\n{self._description}\nЦіна: {self._price} грн/доба"


class Booking:
    """
    Description:
        Клас для представлення бронювання (Class for representing reservations)
    """
    def __init__(self, client: Client, hotel: Hotel, room: Room, nights: int, checkin_date: str, rooms_count: int = 1):
        """
        Description:
            Ініціалізує бронювання, перевіряючи наявність номерів і правильність введених даних
            (Initializes the reservation, checking the availability of rooms and the correctness of the entered data)
        Args:
            client (Client): Клієнт (Client)
            hotel (Hotel): Готель (Hotel)
            room (Room): Номер (Room)
            nights (int): Кількість діб (Number of nights)
            checkin_date (date): Дата заїзду (Arrival date)
            checkout_date (date): Дата виїзду (Departure date)
            total_price (int): Загальна вартість (Загальна вартість)
        Raise:
            ValueError: Якщо готель не має номерів або дані введено некоректно
                        (If the hotel has no rooms or the data is entered incorrectly)
        """
        self._client = client
        self._hotel = hotel
        self._room = room
        self._checkin_date = checkin_date
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
        """
        Description:
            Повертає інформацію про бронювання (Provides details about the booking)
        Return:
            str: У форматі: Бронювання для Client(first_name, last_name):
                            Готель: Hotel(name)
                            Номер: room(title)
                            Кількість діб: nights
                            Кількість номерів: rooms_count
                            Дата заїзду: checkin_date (у форматі дд.мм.рррр)
                            Дата виїзду: _checkout_date (у форматі дд.мм.рррр)
                            Загальна ціна: total_price грн
        """
        return (f"Бронювання для {self._client._first_name.title()} {self._client._last_name.title()}:\n"
                f"Готель: {self._hotel._name.title()}\n"
                f"Номер: {self._room._title}\n"
                f"Кількість ночей: {self._nights}\n"
                f"Кількість номерів: {self._rooms_count}\n"
                f"Дата заїзду: {self._checkin_date.strftime('%d.%m.%Y')}\n"
                f"Дата виїзду: {self._checkout_date.strftime('%d.%m.%Y')}\n"
                f"Загальна ціна: {self._total_price} грн\n")

    def send_reminder(self):
        """
        Description:
            Надсилає нагадування про дату заїзду (Notifies the client about the check-in date)

        Returns:
            str: Повідомлення-нагадування (Reminder message)
        """
        today = date.today()
        days_left = (self._checkin_date - today).days

        if days_left > 1:
            message = (
                f"Нагадування: до вашого заїзду в готель залишилось {days_left} днів.\n"
                f"Готель: {self._hotel._name.title()}\n"
                f"Дата заїзду: {self._checkin_date.strftime('%d.%m.%Y')}\n"
                f"Ми чекаємо на вас!"
            )
        elif days_left == 1:
            message = (
                f"Нагадування: ваш заїзд в готель вже завтра!\n"
                f"Готель: {self._hotel._name.title()}\n"
                f"Номер: {self._room._title}\n"
                f"Дата заїзду: {self._checkin_date.strftime('%d.%m.%Y')}"
            )
        elif days_left == 0:
            message = (
                f"Сьогодні ваш заїзд у готель \"{self._hotel._name.title()}\"!\n"
                f"Чекаємо вас з нетерпінням!"
            )
        else:
            message = f"Дата заїзду ({self._checkin_date.strftime('%d.%m.%Y')}) вже минула."
        return message


h1 = Hotel("КиЇвська ХАтка", "вул. Хрещатик, 1, Київ", 4.0,
           3, "+380111111111", "info@kyivhatka.ua")

c1 = Client("aRtem", "LEVinskiy", "+380978517087", "levinskiy2306@gmail.com")

rooms = [
    Room("№1 Двохмісний номер", "Комфортний номер з двоспальним ліжком.", 1000, "img/room_image.jpg"),
    Room("№1 Двохмісний номер", "Комфортний номер з двоспальним ліжком.", 1300, "img/image.jpg"),
    Room("№3 Одномісний номер", "Номер для одного гостя.", 2000, "img/photo2.jpg")
]

b1 = Booking(c1, h1, rooms[0], 3, "30.05.2025", 1)
print(b1)
print(b1.send_reminder())