-- Smart Parking System schema
-- Run this file in MySQL to initialize the project database.

CREATE DATABASE IF NOT EXISTS smart_parking;
USE smart_parking;

-- Store each parking slot status
CREATE TABLE IF NOT EXISTS slots (
    id INT PRIMARY KEY,
    status ENUM('Available', 'Booked') NOT NULL DEFAULT 'Available'
);

-- Store confirmed bookings
CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    vehicle VARCHAR(40) NOT NULL,
    slot_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (slot_id) REFERENCES slots(id)
);

-- Seed at least 6 parking slots
INSERT INTO slots (id, status)
VALUES
    (1, 'Available'),
    (2, 'Available'),
    (3, 'Available'),
    (4, 'Available'),
    (5, 'Available'),
    (6, 'Available')
ON DUPLICATE KEY UPDATE status = VALUES(status);
