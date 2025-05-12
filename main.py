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






bot.polling(none_stop=True)
