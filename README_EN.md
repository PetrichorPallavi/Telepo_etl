# Telepo_etl
# 🗺️ Tokyo Business Search System

A location-based business search application built using **OpenStreetMap (OSM), PostGIS, and Streamlit**.
This system allows users to search for nearby businesses (e.g., cafes, clinics) around train stations in Tokyo.

---

# 🚀 Features

* 🔍 Search businesses by keyword (English / Japanese)
* 📍 Station-based location search
* 🗺️ Interactive map visualization (Folium)
* 📊 Tabular results with business details
* 🔄 Manual data update pipeline (OSM → DB)
* ⚡ Fast geospatial queries using PostGIS

---

# 🧱 System Architecture

```
           OpenStreetMap (Geofabrik)
                     ↓
            osm2pgsql (ETL)
                     ↓
               PostGIS DB
                     ↓
           SQL Queries (search)
                     ↓
              Streamlit App
```

---

# 🧠 Why This Architecture?

### ❌ Why NOT direct OSM API?

* Slow (network latency)
* Rate-limited
* Not production-safe

### ✅ Why DB + ETL?

* ⚡ Fast (local indexed queries)
* 🔁 Reliable (no external dependency)
* 🔍 Advanced filtering (distance, tags)
* 📊 Scalable for large datasets

---

# 🛠️ Tech Stack

| Component        | Technology                |
| ---------------- | ------------------------- |
| Backend DB       | PostgreSQL + PostGIS      |
| Data Source      | OpenStreetMap (Geofabrik) |
| ETL              | osm2pgsql                 |
| Frontend         | Streamlit                 |
| Maps             | Folium                    |
| Containerization | Docker                    |

---

# 📦 Prerequisites

Install the following:

### 1. Docker Desktop

https://www.docker.com/products/docker-desktop

### 2. Python (3.10+ recommended)

https://www.python.org/downloads/

---

# 📥 Project Setup

## 1. Clone Repository

```bash
git clone https://github.com/PetrichorPallavi/Telepo_etl.git
cd tokyo-osm-system
```

---

## 2. Download OSM Data

Download Kanto region data:

👉 https://download.geofabrik.de/asia/japan/kanto-latest.osm.pbf

Place file in:

```
/data/kanto-latest.osm.pbf
```

---

## 3. Start Docker Services

```bash
docker compose up -d
```

This will start:

* PostGIS database
* OSM importer
* OSM updater

---

## 4. Initialize Database (First Time Only)

Import OSM data:

```bash
docker compose run osm_import
```

---

## 5. Create Business Table

Run SQL:

```bash
docker exec -i tokyo_postgis psql -U postgres -d tokyo_osm < sql/create_business_table.sql
```

---

## 6. Refresh Business Data

```bash
docker exec -i tokyo_postgis psql -U postgres -d tokyo_osm < sql/refresh_business_table.sql
```

---

## 7. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## 8. Run Application

```bash
cd app
streamlit run app.py
```

Open browser:

```
http://localhost:8501
```

---

# 🔄 Updating Data

You can update OSM data using:

### Option A — Manual Script

```powershell
.\update.ps1
```

### Option B — UI Button (Recommended)

* Click **"Update Data"** in sidebar
* Automatically:

  * Fetches latest OSM updates
  * Refreshes business table
  * Updates timestamp

---

# 📁 Project Structure

```
tokyo-osm-system/
│
├── app/
│   ├── app.py
│   └── queries.py
│
├── sql/
│   ├── create_business_table.sql
│   └── refresh_business_table.sql
│
├── data/
│   └── kanto-latest.osm.pbf
│
├── docker-compose.yml
├── update.ps1
└── README.md
```

---

# ⚙️ Configuration

### Database Connection (app/queries.py)

```python
postgresql+psycopg://postgres:postgres@127.0.0.1:5433/tokyo_osm
```

Ensure Docker is mapped to port **5433**.

---

# ⚠️ Troubleshooting

## ❌ DB Connection Timeout

```bash
docker compose up -d
```

---

## ❌ Port Conflict

Change in `docker-compose.yml`:

```yaml
ports:
  - "5433:5432"
```

---

## ❌ SQL File Not Found in Container

Ensure:

```yaml
volumes:
  - ./sql:/sql
```

---

## ❌ PowerShell Script Blocked

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

---

# 🚀 Future Improvements

* 🔍 Fuzzy search / autocomplete
* 🇯🇵 Japanese-English keyword normalization
* 📄 Pagination / infinite scroll
* ⚡ Query optimization (indexes, caching)
* 🧠 Ranking (distance + popularity)

---

# 📌 Notes

* Phone availability depends on OSM data completeness
* Not all businesses have full metadata

---

# 👨‍💻 Author

Developed as a geospatial search system prototype using real-world OSM data.

---

# 📄 License


