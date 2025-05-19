# Gestione Produzione Scarpe

Applicazione web per la gestione della produzione di scarpe.

## Struttura del Progetto

- `frontend/`: Applicazione React
- `backend/`: API Python con FastAPI
- `docs/`: Documentazione
- `docker/`: Configurazione Docker

## Requisiti

- Node.js 16+
- Python 3.9+
- Docker (opzionale)

## Installazione

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Su Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Esecuzione

### Backend

```bash
cd backend
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm start
```

## Documentazione API

La documentazione delle API è disponibile all'indirizzo `http://localhost:8000/docs` quando il backend è in esecuzione.
