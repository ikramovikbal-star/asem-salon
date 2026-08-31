import os
from datetime import date, datetime
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

load_dotenv()

app = Flask(__name__, static_folder="public", static_url_path="")

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "dev-only-change-this-secret"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

database_url = os.getenv("DATABASE_URL", "").strip()

# Локально можно ничего не указывать — будет SQLite.
if not database_url:
    database_url = "sqlite:///acem.db"

# Некоторые хостинги всё ещё выдают postgres://
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url

db = SQLAlchemy(app)

ALLOWED_SERVICES = {
    "Маникюр",
    "Педикюр",
    "Брови",
    "Стрижки",
    "Прически",
    "Макияж",
}

ALLOWED_TIMES = {
    "10:00",
    "11:00",
    "12:00",
    "13:00",
    "14:00",
    "15:00",
    "16:00",
    "17:00",
    "18:00",
}


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    service = db.Column(db.String(80), nullable=False)
    booking_date = db.Column(db.Date, nullable=False, index=True)
    booking_time = db.Column(db.String(5), nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    __table_args__ = (
        db.UniqueConstraint(
            "service",
            "booking_date",
            "booking_time",
            name="uq_booking_service_date_time"
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "service": self.service,
            "date": self.booking_date.isoformat(),
            "time": self.booking_time,
            "created_at": self.created_at.isoformat(),
        }


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if session.get("admin") is not True:
            return jsonify({"error": "Нет доступа"}), 401
        return fn(*args, **kwargs)
    return wrapper


with app.app_context():
    db.create_all()


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/booked-times")
def booked_times():
    service = request.args.get("service", "").strip()
    date_str = request.args.get("date", "").strip()

    if service not in ALLOWED_SERVICES:
        return jsonify({"error": "Неизвестная услуга"}), 400

    try:
        booking_date = date.fromisoformat(date_str)
    except ValueError:
        return jsonify({"error": "Неверная дата"}), 400

    rows = (
        Booking.query
        .filter_by(service=service, booking_date=booking_date)
        .all()
    )

    return jsonify({
        "times": sorted(row.booking_time for row in rows)
    })


@app.post("/api/bookings")
def create_booking():
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    phone = str(data.get("phone", "")).strip()
    service = str(data.get("service", "")).strip()
    date_str = str(data.get("date", "")).strip()
    booking_time = str(data.get("time", "")).strip()

    if len(name) < 2 or len(name) > 120:
        return jsonify({"error": "Введите корректное имя"}), 400

    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) < 11 or len(digits) > 15:
        return jsonify({"error": "Введите корректный номер телефона"}), 400

    if service not in ALLOWED_SERVICES:
        return jsonify({"error": "Неизвестная услуга"}), 400

    if booking_time not in ALLOWED_TIMES:
        return jsonify({"error": "Недоступное время"}), 400

    try:
        booking_date = date.fromisoformat(date_str)
    except ValueError:
        return jsonify({"error": "Неверная дата"}), 400

    if booking_date < date.today():
        return jsonify({"error": "Нельзя записаться на прошедшую дату"}), 400

    booking = Booking(
        name=name,
        phone=phone,
        service=service,
        booking_date=booking_date,
        booking_time=booking_time,
    )

    db.session.add(booking)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Это время уже занято. Выберите другое."
        }), 409

    return jsonify({
        "message": "Запись успешно создана",
        "booking": booking.to_dict()
    }), 201


@app.post("/api/admin/login")
def admin_login():
    data = request.get_json(silent=True) or {}
    password = str(data.get("password", ""))

    configured_password = os.getenv("ADMIN_PASSWORD", "").strip()

    if not configured_password:
        return jsonify({
            "error": "На сервере не настроен ADMIN_PASSWORD"
        }), 500

    if password != configured_password:
        return jsonify({"error": "Неверный код"}), 401

    session["admin"] = True
    return jsonify({"ok": True})


@app.post("/api/admin/logout")
@admin_required
def admin_logout():
    session.clear()
    return jsonify({"ok": True})


@app.get("/api/admin/bookings")
@admin_required
def admin_bookings():
    rows = (
        Booking.query
        .order_by(
            Booking.booking_date.asc(),
            Booking.booking_time.asc(),
            Booking.created_at.asc()
        )
        .all()
    )

    return jsonify({
        "bookings": [row.to_dict() for row in rows]
    })


@app.delete("/api/admin/bookings/<int:booking_id>")
@admin_required
def delete_booking(booking_id):
    booking = db.session.get(Booking, booking_id)

    if booking is None:
        return jsonify({"error": "Запись не найдена"}), 404

    db.session.delete(booking)
    db.session.commit()

    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
