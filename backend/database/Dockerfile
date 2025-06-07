# Utilizza l'immagine ufficiale di PostgreSQL
FROM postgres:15-alpine

# Imposta le variabili d'ambiente per l'utente e la password di default
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_DB=unify_db

# Copia lo script di inizializzazione
COPY init.sql /docker-entrypoint-initdb.d/

# Esponi la porta predefinita di PostgreSQL
EXPOSE 5432
