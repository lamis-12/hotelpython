
import pytest
import database


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "test.db"
    database.init_db(path)
    return str(path)


def test_get_rooms(db_path):
    rooms = database.get_rooms(db_path)

    assert len(rooms) == 3
    assert rooms[0]["room_number"] == 101


def test_create_booking(db_path):
    reservation_id = database.create_booking(
        db_path,
        101,
        "Test User",
        "test@example.com",
        "2026-12-01",
        "2026-12-03"
    )

    assert reservation_id > 0


def test_calculate_total_price(db_path):
    database.create_booking(
        db_path,
        101,
        "Test User",
        "test@example.com",
        "2026-12-01",
        "2026-12-03"
    )

    reservations = database.get_reservations(db_path)

    assert reservations[0]["total_price"] == 240


def test_reject_invalid_room(db_path):
    with pytest.raises(ValueError):
        database.create_booking(
            db_path,
            999,
            "Test User",
            "test@example.com",
            "2026-12-01",
            "2026-12-03"
        )


def test_reject_overlapping_booking(db_path):
    database.create_booking(
        db_path,
        101,
        "First User",
        "first@example.com",
        "2026-12-01",
        "2026-12-04"
    )

    with pytest.raises(ValueError):
        database.create_booking(
            db_path,
            101,
            "Second User",
            "second@example.com",
            "2026-12-02",
            "2026-12-05"
        )


def test_allow_non_overlapping_booking(db_path):
    database.create_booking(
        db_path,
        101,
        "First User",
        "first@example.com",
        "2026-12-01",
        "2026-12-03"
    )

    second_id = database.create_booking(
        db_path,
        101,
        "Second User",
        "second@example.com",
        "2026-12-03",
        "2026-12-05"
    )

    assert second_id > 0


def test_reject_checkout_before_checkin(db_path):
    with pytest.raises(ValueError):
        database.create_booking(
            db_path,
            101,
            "Test User",
            "test@example.com",
            "2026-12-05",
            "2026-12-03"
        )


def test_reject_zero_nights(db_path):
    with pytest.raises(ValueError):
        database.create_booking(
            db_path,
            101,
            "Test User",
            "test@example.com",
            "2026-12-01",
            "2026-12-01"
        )


def test_reject_invalid_email(db_path):
    with pytest.raises(ValueError):
        database.create_booking(
            db_path,
            101,
            "Test User",
            "invalid-email",
            "2026-12-01",
            "2026-12-03"
        )


def test_cancel_booking(db_path):
    reservation_id = database.create_booking(
        db_path,
        101,
        "Test User",
        "test@example.com",
        "2026-12-01",
        "2026-12-03"
    )

    result = database.cancel_booking(db_path, reservation_id)

    assert result is True

    reservations = database.get_reservations(db_path)

    assert reservations[0]["status"] == "cancelled"


def test_cancel_twice(db_path):
    reservation_id = database.create_booking(
        db_path,
        101,
        "Test User",
        "test@example.com",
        "2026-12-01",
        "2026-12-03"
    )

    database.cancel_booking(db_path, reservation_id)

    with pytest.raises(ValueError):
        database.cancel_booking(db_path, reservation_id)
