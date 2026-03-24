# Smart Parking System (Flask + MySQL + Vanilla JS)

A beginner-friendly full-stack project to manage parking slot booking with a modern responsive UI.

## Project Structure

```bash
Smart-parking-System/
├── app.py
├── README.md
├── sql/
│   └── schema.sql
├── static/
│   ├── script.js
│   └── style.css
└── templates/
    ├── admin.html
    └── index.html
```

## Prerequisites

- Python 3.9+
- MySQL Server
- VS Code (recommended)

## 1) Setup Database

1. Start your MySQL server.
2. Open MySQL client and run:

```sql
SOURCE /full/path/to/Smart-parking-System/sql/schema.sql;
```

> This creates `smart_parking` database with `slots` and `bookings` tables and inserts 6 default slots.

## 2) Setup Python Environment

In VS Code terminal (inside project root):

```bash
python -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate
pip install flask mysql-connector-python
```

## 3) Configure DB Credentials

Edit `app.py` and update `DB_CONFIG` if your MySQL credentials are different:

- `host`
- `user`
- `password`
- `database`

## 4) Run Application

```bash
python app.py
```

Then open:

- User Dashboard: `http://127.0.0.1:5000/`
- Admin Panel: `http://127.0.0.1:5000/admin`

## Features Implemented

- 6 parking slots in responsive card layout
- Green/Red status color coding
- Booking modal with Name + Vehicle Number
- Two-step flow: Validate booking -> Fake Payment
- Loading spinner while processing requests
- No page reload (`fetch` API used)
- Prevent booking already-booked slot
- Full parking alert when no slots are available
- Admin table view of all bookings

## Notes

- `debug=True` is enabled in development. Disable for production.
- This app is intentionally beginner-friendly and easy to extend.
