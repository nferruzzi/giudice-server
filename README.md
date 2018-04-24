## Giudice gara server
Per supporto al software contattare l'autore

### Dipendenze
- python3 (testato con la 3.5)
- qt 5.6 con qtSerialPort
- pyQt
- py Bottle v0.12
- py apsw
- pyinstaller 3.1.1 (windows)
- InstallSimple 2.9 (windows)

### Eseguire i tests
- `python3 test_gara.py`

### Convertire la UI in file python
Dal folder `ui`
- `sh pyuic.sh`

### Buildare su windows ###
- `pyinstaller main.spec`
- `installer.spro`