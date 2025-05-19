# Shoe Production Manager - Backend

Backend API per la gestione della produzione di scarpe, sviluppato con FastAPI e SQLAlchemy.

## Requisiti

- Python 3.8+
- Pipenv (consigliato) o pip
- Database SQLite (predefinito) o PostgreSQL

## Installazione

1. Clona il repository
2. Crea un ambiente virtuale (consigliato):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Su Windows: .\venv\Scripts\activate
   ```
3. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```
4. Copia il file di configurazione di esempio e personalizzalo:
   ```bash
   cp .env.example .env
   ```
5. Modifica il file `.env` secondo le tue esigenze

## Avvio dell'applicazione

### Modalità sviluppo

```bash
uvicorn app.main:app --reload
```

L'API sarà disponibile all'indirizzo: http://localhost:8000

### Documentazione API

- Documentazione interattiva (Swagger UI): http://localhost:8000/docs
- Documentazione alternativa (ReDoc): http://localhost:8000/redoc

## Struttura del progetto

```
backend/
├── app/                     # Codice sorgente dell'applicazione
│   ├── api/                 # Endpoint API
│   ├── core/                # Configurazione e logica di base
│   ├── db/                  # Configurazione del database
│   ├── models/              # Modelli SQLAlchemy
│   ├── schemas/             # Modelli Pydantic
│   └── main.py              # Punto di ingresso dell'applicazione
├── tests/                   # Test
├── .env.example             # File di esempio per le variabili d'ambiente
├── .env                     # Variabili d'ambiente (ignorato da git)
├── requirements.txt         # Dipendenze principali
└── requirements-dev.txt     # Dipendenze di sviluppo
```

## Utente predefinito

È stato creato un utente amministratore predefinito con le seguenti credenziali:

- Email: `super.unify@purpleswan.com`
- Password: `password01!`

## Variabili d'ambiente

Le principali variabili d'ambiente configurabili sono:

- `DATABASE_URL`: URL di connessione al database
- `SECRET_KEY`: Chiave segreta per la firma dei token JWT
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Durata del token di accesso in minuti
- `FIRST_SUPERUSER_EMAIL`: Email dell'utente amministratore predefinito
- `FIRST_SUPERUSER_PASSWORD`: Password dell'utente amministratore predefinito

## Test

Per eseguire i test:

```bash
pytest
```

## Deployment

Per il deployment in produzione, assicurati di:

1. Impostare `DEBUG=False`
2. Utilizzare un database di produzione (es. PostgreSQL)
3. Configurare un server ASGI come Uvicorn con Gunicorn
4. Configurare un reverse proxy come Nginx
5. Utilizzare HTTPS con certificati SSL validi

## Licenza

MIT
