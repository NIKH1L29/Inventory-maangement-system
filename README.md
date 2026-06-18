# Inventory Management System

Full-stack inventory tracker with a **FastAPI** backend and a **plain HTML/CSS/JS** frontend.

Built for the Ethara AI assessment — supports natural-language commands like:

```
Add 50 units of "Dell Laptop" to warehouse A.
```

**API response:**

```json
{
  "action": "add_item",
  "item_name": "Dell Laptop",
  "quantity": 50,
  "location": "Warehouse A",
  "status": "success"
}
```

---

## Folder structure

Keep everything in one project folder:

```
Inventory management/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI routes
│   │   ├── database.py          # SQLite setup
│   │   ├── models.py            # DB tables
│   │   ├── schemas.py           # Request/response shapes
│   │   ├── crud.py              # Database operations
│   │   └── command_parser.py    # Plain-English command parser
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/
│       ├── config.js            # API URL config
│       └── app.js               # UI logic
├── .gitignore
└── README.md
```

---

## Run locally

### 1. Backend (Python + FastAPI)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000/docs** for interactive API docs.

### 2. Frontend

Open `frontend/index.html` in a browser, **or** serve it with a simple HTTP server:

```powershell
cd frontend
python -m http.server 5500
```

Then open **http://localhost:5500**. The default API URL is `http://localhost:8000`.

---

## Supported commands

| Command | Example |
|---------|---------|
| Add stock | `Add 50 units of "Dell Laptop" to warehouse A.` |
| Remove stock | `Remove 5 units of "Dell Laptop" from warehouse A.` |
| List inventory | `List inventory in warehouse A.` |
| List all | `Show inventory` |
| Transfer | `Transfer 10 units of "Dell Laptop" from warehouse A to warehouse B.` |

---

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/inventory` | List all stock |
| POST | `/api/items` | Add stock (JSON body) |
| POST | `/api/command` | Natural language command |
| GET | `/api/warehouses` | List warehouses |
| DELETE | `/api/items/{id}` | Remove an item row |


## Tech stack

- **Backend:** Python 3.11, FastAPI, SQLAlchemy, SQLite  
- **Frontend:** HTML5, CSS3, Vanilla JavaScript  
- **Deploy:** Docker, Render, Netlify  

##  Run Locally

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

**### Frontend**
cd frontend
python -m http.server 5500

**## Deployment Links**
GitHub Repo: https://github.com/NIKH1L29/Inventory-management-system

Docker Hub (Backend): https://hub.docker.com/r/nikhil29n/inventory-backend

Frontend (Netlify): https://inventory-management-frontend-a.netlify.app

Backend API (Render): https://inventory-backend-api-ogh7.onrender.com

## License
Developed by Nikhil N — AI Engineer / Python Developer
Actively applying for GenAI, Agentic AI, and LLM engineering roles.

