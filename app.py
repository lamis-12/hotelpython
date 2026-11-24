
import os
from flask import (
    Flask, render_template, request,
    redirect, url_for, flash, abort
)
import database


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get(
            "SECRET_KEY", "development-key-change-before-deployment"
        ),
        DATABASE=os.path.join(app.instance_path, "hotel.db")
    )

    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    database.init_db(app.config["DATABASE"])

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/rooms")
    def rooms():
        check_in = request.args.get("check_in", "")
        check_out = request.args.get("check_out", "")

        try:
            rooms_list = database.get_rooms(
                app.config["DATABASE"],
                check_in or None,
                check_out or None
            )
        except ValueError as error:
            flash(str(error), "error")
            return redirect(url_for("home"))

        return render_template(
            "rooms.html",
            rooms=rooms_list,
            check_in=check_in,
            check_out=check_out
        )

    @app.route("/book/<int:room_number>", methods=["GET", "POST"])
    def booking(room_number):
        room = database.get_room(
            app.config["DATABASE"], room_number
        )

        if room is None:
            abort(404)

        if request.method == "POST":
            check_in = request.form.get("check_in", "")
            check_out = request.form.get("check_out", "")
            guest_name = request.form.get("guest_name", "")
            email = request.form.get("email", "")

            try:
                database.create_booking(
                    app.config["DATABASE"],
                    room_number,
                    guest_name,
                    email,
                    check_in,
                    check_out
                )

                flash("Reservation successful!", "success")
                return redirect(url_for("reservations"))

            except ValueError as error:
                flash(str(error), "error")

        return render_template(
            "booking.html",
            room=room,
            check_in=request.values.get("check_in", ""),
            check_out=request.values.get("check_out", "")
        )

    @app.route("/reservations")
    def reservations():
        reservation_list = database.get_reservations(
            app.config["DATABASE"]
        )

        return render_template(
            "reservations.html",
            reservations=reservation_list
        )

    @app.route("/cancel/<int:reservation_id>", methods=["POST"])
    def cancel(reservation_id):
        try:
            database.cancel_booking(
                app.config["DATABASE"],
                reservation_id
            )
            flash("Reservation cancelled successfully!", "success")

        except ValueError as error:
            flash(str(error), "error")

        return redirect(url_for("reservations"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
