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

---

## Deploy and get public links (free)

You need **4 links** for submission:

1. GitHub repository  
2. Docker Hub image  
3. Frontend hosted URL  
4. Backend API hosted URL  

### Step 1 — Push to GitHub

```powershell
cd "C:\Users\Nikhil N\OneDrive\Documents\Inventory management"
git init
git add .
git commit -m "Inventory management system - FastAPI + HTML frontend"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/inventory-management.git
git push -u origin main
```

**Link:** `https://github.com/YOUR_USERNAME/inventory-management`

---

### Step 2 — Docker Hub image

1. Create account at [hub.docker.com](https://hub.docker.com)
2. Build and push:

```powershell
cd backend
docker build -t YOUR_DOCKER_USERNAME/inventory-api:latest .
docker login
docker push YOUR_DOCKER_USERNAME/inventory-api:latest
```

**Link:** `https://hub.docker.com/r/YOUR_DOCKER_USERNAME/inventory-api`

---

### Step 3 — Host backend API (Render — free tier)

1. Sign up at [render.com](https://render.com)
2. **New → Web Service**
3. Connect your GitHub repo
4. Settings:
   - **Root directory:** `backend`
   - **Runtime:** Docker *(or Python with start command below)*
   - **Start command (if not Docker):** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment variables:**
     - `ALLOWED_ORIGINS` = your frontend URL (add after Step 4)

**Link:** `https://inventory-api-xxxx.onrender.com`

Test: `https://YOUR-API.onrender.com/api/health`

> **Note:** Free tier sleeps after inactivity. First request may take ~30 seconds.

**Alternative:** [Railway](https://railway.app) — similar steps, deploy from GitHub `backend/` folder.

---

### Step 4 — Host frontend (Netlify — free)

1. Sign up at [netlify.com](https://netlify.com)
2. **Add new site → Deploy manually** (drag the `frontend/` folder)
   - Or connect GitHub and set **publish directory** to `frontend`
3. After deploy, copy your site URL, e.g. `https://your-site.netlify.app`
4. Update `frontend/js/config.js` — set `DEFAULT_API_URL` to your Render API URL
5. Redeploy frontend
6. Update Render env var `ALLOWED_ORIGINS` to your Netlify URL

**Link:** `https://your-site.netlify.app`

**Alternative:** [GitHub Pages](https://pages.github.com) — push `frontend/` to `gh-pages` branch.

---

## Submission checklist

| Item | Example |
|------|---------|
| GitHub repo | `https://github.com/you/inventory-management` |
| Docker Hub | `https://hub.docker.com/r/you/inventory-api` |
| Frontend URL | `https://your-site.netlify.app` |
| Backend API URL | `https://inventory-api-xxxx.onrender.com` |

Before submitting, verify:

- [ ] Frontend connects (green "Connected" status)
- [ ] Command `Add 50 units of "Dell Laptop" to warehouse A.` returns success JSON
- [ ] Inventory table updates after add/remove
- [ ] `/api/health` returns `{"status":"healthy"}`

---

## Tech stack

- **Backend:** Python 3.11, FastAPI, SQLAlchemy, SQLite  
- **Frontend:** HTML5, CSS3, Vanilla JavaScript  
- **Deploy:** Docker, Render, Netlify  

---

## License

MIT — use freely for your assessment submission.
