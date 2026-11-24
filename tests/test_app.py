
def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Find Your Perfect Stay" in response.data


def test_rooms_page(client):
    response = client.get("/rooms")

    assert response.status_code == 200
    assert b"Room 101" in response.data


def test_booking_page(client):
    response = client.get("/book/101")

    assert response.status_code == 200
    assert b"Book Room 101" in response.data


def test_booking_success(client):
    response = client.post(
        "/book/101",
        data={
            "guest_name": "Test User",
            "email": "test@example.com",
            "check_in": "2026-12-01",
            "check_out": "2026-12-03"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Reservation successful!" in response.data


def test_booking_invalid_dates(client):
    response = client.post(
        "/book/101",
        data={
            "guest_name": "Test User",
            "email": "test@example.com",
            "check_in": "2026-12-05",
            "check_out": "2026-12-03"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Check-out must be after check-in" in response.data


def test_booking_nonexistent_room(client):
    response = client.get("/book/999")

    assert response.status_code == 404


def test_cancel_reservation(client, app):
    import database

    reservation_id = database.create_booking(
        app.config["DATABASE"],
        101,
        "Test User",
        "test@example.com",
        "2026-12-01",
        "2026-12-03"
    )

    response = client.post(
        f"/cancel/{reservation_id}",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Reservation cancelled successfully!" in response.data


def test_reservations_page(client):
    response = client.get("/reservations")

    assert response.status_code == 200
    assert b"Reservations" in response.data
