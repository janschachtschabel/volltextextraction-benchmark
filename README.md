# Load Test Tool – Text Extraction Service

Asynchrones Lasttestwerkzeug für REST-APIs, die Volltexte aus Webseiten extrahieren.  
Entwickelt für den [openeduhub text-extraction service](https://text-extraction.staging.openeduhub.net/), verwendbar für jeden kompatiblen Endpunkt.

---

## Was das Tool macht

- Testet alle Kombinationen aus **Methode** (`simple`, `browser`) × **Format** (`txt`, `markdown`)
- Steigert die **gleichzeitigen Requests** stufenweise: 1 → 2 → 4 → 8 → 16
- Klassifiziert Fehler nach Typ (`http_4xx`, `timeout`, `connection`, …)
- Analysiert Fehler-Bodies und geholtes HTML per **Schlagwort-Muster** (Geo-Block, Bot-Detection, Paywall, Cookie-Wall, Login, 404, JS-Pflicht, …)
- Erzeugt **3 Plots** und eine **JSON-Rohdatei** pro Testlauf

---

## Dateien

| Datei | Zweck |
|---|---|
| `loadtest.py` | Hauptskript – Lasttest, Auswertung, Plots |
| `sample_urls.py` | URLs aus einer CSV-Datei samplen → `test_urls.txt` |
| `requirements.txt` | Python-Abhängigkeiten |

---

## Schnellstart

```bash
# 1. Abhängigkeiten installieren
pip install -r requirements.txt

# 2a. Eigene URLs samplen (aus CSV-Datei, siehe unten)
python sample_urls.py

# 2b. Oder: test_urls.txt manuell anlegen (eine URL pro Zeile)
echo "https://example.com" > test_urls.txt

# 3. Test starten
python loadtest.py
```

Ohne `test_urls.txt` verwendet `loadtest.py` die eingebaute Fallback-Liste.

---

## URL-Sample aus CSV erzeugen (`sample_urls.py`)

Das Skript liest eine CSV-Datei und zieht ein diversifiziertes Sample:

```
# Konfiguration oben in sample_urls.py anpassen:
CSV_FILE       = "meine_daten.csv"   # Pfad zur CSV
TARGET_COUNT   = 80                  # Gewünschte Anzahl Test-URLs
MAX_PER_DOMAIN = 2                   # Max. URLs pro Domain
```

**CSV-Format:** Semikolon-getrennt, URL in Spalte `properties.ccm:wwwurl`.  
Für andere Spaltenbezeichnungen die Variable `URL_COLUMN` in `sample_urls.py` anpassen:

```python
URL_COLUMN = "properties.ccm:wwwurl"  # Zeile 17
```

Domains die keine Texte liefern (YouTube, GeoGebra, Lern-Apps, …) werden automatisch gefiltert. Die Filterliste `SKIP_DOMAINS` kann erweitert werden.

---

## Konfiguration (`loadtest.py`)

| Variable | Standard | Bedeutung |
|---|---|---|
| `API_ENDPOINT` | `https://…/from-url` | Ziel-API |
| `METHODS` | `["simple", "browser"]` | Zu testende Methoden |
| `FORMATS` | `["txt", "markdown"]` | Zu testende Ausgabeformate |
| `CONCURRENCY_LEVELS` | `[1, 2, 4, 8, 16]` | Gleichzeitige Requests |
| `REQUEST_TIMEOUT` | `120` s | Timeout pro Request |
| `URL_FILE` | `test_urls.txt` | URL-Eingabedatei |

---

## Ausgabe pro Testlauf

| Datei | Inhalt |
|---|---|
| `loadtest_raw_TIMESTAMP.json` | Alle Einzelergebnisse (URL, Methode, Format, Concurrency, Antwortzeit, Status, Fehler, HTML-Snippet) |
| `loadtest_plot_TIMESTAMP.png` | Antwortzeiten (Mean/P50/P95) + Fehlerrate je Kombination |
| `loadtest_errors_TIMESTAMP.png` | Fehlertypen als Stacked-Bar je Kombination und Concurrency-Level |
| `loadtest_patterns_TIMESTAMP.png` | Schlagwort-Muster-Verteilung je Kombination |

Zusätzlich werden in der Konsole ausgegeben:
- Performance-Tabelle (Mean, P50, P95, Fehler%)
- Fehlerfrequenz-Tabelle
- Pattern-Analyse-Tabelle

---

## Erkannte Fehlermuster

Die automatische Schlagwortanalyse klassifiziert Fehler-Bodies und geholtes HTML in folgende Kategorien:

| Muster | Erkannte Signale |
|---|---|
| `geo_block` | "not available in your country", "your region", "geoblocked" |
| `bot_detected` | captcha, cloudflare, ray id, ddos, "checking your browser" |
| `login_required` | login, "sign in", anmelden, registrieren, "members only" |
| `paywall` | subscription, premium, "jetzt abonnieren", freischalten |
| `js_required` | "enable javascript", "javascript is required", noscript |
| `not_found` | 404, "page not found", "existiert nicht" |
| `cookie_wall` | cookiebanner, "cookies akzeptieren", datenschutzeinstellungen |
| `no_content` | "no text content", "could not extract", "no content found" |
| `timeout` | timeout, "timed out", "504", "connection timed out" |
| `server_error` | 500, 502, 503, "internal server error", "bad gateway" |
| `gone` | 410, "no longer available", "nicht mehr verfügbar" |
| `ssl_error` | "ssl error", "certificate verify failed" |
| `redirect_error` | "too many redirects", "redirect loop" |

---

## Anforderungen

- Python ≥ 3.10
- Pakete: siehe `requirements.txt`

```
aiohttp>=3.9
matplotlib>=3.8
numpy>=1.26
```
