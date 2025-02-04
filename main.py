
from collections import UserDict
from datetime import datetime, timedelta
import pickle


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Birthday(Field):
    def __init__(self, value):
        if value:
            try:
                datetime.strptime(value, "%d.%m.%Y")
            except ValueError:
                raise ValueError("Birthday must be in format DD.MM.YYYY")
        self.value = value

    def __repr__(self):
        return self.value if self.value else "No birthday"


class Phone(Field):
    def __init__(self, number):
        if not isinstance(number, str) or not number.isdigit() or len(number) != 10:
            raise ValueError("The phone number must be a string of 10 digits")
        super().__init__(number)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(None)

    def add_phone(self, number):
        phone = Phone(number)
        self.phones.append(phone)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def remove_phone(self, number):
        for phone in self.phones:
            if phone.value == number:
                self.phones.remove(phone)
                return True
        return False

    def edit_phone(self, old_number, new_number):
        if self.find_phone(old_number):
            self.add_phone(new_number)
            self.remove_phone(old_number)
            return True
        else:
            raise ValueError(f"Old number {old_number} not found")

    def find_phone(self, number):
        for phone in self.phones:
            if phone.value == number:
                return phone
        return None

    def __str__(self):
        birthday_str = f", birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError(f"Record with name {name} not found.")

    def get_upcoming_birthdays(self):
        today = datetime.now()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday and record.birthday.value:
                try:
                    birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y")
                except ValueError:
                    continue

                this_year_birthday = birthday_date.replace(year=today.year)

                if this_year_birthday < today:
                    this_year_birthday = this_year_birthday.replace(year=today.year + 1)

                if this_year_birthday.weekday() == 5:
                    this_year_birthday += timedelta(days=2)
                elif this_year_birthday.weekday() == 6:
                    this_year_birthday += timedelta(days=1)
                days_until_birthday = (this_year_birthday - today).days

                if 0 <= days_until_birthday <= 7:
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "birthday": this_year_birthday.strftime("%d.%m.%Y"),
                    })

        return upcoming_birthdays

    def __str__(self):
        if not self.data:
            return "The address book is empty."
        return "\n".join(str(record) for record in self.data.values())


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

    # Decorator to handle input errors


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"ValueError: {e}"
        except IndexError:
            return "Please provide the correct number of arguments."
        except KeyError:
            return "Contact not found."
        except Exception as e:
            return str(e)

    return inner


@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def show_upcoming_birthdays(address_book):
    upcoming = address_book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays."
    return "\n".join([f"{item['name']}: {item['birthday']}" for item in upcoming])


@input_error
def change_contact(args, address_book):
    name, old_phone, new_phone = args
    record = address_book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Contact updated."
    else:
        raise KeyError(f"Contact with name {name} not found.")


@input_error
def show_phone(args, address_book):
    name = args[0]
    record = address_book.find(name)
    if record:
        return f"Phone(s) for {name}: {', '.join(phone.value for phone in record.phones)}"
    else:
        raise KeyError


@input_error
def show_all_phones(address_book):
    if not address_book.data:
        return "No contacts available."
    return "\n".join([str(record) for record in address_book.data.values()])


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if not record:
        raise ValueError(f"Contact {name} not found.")
    record.add_birthday(birthday)
    return f"Birthday {birthday} added to contact {name}."


@input_error
def show_birthday(args, address_book):
    name = args[0]
    record = address_book.find(name)
    if not record or not record.birthday:
        raise ValueError(f"No birthday found for contact {name}.")
    return f"Birthday of {name}: {record.birthday}"


def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
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
            print(show_all_phones(book))
        elif command == "birthdays":
            print(show_upcoming_birthdays(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
