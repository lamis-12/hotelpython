
document.addEventListener("DOMContentLoaded", function () {

    const checkIn = document.getElementById("check_in");
    const checkOut = document.getElementById("check_out");

    const bookingCheckIn =
        document.getElementById("booking_check_in");

    const bookingCheckOut =
        document.getElementById("booking_check_out");

    function connectDates(start, end) {
        if (!start || !end) return;

        function updateMinimum() {
            if (start.value) {
                const minimumDate = new Date(start.value);
                minimumDate.setDate(minimumDate.getDate() + 1);

                const year = minimumDate.getFullYear();
                const month = String(
                    minimumDate.getMonth() + 1
                ).padStart(2, "0");

                const day = String(
                    minimumDate.getDate()
                ).padStart(2, "0");

                end.min = `${year}-${month}-${day}`;
            }
        }

        start.addEventListener("change", updateMinimum);
        updateMinimum();
    }

    connectDates(checkIn, checkOut);
    connectDates(bookingCheckIn, bookingCheckOut);

});
