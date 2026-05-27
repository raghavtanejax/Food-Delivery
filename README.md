# 🍔 FoodieExpress — Food Delivery App

A full-stack food delivery web application for a single restaurant, built with **FastAPI** (Python), **MongoDB**, and a modern **HTML/CSS/JS** frontend.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **Auth** | JWT-based login/signup with Customer & Admin roles |
| 📢 **Notice Board** | Admin broadcasts daily updates on the home page |
| 🍽️ **Digital Menu** | Categorized menu (Starters, Mains, Drinks, Desserts) with cart |
| 📦 **Ordering** | Place orders, view history, track status |
| ⚙️ **Admin Dashboard** | Manage menu items, update order statuses, post notices |

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10+ with FastAPI
- **Database:** MongoDB (with Motor async driver)
- **Auth:** JWT tokens (python-jose) + bcrypt password hashing
- **Frontend:** Vanilla HTML / CSS / JavaScript (dark premium theme)

---

## 🚀 Getting Started

### Prerequisites

1. **Python 3.10+** installed ([python.org](https://python.org))
2. **MongoDB** running locally on `mongodb://localhost:27017`
   - Install from [mongodb.com/try/download](https://www.mongodb.com/try/download/community)
   - Or use **MongoDB Atlas** (cloud) — just update the URI in `.env`

### Step 1: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Configure Environment

Edit `backend/.env` if you need to change the MongoDB URI or JWT secret:

```env
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=food_delivery
JWT_SECRET=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440
```

### Step 3: Seed the Database (Dummy Data)

```bash
cd backend
python -m app.seed
```

This creates:
- **15 menu items** across 4 categories
- **Default admin account:** `admin@foodie.com` / `admin123`

### Step 4: Run the Server

```bash
cd backend

python -m uvicorn app.main:app --reload --port 8001

```

### Step 5: Open the App

Visit **[http://localhost:8000](http://localhost:8000)** in your browser.

---

## 👤 Default Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@foodie.com` | `admin123` |
| Customer | *(Sign up via the app)* | — |

---

## 📁 Project Structure

```
Food-Delivery/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI entry point
│   │   ├── config.py         # Environment config
│   │   ├── database.py       # MongoDB connection (Motor)
│   │   ├── seed.py           # Dummy data seeder
│   │   ├── models/           # Pydantic schemas
│   │   ├── routers/          # API endpoints
│   │   └── utils/            # JWT & auth helpers
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── index.html            # Login / Signup
│   ├── home.html             # Home + Notice Board
│   ├── menu.html             # Menu + Cart
│   ├── orders.html           # Order History
│   ├── admin.html            # Admin Dashboard
│   ├── css/style.css         # Design system
│   └── js/                   # Page-specific logic
└── README.md
```

---

## 🔌 API Endpoints

### Auth
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/auth/signup` | Register | Public |
| POST | `/api/auth/login` | Login → JWT | Public |
| GET | `/api/auth/me` | Current user | Auth |

### Menu
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/menu/` | List all items | Public |
| POST | `/api/menu/` | Add item | Admin |
| PUT | `/api/menu/{id}` | Update item | Admin |
| DELETE | `/api/menu/{id}` | Delete item | Admin |

### Orders
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/orders/` | Place order | Customer |
| GET | `/api/orders/my` | My orders | Customer |
| GET | `/api/orders/all` | All orders | Admin |
| PUT | `/api/orders/{id}/status` | Update status | Admin |

### Notices
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/notices/` | List notices | Public |
| POST | `/api/notices/` | Create notice | Admin |
| DELETE | `/api/notices/{id}` | Delete notice | Admin |

---
---

## 📝 License

MIT — built for learning and experimentation.
