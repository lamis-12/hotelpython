
import pytest
import hotel


# Réinitialiser les chambres avant chaque test
@pytest.fixture(autouse=True)
def reset_rooms():
    hotel.rooms = {
        101: {"price": 120, "available": True},
        102: {"price": 150, "available": True},
        103: {"price": 200, "available": True}
    }


# 1. Tests de is_available()

def test_is_available():
    assert hotel.is_available(101) == True

def test_is_available_reserved_room():
    hotel.rooms[101]["available"] = False
    assert hotel.is_available(101) == False

def test_is_available_invalid_room():
    with pytest.raises(ValueError):
        hotel.is_available(999)


# 2. Tests de book_room()

def test_book_room():
    assert hotel.book_room(101) == True
    assert hotel.rooms[101]["available"] == False

def test_book_room_already_reserved():
    hotel.rooms[101]["available"] = False
    with pytest.raises(ValueError):
        hotel.book_room(101)

def test_book_room_invalid_room():
    with pytest.raises(ValueError):
        hotel.book_room(999)


# 3. Tests de cancel_booking()

def test_cancel_booking():
    hotel.rooms[101]["available"] = False
    assert hotel.cancel_booking(101) == True
    assert hotel.rooms[101]["available"] == True

def test_cancel_booking_not_reserved():
    with pytest.raises(ValueError):
        hotel.cancel_booking(101)

def test_cancel_booking_invalid_room():
    with pytest.raises(ValueError):
        hotel.cancel_booking(999)


# 4. Tests de calculate_price()

def test_calculate_price():
    assert hotel.calculate_price(101, 2) == 240

def test_calculate_price_one_night():
    assert hotel.calculate_price(101, 1) == 120

def test_calculate_price_zero_nights():
    with pytest.raises(ValueError):
        hotel.calculate_price(101, 0)

def test_calculate_price_negative_nights():
    with pytest.raises(ValueError):
        hotel.calculate_price(101, -2)

def test_calculate_price_invalid_room():
    with pytest.raises(ValueError):
        hotel.calculate_price(999, 2)

# 5. Tests supplémentaires : plusieurs chambres

def test_book_room_different_rooms():
    assert hotel.book_room(102) == True
    assert hotel.book_room(103) == True

    assert hotel.rooms[102]["available"] == False
    assert hotel.rooms[103]["available"] == False
    assert hotel.rooms[101]["available"] == True


def test_cancel_booking_does_not_affect_other_rooms():
    hotel.rooms[101]["available"] = False

    hotel.cancel_booking(101)

    assert hotel.rooms[101]["available"] == True
    assert hotel.rooms[102]["available"] == True
    assert hotel.rooms[103]["available"] == True


# 6. Tests supplémentaires : calcul des prix

@pytest.mark.parametrize("room_id, nights, expected", [
    (102, 3, 450),
    (103, 2, 400),
    (101, 5, 600)
])
def test_calculate_price_multiple_rooms(room_id, nights, expected):
    assert hotel.calculate_price(room_id, nights) == expected
