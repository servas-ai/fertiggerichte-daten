# Fertiggerichte Österreich – offener Datensatz

Rohdaten hinter [fertiggerichte-vergleich](https://servas-ai.github.io/fertiggerichte-vergleich/): Fertiggerichte im österreichischen Lebensmittelhandel (Billa, Spar, Hofer, Lidl, Penny, dm), Preise mit Abrufdatum, Nährwerte, Hersteller, Rechtsträger (GLEIF/Firmenbuch), zugelassene Betriebe (ÖVIS) und Logo-Index.

| Tabelle | Datei | Inhalt |
|---|---|---|
| products | `data/products.csv/.json` | Produkt-Stammdaten |
| prices | `data/prices.csv/.json` | Preis, €/kg, `fetched_at`, Quelle |
| nutrition | `data/nutrition.csv/.json` | Nährwerte je 100 g, Nutri-Score, €/10 g Protein |
| producers | `data/producers.csv/.json` | Hersteller, Werke, Zulassungscodes |
| companies | `data/companies.csv/.json` | Rechtsträger: LEI, FN, Adresse, Konzernmutter, Umsatz/Mitarbeiter (mit Quelle) |
| establishments | `data/establishments.csv/.json` | Statistik Austria/ÖVIS Liste zugelassener Betriebe |
| brand_tree | `data/brand_tree.json` | Hersteller → Marke → Kette |
| logos | `data/logos.csv/.json` | Logo-Index mit Quell-URL |

Schema: [`datapackage.json`](datapackage.json) (Frictionless). Feldbeschreibung: [DATA_DICTIONARY.md](DATA_DICTIONARY.md). Regeln: [DATA_GUIDELINES.md](DATA_GUIDELINES.md).

```bash
python3 scripts/export.py            # aus der App neu exportieren
python3 scripts/companies_enrich.py  # Firmendaten (GLEIF, Parents) auffrischen, ~5 min
python3 scripts/datapackage.py && python3 scripts/validate.py
pip install git+https://github.com/servas-ai/food-connectors && food company "GMS GOURMET GmbH"   # Registry-Lookup jetzt in servas-ai/food-connectors (CLI `food company`, MCP `food-mcp`)
```

Lizenz: eigene Daten **CC BY 4.0**; Teile aus Open Food Facts unterliegen **ODbL 1.0**, GLEIF-Daten CC0. Siehe DATA_GUIDELINES.md.

Credits: GLEIF API, EU VIES, Statistik Austria ÖVIS, Open Food Facts, heisse-preise.io; Ideen aus [p-meier/northdata-connectors](https://github.com/p-meier/northdata-connectors) und [Lukhers-dev/firmenbuch-HVD](https://github.com/Lukhers-dev/firmenbuch-HVD).

## Externe Datensätze (importiert 2026-10-13)
- `data/off_ready_meals_at.csv`: Fertiggerichte aus Open Food Facts (Österreich), via `food fetch --store off`. Lizenz ODbL / DbCL, © Open Food Facts contributors. Keine Preise.
- `data/external_datasets.csv`: kuratierter Katalog offener Datensätze (Hugging Face, Kaggle, Zenodo, data.gv.at, BLS, CIQUAL, USDA, Swiss FCDB) mit Lizenz, Größe und Aktualität. Live-Suche: `food datasets --search "…"`.
