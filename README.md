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

Auf der [Rewe-Seite](https://www.rewe.de/angebote/nationale-angebote/) muss man die PLZ seines bevorzugten Marktes eingeben, z.B. 63773.
Anschließend landet man auf der [Übersichtsseite](https://www.rewe.de/angebote/goldbach/562286/rewe-markt-erlengrund-14/).
Oben rechts auf die Schaltfläche "Kategorie wählen" klicken und die URLs der Kategorien in "urls.txt" speichern. 

INSERT PIC

## Verwendung/Installation

1. `main.py` herunterladen
1. Die Datei `urls.txt` im selben Verzeichnis anlegen und pro Zeile eine URL eintragen, z.B. `https://www.rewe.de/angebote/kuehlung/c19/goldbach/562286/rewe-markt-erlengrund-14/`
1. `python3 main.py` ausführen
1. Die Angebote werden dann im selben Verzeichnis in `Angebote Rewe.md` geschrieben

## Hinweise zur Automatisierung

Für Headless-Server muss ein Dummy-Monitor eingerichtet werden.

Für Debian-Systeme: `sudo apt install xserver-xorg-video-dummy`
