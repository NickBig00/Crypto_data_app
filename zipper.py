import zipfile
import os

# Dateipfade
exe_file = r"C:\Users\gross\PycharmProjects\FiverrProjects\cryptoData\dist\crypto_data_app.exe"
requirements_file = r"C:\Users\gross\PycharmProjects\FiverrProjects\cryptoData\requirements.txt"
zip_file = r"C:\Users\gross\PycharmProjects\FiverrProjects\cryptoData\crypto_data_app.zip"

# ZIP-Datei erstellen
with zipfile.ZipFile(zip_file, 'w') as zipf:
    zipf.write(exe_file, os.path.basename(exe_file))
    zipf.write(requirements_file, os.path.basename(requirements_file))

print(f"ZIP-Datei erstellt: {zip_file}")
