
# List of hotel rooms
rooms = {
    101: {"price": 120, "available": True},
    102: {"price": 150, "available": True},
    103: {"price": 200, "available": True}
}


# Check room availability
def is_available(room_number):
    if room_number not in rooms:
        raise ValueError("Room does not exist")

    return rooms[room_number]["available"]


# Book a room
def book_room(room_number):
    if room_number not in rooms:
        raise ValueError("Room does not exist")

    if not rooms[room_number]["available"]:
        raise ValueError("Room already booked")

    rooms[room_number]["available"] = False
    return True


# Cancel a booking
def cancel_booking(room_number):
    if room_number not in rooms:
        raise ValueError("Room does not exist")

    if rooms[room_number]["available"]:
        raise ValueError("No booking to cancel")

    rooms[room_number]["available"] = True
    return True


# Calculate the stay price
def calculate_price(room_number, nights):
    if room_number not in rooms:
        raise ValueError("Room does not exist")

    if nights <= 0:
        raise ValueError("Invalid number of nights")

    return rooms[room_number]["price"] * nights
