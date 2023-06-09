# Rewe Discounts

Dieses Programm sucht mittels der Rewe-API für einen bestimmten Rewe-Markt die aktuellen
Angebote und schreibt eine Markdown-formatierte Übersichtsliste heraus.

Zur besseren Preisvergleichbarkeit wird der Preis pro Referenzmenge
(z.B. 100 g oder 100 ml) mit ausgegeben. 

Anwendungsbeispiel:
* Sonntags lädt der Server (z.B. Raspberry Pi/Debian) per cron-Job die
neuen Angebote herunter, und speichert sie als Notiz in einer Nextcloud-Instanz
zum komfortablen Abruf per Smartphone.

## Abhängigkeiten (Dependencies)
Die einzige externe Abhängigkeit ist zur Abfrage der Rewe API nötig, und damit Cloudflare die Anfrage durchlässt:
- `$ pip install cloudscraper`

Falls das Programm nicht funktioniert und 403-Fehler wirft (siehe [Issue in Github](https://github.com/foo-git/rewe-discounts/issues/14)), versuche die Version festzulegen:
- `$ pip install --force-reinstall -v "cloudscraper==1.2.69"`

## Verwendung (Usage)

* Aktuelles Release [herunterladen](https://github.com/foo-git/rewe-discounts/releases) bzw. Master-Branch klonen.
* `python3 ./rewe_discounts/rewe_discounts.py` ausführen und Hilfetext durchlesen.
    * Mit `rewe_discounts.py --list-markets PLZ` lässt sich für eine beliebige Postleitzahl (PLZ) eine Marktliste inklusive der Market ID ausgeben lassen.
    * Wähle einen Markt und kopiere die ID, z.B. "562286".
    * Durch `rewe_discounts.py --market-id 562286 --output-file "Angebote Rewe.md"` werden die Angebote des Markets in eine Datei geschrieben. 

Ein Ausschnitt von `Angebote Rewe.md` sieht beispielsweise so aus:
```
# Kochen & Backen
Gültig diese Woche bis Samstag, 30.05.2020

**Barilla Pasta**
- 0.79, 1 kg = 1.58
- versch. Ausformungen, je 500-g-Pckg.

**Knorr Grillsauce**
- 0.65, 100 ml = 0.26
- versch. Sorten, je 250-ml-Fl.

**Erasco Eintopf**
- 1.49, 1 kg = 1.86
- versch. Sorten, je 800-g-Dose

**Mondamin Milchreis im Becher**
- 0.79, 100 g = 1.36
- je 58-g-Becher
```

Es lassen sich bestimmte Produkte auch hervorheben und an erster Stelle der Datei platzieren.
Hierzu wird noch eine Textdatei angelegt, und pro Zeile ein Suchbegriff wie "Nudeln" oder "Joghurt" eingegeben:

`rewe_discounts.py --market-id 562286 --output-file "Angebote Rewe.md" --highlights=highlights.txt`
