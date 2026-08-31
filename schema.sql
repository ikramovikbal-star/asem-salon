CREATE TABLE IF NOT EXISTS bookings (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    phone VARCHAR(30) NOT NULL,
    service VARCHAR(80) NOT NULL,
    booking_date DATE NOT NULL,
    booking_time VARCHAR(5) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_booking_service_date_time
        UNIQUE (service, booking_date, booking_time)
);
