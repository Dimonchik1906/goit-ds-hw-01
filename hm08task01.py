import pickle
from pathlib import Path
from collections import UserDict
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name can not be empty")
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be 10 digits")
        super().__init__(value) 

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")              

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    # реалізація класу
    def add_phone(self, phone):
        self.phones.append(Phone(phone))
    # видалення контакту
    def remove_phone(self, phone_number):
        self.phones = [p for p in self.phones if p.value != phone_number]
    # пошук номера
    def find_phone(self, number):
        for p in self.phones:
            if p.value == number:
                return p
        return None
    # зміна номеру
    def edit_phone(self, old_number, new_number):     
        edit_cash = self.find_phone(old_number)
        if edit_cash:
            self.add_phone(new_number)
            self.remove_phone(old_number)
            return
        raise ValueError("Phone number not found")
    # додаємо день народдження
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
    # ввивід тексту
    def __str__(self):
        if self.birthday:
            message = f"Name contact: {self.name.value}, phone: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday.value}"
        else: 
            message = f"Name contact: {self.name.value}, phone: {'; '.join(p.value for p in self.phones)}"
        return message

class AddressBook(UserDict):
    # додати запис
    def add_record(self, record: Record):
        self.data[record.name.value] = record
    # знайти запис
    def find(self, name):
        return self.data.get(name)
    # видалити запис
    def delete(self, name):
        if name in self.data:
            del self.data[name]
    
    @staticmethod
    def find_next_weekday(d, weekday):
        # Знаходження наступного  дня 
        days_ahead = weekday - d.weekday()
        if days_ahead <= 0:  # Якщо день народження вже минув у цьому тижні.
            days_ahead += 7
        return d + timedelta(days_ahead)
    #фукція зназодження найблищих днів народження
    def get_upcoming_birthdays(self, days=7) -> list:
        today = datetime.today().date()
        upcoming_birthdays = []

        for user in self.data.values():
            if user.birthday is None:
                continue
            
            birthday_date = datetime.strptime(user.birthday.value, "%d.%m.%Y").date()
            birthday_this_year = birthday_date.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            if 0 <= (birthday_this_year - today).days <= days:
                if birthday_this_year.weekday() >= 5:  # якщо субота або неділя
                    birthday_this_year += timedelta(days=(7 - birthday_this_year.weekday()))  # Привітання в понеділок
                congratulation_date_str = birthday_this_year.strftime("%Y.%m.%d")
                upcoming_birthdays.append(
                    {
                        "name": user.name.value,
                        "congratulation_date": congratulation_date_str,
                    }
                )
        return upcoming_birthdays
#опрацювання помилок
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            if func.__name__ ==  "add_birthday":
                return "Invalid date format. Use DD.MM.YYYY"
            if func.__name__ ==  "add_contact":
                return "Give me name and 10 didgits phone, please."
            return f"The entered data is not correcte {e}"
        except IndexError:
            return "Enter the argument for the command."
        except KeyError:
            return "This contact does not exist."
        except Exception as e:
            return f"Something went wrong: {e}"
    return inner

@input_error #ддодав врахувавши помилику попереднього завдання
def parse_input(user_input): #Функція отримання команди від користувача
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args
#додати контакт
@input_error
def add_contact(args, book): #Функція додавання нового контакту
    name, phone, *_ = args
    record = book.find(name)
    message = f"Contact {name} updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = f"Contact {name} added."
    if phone:
        if not record.find_phone(phone):
            record.add_phone(phone)
        else:
            return f"Phone {phone} is already in the contact {name}"
    return message
#зміна номеру телефону
@input_error
def change_contact(args, book): #Функція зміну номеру 
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return f"Contact for {name} updated."
    else:
        raise KeyError
#показати номер телефону
@input_error
def show_phone(args,book): 
    name,  = args
    record = book.find(name)
    if record:
        return "; ".join([str(phone) for phone in record.phones])
    else:
        raise KeyError
    #показати всі контакти
def show_all(book): #Функція показу всіх контактів
    return "\n\n".join([str(record) for record in book.data.values()]) if book.data else "No contacts found."
#доддати день народження
@input_error
def add_birthday(args, book):
    name, birthday, *_ = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday for {name} added: {birthday}"
    else:
        raise KeyError
    # Показ дати дня народження
@input_error
def show_birthday(args, book):
    (name,) = args
    record = book.find(name)
    if record and record.birthday:
        return str(record.birthday)
    return "Birthday not found for this contact."

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

def main(): #Функція обробки команд
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        
        user_input = input("Enter a command: ").strip().lower()
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)
            break

        elif command == "hello":
            print("How can I help you?")
            
        elif command == "add":
            print(add_contact(args, book))
            
        elif command == "change":
            print(change_contact(args, book))
            
        elif command == "phone":
            print(show_phone(args, book))
            
        elif command == "all":
            print(show_all(book))
            
        elif command == "add-birthday":
            print(add_birthday(args, book))
            
        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            birthdays = book.get_upcoming_birthdays()
            if not birthdays:
                print("There are no upcoming birthdays.")
                continue
            for day in birthdays:
                print(f"{day}")
                
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()

