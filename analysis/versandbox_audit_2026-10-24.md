# Versand- & Kochbox-Anbieter Audit (2026-10-24)

## 1. Übersicht & Compliance
- **Geprüfte Anbieter (7):** `Bofrost`, `Löwenanteil`, `Hofmann` (`HOFMANNs`), `HelloFresh`, `Marley Spoon`, `Factor`, `Kochabo`
- **Strikte Regeln eingehalten:**
  - `robots.txt` vor jedem Host-Zugriff geprüft (`HTTP 200` + `text/plain` Voraussetzung; bei SSL-/HTTP-Fehler sofortiger Abbruch für den Host).
  - Rate-Limit `>= 1,22 s` Pause zwischen Requests auf denselben Host (Vorgabe `>= 1,15 s`).
  - Rein öffentlich zugängliche Seiten/Sitemaps/JSON-Endpunkte ohne Login/Captcha-Bypass.

| Anbieter | Zeilen in `data.json` | `rankable` (Main) | `rankableLight` | `rankable_mealkit` | `sold_out` | `dupOf` | `price_date` | `robots.txt` | Live-Befund (2026-10-24) |
|---|---:|---:|---:|---:|---:|---:|---|---|---|
| **Bofrost** (`bofrost`) | 199 | 13 | 22 | 0 | 0 | 0 | `2026-10-14` (144), `2026-10-16` (55) | 200 OK | **199/199** Artikel in aktueller Sitemap (`488` Produkte); **36/36** geprüfte PDPs (alle Ranked/Light + 2 Neuheiten) `HTTP 200`, `InStock`, Preis & Gewicht 100 % identisch. **2 URLs** (`#2951` Thai-Curry, `#3068` Bauerntopf) aus `/shop/neuheiten_48008/` auf kanonische `/shop/<slug>.html`-URL umgezogen (`SC55_VERSANDBOX`). |
| **Löwenanteil** (`Löwenanteil`) | 17 | 0 | 4 | 0 | 0 | 0 | `2026-10-14` (17) | 200 OK | **17/17** Gläser (`570 g`, 2 Portionen à `285 g`) via `/products.json` `HTTP 200`, `available: true`, Preis exakt `9,99 €`. (0 im Haupt-Ranking wegen `< 400 kcal` pro 285-g-Portion; 4 im Light-Ranking `#3123`, `#3126`, `#3131`, `#3132`). |
| **Hofmann** (`HOFMANNs` via `Gurkerl`) | 7 | 0 | 0 | 0 | 0 | 0 | `2026-10-14` (1), `2026-10-16` (6) | `hofmanns-shop.de`: 200 OK; `gurkerl.at`: 200 OK; `hofmann-menue.de`: SSL-Mismatch (gesperrt) | **D2C (`hofmanns-shop.de`):** *„Wichtige Information: Wir versenden leider nicht mehr nach Österreich.“* (nur DE). **Retail (`Gurkerl`):** Alle 7 Zeilen wegen `Gurkerl liefert nicht nach 4020 Linz` vom Ranking ausgeschlossen; Preise & Grammaturen 100 % aktuell (`2/7` aktuell lagernd: `#1706` Rindsgulasch, `#1755` Hähnchen Erdnuss-Tikka; `5/7` temporär `inStock: false`). |
| **HelloFresh** (`HelloFresh`) | 94 (aus 100 in `mealkits_src.json`) | 0 | 0 | 31 | 0 | 0 | `2026-10-13` (94) | 200 OK | **31/31** `rankable_mealkit`-Rezept-URLs liefern `HTTP 200` + valides `Recipe`-JSON-LD (25 davon per `HTTP 308` auf die kanonische Rezept-Archiv-URL); Ab-Preis `4,25 €/Portion` auf `/plans` bestätigt. |
| **Marley Spoon** (`Marley Spoon`) | 0 (80 in `mealkits_2026-10-13.json`) | 0 | 0 | 0 | 0 | 0 | – | 200 OK | `/menu` und `/menu/ready-to-heat` `HTTP 200` (`ab 4,59 €/Portion`, liefert nach 4020 Linz), aber im öffentlichen SSR-HTML/JSON-LD fehlen Nährwerte & Portionsgewichte (`products_in_app: false` in `analysis/online_providers.json`). |
| **Factor** (`Factor`) | 0 | 0 | 0 | 0 | 0 | 0 | – | 200 OK (`factormeals.de`) | `/about/liefergebiete` (`HTTP 200`) bestätigt: Lieferung ausschließlich innerhalb Deutschlands (`delivers_linz: false`, keine AT-Domain). |
| **Kochabo** (`Kochabo`) | 0 | 0 | 0 | 0 | 0 | 0 | – | SSL EOF (gesperrt) | `https://www.kochabo.at/robots.txt` bricht mit `SSLError: UNEXPECTED_EOF_WHILE_READING` ab → Host gemäß strikter Regel als nicht erreichbar/gesperrt behandelt (0 Produkt-Requests). |

---

## 2. Detailbefunde & Umsetzung in `export_app.py` (`SC55_VERSANDBOX`)

### 2.1 Bofrost (`#2951` & `#3068` kanonische Sitemap-URLs)
- Alle 199 `bofrost`-Zeilen in `data.json` sind mit ihrer Artikelnummer in der aktuellen `bofrost.at`-Produkt-Sitemap (`PRODUCT-de-AT-EUR-*.xml`, 488 Produkte) enthalten.
- Zwei Produkte sind aus der temporären Kategorie `/shop/neuheiten_48008/` in den regulären Stamm-Pfad `/shop/` gewandert und leiten per `HTTP 301` um:
  1. **`#2951` (`fu8wimlzwf`, `Thai-Curry`, Art.-Nr. `01283`, `600 g`, `11,79 €`):**
     - Alt: `https://www.bofrost.at/shop/neuheiten_48008/thai-curry_01283.html`
     - Neu (kanonisch): `https://www.bofrost.at/shop/thai-curry_01283.html` (`InStock`, `11,79 €`, `600 g`)
  2. **`#3068` (`ndwygcgf56`, `Bauerntopf`, Art.-Nr. `20550`, `800 g`, `13,79 €`, `pliLight: 22.2`):**
     - Alt: `https://www.bofrost.at/shop/neuheiten_48008/bauerntopf_20550.html`
     - Neu (kanonisch): `https://www.bofrost.at/shop/bauerntopf_20550.html` (`InStock`, `13,79 €`, `800 g`)
- **Hinweis zu namensgleichen Bofrost-Zeilen (`Wiener Schnitzel vom Schwein`):**
  - `#2645` (`9t1w28d0ef`, Art.-Nr. `03562`, `540 g`, `17,49 €`, `/shop/fleisch-gefluegel/fleisch-paniert/wiener-schnitzel-vom-schwein_03562.html`) ist die reine Fleisch-Komponente (`component: true`).
  - `#3069` (`g40k5yoxw4`, Art.-Nr. `20555`, `430 g`, `10,79 €`, `/shop/menues/schlemmer-menues/wiener-schnitzel-vom-schwein_20555.html`) ist das Schlemmer-Menü mit Beilage (`component: false`). Kein Duplikat (`dupOf` bleibt leer).
- **Off-Switch in `export_app.py`:**
  - `SC55_VERSANDBOX=0` bzw. `GOOD_CHOICE_DISABLE_SC55_VERSANDBOX=1` stellt den exakten Vorzustand (`dataVersion: a9e298c0daba`) bit-identisch wieder her.
