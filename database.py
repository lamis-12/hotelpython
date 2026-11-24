
import sqlite3
from pathlib import Path
from datetime import date
import hotel


def get_connection(db_path):
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db(db_path):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    connection = get_connection(db_path)

    try:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS rooms (
                room_number INTEGER PRIMARY KEY,
                price REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_number INTEGER NOT NULL,
                guest_name TEXT NOT NULL,
                email TEXT NOT NULL,
                check_in TEXT NOT NULL,
                check_out TEXT NOT NULL,
                total_price REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                FOREIGN KEY (room_number)
                    REFERENCES rooms(room_number)
            );
        """)

        for number, details in hotel.rooms.items():
            connection.execute(
                """
                INSERT OR IGNORE INTO rooms (room_number, price)
                VALUES (?, ?)
                """,
                (number, details["price"])
            )

        connection.commit()

    finally:
        connection.close()


def validate_dates(check_in, check_out):
    try:
        arrival = date.fromisoformat(check_in)
        departure = date.fromisoformat(check_out)
    except (ValueError, TypeError):
        raise ValueError("Invalid date format")

    nights = (departure - arrival).days

    if nights <= 0:
        raise ValueError("Check-out must be after check-in")

    return nights


def get_rooms(db_path, check_in=None, check_out=None):
    connection = get_connection(db_path)

    try:
        rooms = connection.execute(
            "SELECT * FROM rooms ORDER BY room_number"
        ).fetchall()

        if check_in is None and check_out is None:
            return [dict(room, available=True) for room in rooms]

        if not check_in or not check_out:
            raise ValueError("Both dates are required")

        validate_dates(check_in, check_out)

        result = []

        for room in rooms:
            conflict = connection.execute(
                """
                SELECT id FROM reservations
                WHERE room_number = ?
                AND status = 'active'
                AND NOT (check_out <= ? OR check_in >= ?)
                LIMIT 1
                """,
                (room["room_number"], check_in, check_out)
            ).fetchone()

            result.append({
                "room_number": room["room_number"],
                "price": room["price"],
                "available": conflict is None
            })

        return result

    finally:
        connection.close()


def get_room(db_path, room_number):
    connection = get_connection(db_path)

    try:
        room = connection.execute(
            "SELECT * FROM rooms WHERE room_number = ?",
            (room_number,)
        ).fetchone()

        return dict(room) if room else None

    finally:
        connection.close()


def create_booking(
    db_path,
    room_number,
    guest_name,
    email,
    check_in,
    check_out
):
    nights = validate_dates(check_in, check_out)

    guest_name = guest_name.strip()
    email = email.strip()

    if not guest_name or not email or "@" not in email:
        raise ValueError("Invalid guest information")

    connection = get_connection(db_path)

    try:
        connection.execute("BEGIN IMMEDIATE")

        room = connection.execute(
            "SELECT * FROM rooms WHERE room_number = ?",
            (room_number,)
        ).fetchone()

        if room is None:
            raise ValueError("Room does not exist")

        conflict = connection.execute(
            """
            SELECT id FROM reservations
            WHERE room_number = ?
            AND status = 'active'
            AND NOT (check_out <= ? OR check_in >= ?)
            LIMIT 1
            """,
            (room_number, check_in, check_out)
        ).fetchone()

        if conflict:
            raise ValueError("Room is already booked for these dates")

        total_price = room["price"] * nights

        cursor = connection.execute(
            """
            INSERT INTO reservations (
                room_number, guest_name, email,
                check_in, check_out, total_price
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                room_number,
                guest_name,
                email,
                check_in,
                check_out,
                total_price
            )
        )

        connection.commit()
        return cursor.lastrowid

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_reservations(db_path):
    connection = get_connection(db_path)

    try:
        reservations = connection.execute(
            """
            SELECT reservations.*, rooms.price
            FROM reservations
            JOIN rooms
            ON reservations.room_number = rooms.room_number
            ORDER BY reservations.id DESC
            """
        ).fetchall()

        return [dict(item) for item in reservations]

    finally:
        connection.close()


def cancel_booking(db_path, reservation_id):
    connection = get_connection(db_path)

    try:
        cursor = connection.execute(
            """
            UPDATE reservations
            SET status = 'cancelled'
            WHERE id = ? AND status = 'active'
            """,
            (reservation_id,)
        )

        connection.commit()

        if cursor.rowcount == 0:
            raise ValueError("Reservation not found or already cancelled")

        return True

    finally:
        connection.close()
