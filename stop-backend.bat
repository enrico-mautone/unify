@echo off
echo Stopping Unify Backend Services...

echo Stopping Entity Service...
taskkill /FI "WINDOWTITLE eq Unify Entity Service" /F

echo Stopping Auth Service...
taskkill /FI "WINDOWTITLE eq Unify Auth Service" /F

echo All services have been stopped. 