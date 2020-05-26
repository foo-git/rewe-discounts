# Rewe Angebots-Scraper

Dieses Programm durchsucht die Rewe-Angebotsseiten und schreibt eine Markdown-formatierte Übersichtsliste heraus.

Zur besseren Preisvergleichbarkeit wird der Preis pro 100 g/100 ml mit ausgegeben. 

Anwendungsbeispiel:
* Sonntags lädt der Server (z.B. Raspberry Pi/Debian) per cron-Job die neuen Angebote herunter, und speichert sie als Notiz in einer Nextcloud-Instanz zum komfortablen Abruf.

## Abhängigkeiten

- `$ pip install selenium bs4 lxml`
- [geckodriver](https://github.com/mozilla/geckodriver/releases) herunterladen und in PATH verfügbar machen, z.B. in `/usr/bin/geckodriver` 

Es kann auch ein anderer Browser als Firefox verwendet werden, hierzu auf [selenium-docs](https://www.selenium.dev/documentation/en/webdriver/driver_requirements/) nachschauen.
Dann muss aber auch in der `main.py` der webdriver-Aufruf angepasst werden.

## Wie komme ich an die URLs?

Auf der [Rewe-Seite](https://www.rewe.de/angebote/nationale-angebote/) muss man die PLZ seines bevorzugten Marktes eingeben, z.B. 63773:
![grafik](https://user-images.githubusercontent.com/53096886/82885025-17861380-9f34-11ea-9e00-3a0428db3f8e.png)

Anschließend landet man auf der [Übersichtsseite](https://www.rewe.de/angebote/goldbach/562286/rewe-markt-erlengrund-14/):
![grafik](https://user-images.githubusercontent.com/53096886/82884898-edccec80-9f33-11ea-8947-26ea9b75eb96.png)

Oben rechts auf die Schaltfläche "Kategorie wählen" klicken und alle URLs der Kategorien in "urls.txt" speichern, z.B.
`https://www.rewe.de/angebote/kuehlung/c19/goldbach/562286/rewe-markt-erlengrund-14/` 


## Verwendung/Installation

1. `main.py` herunterladen und ausführbar machen (`chmod +x main.py`)
1. Die Datei `urls.txt` im selben Verzeichnis anlegen und pro Zeile eine URL eintragen, z.B. `https://www.rewe.de/angebote/kuehlung/c19/goldbach/562286/rewe-markt-erlengrund-14/`
1. `python3 main.py` ausführen
1. Die Angebote werden dann im selben Verzeichnis in `Angebote Rewe.md` geschrieben

## Hinweise zur Automatisierung (Debian)

Für Headless-Server muss zuerst noch ein Dummy-Monitor eingerichtet werden, damit Firefox erfolgreich gestartet werden kann.

`sudo apt install xserver-xorg-video-dummy`

Anschließend muss die X-Konfigurationsdatei `dummy-1920x1080.conf` erstellt werden:

````
Section "Monitor"
  Identifier "Monitor0"
  HorizSync 28.0-80.0
  VertRefresh 48.0-75.0
  # https://arachnoid.com/modelines/
  # 1920x1080 @ 60.00 Hz (GTF) hsync: 67.08 kHz; pclk: 172.80 MHz
  Modeline "1920x1080_60.00" 172.80 1920 2040 2248 2576 1080 1081 1084 1118 -HSync +Vsync
EndSection

Section "Device"
  Identifier "Card0"
  Driver "dummy"
  VideoRam 256000
EndSection

Section "Screen"
  DefaultDepth 24
  Identifier "Screen0"
  Device "Card0"
  Monitor "Monitor0"
  SubSection "Display"
    Depth 24
    Modes "1920x1080_60.00"
  EndSubSection
EndSection
````


Nun kann man den X-Server starten, welcher (vermutlich) dann auf DISPLAY=:0 läuft:

`sudo X -config dummy-1920x1080.conf`


Damit das Programm automatisch ausgeführt werden kann, muss noch ein Cron-Job angelegt werden.
In der Datei könnte man gleich auch noch einen Kopierbefehl einfügen, wenn man die Datei woanders (z.B. Nextcloud) benötigt.

Hierzu das Shellskript `/etc/cron.daily/rewe_scraper` erstellen und folgendes einfügen:
````
#!/bin/bash
USER=foo
PATH_TO_PROGRAM="main.py"
LOGFILE=/tmp/rewe.log
su -c "cd /tmp/; DISPLAY=:0 $PATH_TO_PROGRAM" "$USER" 2>&1 | tee -a "$LOGFILE"
````

Da von geckodriver ein Logfile angelegt wird, muss in ein schreibbares Verzeichnis (/tmp/) gewechselt werden.
Zusätzlich dazu gibt es noch ein eigenes Logfile für den Rewe-Angebots-Scraper.