# Unify CLI

Unify CLI è uno strumento da riga di comando per gestire l'applicazione Shoe Production Manager.

## Installazione

1. Assicurati di avere Python 3.8+ installato
2. Installa le dipendenze:
   ```bash
   pip install -e .
   ```

## Utilizzo

### Avvio del backend

```bash
# Avvia il backend in modalità sviluppo (default)
unify backend start

# Specifica un ambiente diverso (dev, test, prod)
unify backend start --env test

# Specifica host e porta personalizzati
unify backend start --host 127.0.0.1 --port 8001

# Disabilita il reload automatico
unify backend start --no-reload
```

### Avvio del frontend

```bash
# Avvia il frontend in modalità sviluppo (default)
unify frontend start

# Specifica un ambiente diverso (dev, test, prod)
unify frontend start --env test

# Specifica host e porta personalizzati
unify frontend start --host 0.0.0.0 --port 3001

# Disabilita l'apertura automatica del browser
unify frontend start --no-open
```

### Installazione delle dipendenze

```bash
# Installa le dipendenze del backend
unify backend install-deps

# Installa le dipendenze del frontend
unify frontend install-deps
```

### Build del frontend per la produzione

```bash
# Build per l'ambiente di produzione (default)
unify frontend build

# Build per un ambiente specifico
unify frontend build --env test
```

## Configurazione

Il CLI si aspetta i seguenti file di configurazione per ambiente:

- `backend/.env.development` - Configurazione per l'ambiente di sviluppo
- `backend/.env.test` - Configurazione per l'ambiente di test
- `backend/.env.production` - Configurazione per l'ambiente di produzione
- `frontend/.env.development` - Configurazione per l'ambiente di sviluppo
- `frontend/.env.test` - Configurazione per l'ambiente di test
- `frontend/.env.production` - Configurazione per l'ambiente di produzione

## Sviluppo

Per installare il pacchetto in modalità sviluppo:

```bash
pip install -e .
```

## Licenza

MIT
