-- Crea il database unify_db (se non esiste già)
SELECT 'CREATE DATABASE unify_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'unify_db')\gexec

-- Connettiti al database appena creato
\c unify_db

-- Crea l'utente unify_admin con password
CREATE USER unify_admin WITH PASSWORD 'password01!';

-- Assegna i privilegi all'utente
GRANT ALL PRIVILEGES ON DATABASE unify_db TO unify_admin;

-- Crea lo schema pubblico se non esiste
CREATE SCHEMA IF NOT EXISTS public;

-- Assegna i permessi sullo schema all'utente
GRANT ALL ON SCHEMA public TO unify_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO unify_admin;

-- Assicurati che i permessi vengano applicati anche alle tabelle future
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO unify_admin;
