# Laufanleitung (Deutsch)

Dieses Archiv enthält nur Keystore/Certificates und eine Beispiel-HTTPS-Serverdatei `server.py`,
die das mitgelieferte `puzscan_cert.pem` und `puzscan_key.pem` verwendet, um einen kleinen HTTPS-Server zu starten.

**Wie starten (lokal, Linux/macOS, Python 3.8+):**

1. Öffne ein Terminal im Verzeichnis dieses Archivs (wo `puzscan_cert.pem` und `puzscan_key.pem` liegen).
2. Mache die Startdatei ausführbar (falls nötig): `chmod +x start.sh`
3. Starte den Server: `./start.sh` oder `./start.sh 8443` um Port 8443 zu verwenden.
4. Öffne im Browser: `https://localhost:4443/` (oder den gewählten Port).
   - Browser warnt eventuell wegen selbstsigniertem Zertifikat — das ist normal für Test-Zertifikate.
5. Zum Stoppen: `Ctrl+C` im Terminal.

**Wichtig:** Dies ist nur ein Demo-/Test-Server. Setze ihn nicht unbeaufsichtigt in Produktionsumgebungen ein.
