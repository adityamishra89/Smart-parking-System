"""Smart Parking System Flask application.

This app demonstrates a beginner-friendly but production-style structure using
Flask + MySQL + vanilla JS frontend interactions.
"""

from flask import Flask, jsonify, render_template, request
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Centralized database configuration.
# Update these values to match your local MySQL setup.
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "smart_parking",
}


def get_db_connection():
    """Create and return a new database connection."""
    return mysql.connector.connect(**DB_CONFIG)


def fetch_slots():
    """Fetch all parking slots ordered by id."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, status FROM slots ORDER BY id")
    slots = cursor.fetchall()
    cursor.close()
    conn.close()
    return slots


@app.route("/")
def index():
    """Render main dashboard page."""
    return render_template("index.html")


@app.route("/slots", methods=["GET"])
def get_slots():
    """Return all slots in JSON format for AJAX rendering."""
    try:
        slots = fetch_slots()
        return jsonify({"success": True, "slots": slots})
    except Error as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@app.route("/book", methods=["POST"])
def book_slot():
    """Validate booking request before payment.

    This endpoint checks:
    - user input validity
    - slot existence
    - slot availability
    - whether parking is already full
    """
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    vehicle = (data.get("vehicle") or "").strip()
    slot_id = data.get("slot_id")

    if not name or not vehicle or not slot_id:
        return jsonify({"success": False, "message": "Please fill all booking details."}), 400

    try:
        slot_id = int(slot_id)
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Invalid slot selected."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) AS available_count FROM slots WHERE status = 'Available'")
        available_count = cursor.fetchone()["available_count"]
        if available_count == 0:
            return jsonify({"success": False, "message": "Parking is full. No slots available."}), 409

        cursor.execute("SELECT id, status FROM slots WHERE id = %s", (slot_id,))
        slot = cursor.fetchone()

        if slot is None:
            return jsonify({"success": False, "message": "Selected slot not found."}), 404
        if slot["status"] == "Booked":
            return jsonify({"success": False, "message": "This slot is already booked."}), 409

        return jsonify(
            {
                "success": True,
                "message": "Slot is available. Click Fake Payment to confirm booking.",
            }
        )
    except Error as exc:
        return jsonify({"success": False, "message": str(exc)}), 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "conn" in locals() and conn.is_connected():
            conn.close()


@app.route("/payment", methods=["POST"])
def payment():
    """Simulate payment and finalize booking in a DB transaction."""
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    vehicle = (data.get("vehicle") or "").strip()
    slot_id = data.get("slot_id")

    if not name or not vehicle or not slot_id:
        return jsonify({"success": False, "message": "Payment failed: missing details."}), 400

    try:
        slot_id = int(slot_id)
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Payment failed: invalid slot."}), 400

    try:
        conn = get_db_connection()
        conn.start_transaction()
        cursor = conn.cursor(dictionary=True)

        # Lock the slot row to avoid race conditions in simultaneous booking attempts.
        cursor.execute("SELECT id, status FROM slots WHERE id = %s FOR UPDATE", (slot_id,))
        slot = cursor.fetchone()

        if slot is None:
            conn.rollback()
            return jsonify({"success": False, "message": "Slot not found."}), 404

        if slot["status"] == "Booked":
            conn.rollback()
            return jsonify({"success": False, "message": "Payment failed: slot already booked."}), 409

        cursor.execute("UPDATE slots SET status = 'Booked' WHERE id = %s", (slot_id,))
        cursor.execute(
            "INSERT INTO bookings (name, vehicle, slot_id) VALUES (%s, %s, %s)",
            (name, vehicle, slot_id),
        )

        conn.commit()
        return jsonify({"success": True, "message": "Payment successful! Slot booked."})
    except Error as exc:
        if "conn" in locals() and conn.is_connected():
            conn.rollback()
        return jsonify({"success": False, "message": str(exc)}), 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "conn" in locals() and conn.is_connected():
            conn.close()


@app.route("/admin")
def admin_panel():
    """Render all bookings for admin view."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT b.name, b.vehicle, b.slot_id
            FROM bookings b
            ORDER BY b.id DESC
            """
        )
        bookings = cursor.fetchall()
        return render_template("admin.html", bookings=bookings)
    except Error as exc:
        return render_template("admin.html", bookings=[], error=str(exc))
    finally:
        if "cursor" in locals():
            cursor.close()
        if "conn" in locals() and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    # Debug=True is fine for learning/development. Use False in production.
    app.run(debug=True)
