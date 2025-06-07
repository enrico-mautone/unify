# Unify Entity System

Questo modulo gestisce il sistema di entità di Unify, permettendo la creazione dinamica di tabelle e relazioni nel database.

## Setup Iniziale

### Prerequisiti
- Python 3.8+
- PostgreSQL
- Alembic

### Configurazione Database
1. Crea un database PostgreSQL
2. Configura le variabili d'ambiente nel file `.env`:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

### Setup del Database

#### Opzione 1: Setup Automatico
Per eseguire l'intero processo di setup in un unico comando:
```bash
cd backend/entity
python setup.py
```

#### Opzione 2: Setup Manuale
Se preferisci eseguire i passaggi uno alla volta:

1. Esegui la migrazione iniziale per creare la tabella `entities`:
```bash
cd backend/entity
alembic upgrade add_entity_fields
```

2. Inserisci l'entità Users nella tabella `entities`:
```bash
python -m commands.insert_users_entity
```

3. Genera le migrazioni per tutte le entità:
```bash
python -m commands.generate_entity_migrations
```

4. Esegui le migrazioni generate:
```bash
python -m commands.run_migrations
```

5. Crea l'utente di default:
```bash
python -m commands.setup_users
```

### Reset del Database
Per riportare il database allo stato iniziale (solo tabella `entities` con l'entità Entity):
```bash
cd backend/entity
python -m commands.reset_db
```

## Struttura del Database

### Tabella `entities`
- Contiene le definizioni di tutte le entità del sistema
- Ogni entità può avere campi di tipo diverso (string, integer, boolean, etc.)
- Supporta relazioni self-referentiali

### Utente Default
Dopo il setup, viene creato un utente di default:
- Email: super.unify@purpleswan.com
- Password: password01!

## Comandi Disponibili

- `setup.py`: Esegue l'intero processo di setup
- `commands/insert_users_entity.py`: Inserisce l'entità Users
- `commands/generate_entity_migrations.py`: Genera le migrazioni per le entità
- `commands/run_migrations.py`: Esegue le migrazioni
- `commands/setup_users.py`: Crea l'utente di default
- `commands/reset_db.py`: Resetta il database allo stato iniziale

## Note
- Assicurati di avere i permessi necessari sul database
- Il reset del database elimina tutte le tabelle tranne `entities`
- Le migrazioni sono gestite tramite Alembic 