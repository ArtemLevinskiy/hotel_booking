class Hotel:
    def __init__(self, name : str, address : str, rating : float, num_room : int, price : int, phone : str, email : str):
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
            self._room_available -=n
            return True
        else:
            return f"Вільних номерів немає"

    def calculate_price(self, nights):
        return self._price * nights


h1 = Hotel("Готель Київ", "вул. Хрещатик, 1, Київ", 4.0, 10, 1400, "+3801111111111", "info@kyivhotel.ua")

print(h1.get_info())
print("Доступність номерів", h1.is_available())
print(h1.book_room(2))
print("Ціна за 5 ночей:", h1.calculate_price(5), "грн")












