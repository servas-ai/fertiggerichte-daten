# Data Dictionary

Automatisch aus `datapackage.json` + Beschreibungen. Leere Felder = nicht verifiziert.

## companies
Rechtsträger aus GLEIF/Firmenbuch inkl. Konzernmutter

| Feld | Typ | Beschreibung |
|---|---|---|
| slug | string |  |
| name | string |  |
| role | string |  |
| legal_name | string |  |
| lei | string | Legal Entity Identifier (GLEIF) |
| fn | string | Firmenbuchnummer (nur AT, Register RA000017) |
| register_id | string | Registernummer laut GLEIF (FN/HRB/…) |
| register_authority | string |  |
| legal_form_code | string |  |
| country | string |  |
| address | string |  |
| entity_status | string |  |
| parent_direct | string |  |
| parent_ultimate | string | Oberste Konzernmutter laut GLEIF Level 2 |
| founded | string |  |
| owners | string |  |
| employees | string | Mitarbeiter (Text, mit Quelle) |
| revenue | string | Umsatz mit Jahr und Quelle (Text, aus Recherche) |
| website | string |  |
| product_count | integer |  |
| median_price_eur | number |  |
| median_eur_per_10g_protein | number |  |
| fetched_at | string | Abrufdatum des Preises (ISO) |
| brands | string |  |
| chains | string |  |
| plants_count | integer |  |

## establishments
Statistik Austria / ÖVIS Liste zugelassener Betriebe

| Feld | Typ | Beschreibung |
|---|---|---|
| approval_code | string | Identitätskennzeichen AT xxxxx EG/EU |
| company | string |  |
| street | string |  |
| postcode | integer |  |
| town | string |  |
| state | string |  |
| list | string |  |
| source | string |  |

## logos
Logo-Index mit Quelle

| Feld | Typ | Beschreibung |
|---|---|---|
| slug | string |  |
| name | string |  |
| category | string |  |
| file | string |  |
| source_url | string |  |
| brands | string |  |

## nutrition
Nährwerte je 100 g

| Feld | Typ | Beschreibung |
|---|---|---|
| product_id | string | Stabiler Hash aus URL+Name+Kette |
| kcal_100g | number |  |
| protein_100g | number |  |
| fat_100g | number |  |
| saturated_fat_100g | number |  |
| carbs_100g | number |  |
| sugar_100g | number |  |
| fiber_100g | number |  |
| salt_100g | number |  |
| nutri_score | string |  |
| health_score | number | App-eigener Gesundheitsscore 0–100 |
| eur_per_10g_protein | number | Preis-Leistung: € pro 10 g Protein (Packung) |

## prices
Preisbeobachtungen mit fetched_at

| Feld | Typ | Beschreibung |
|---|---|---|
| product_id | string | Stabiler Hash aus URL+Name+Kette |
| chain | string |  |
| price_eur | number |  |
| price_per_kg_eur | number |  |
| price_status | string | live/aktuell bzw. Jahr der Beobachtung |
| fetched_at | string | Abrufdatum des Preises (ISO) |
| price_source | string |  |

## producers
Hersteller mit Werken (ÖVIS-Zulassungscodes)

| Feld | Typ | Beschreibung |
|---|---|---|
| slug | string |  |
| name | string |  |
| website | string |  |
| group | string |  |
| plants | string |  |
| approval_codes | string |  |
| retail_brands | string |  |
| logo | string |  |

## products
Fertiggerichte im österreichischen Handel

| Feld | Typ | Beschreibung |
|---|---|---|
| product_id | string | Stabiler Hash aus URL+Name+Kette |
| name | string |  |
| brand | string |  |
| chain | string |  |
| dish | string |  |
| storage | string |  |
| pack_size_g | number |  |
| producer | string |  |
| origin | string |  |
| bio | boolean |  |
| vegan | boolean |  |
| url | string |  |
| image_url | string |  |
| source | string |  |

## online_mealprep.csv / .json
Produkte von Online-Meal-Prep-Shops (Schema wie products, `store` = `Online: <Shop>`). Preise und Nährwerte direkt aus dem Shop (`price_source`, `nut_source`, `price_date`). Zusätzlich: `eur_per_10g_protein`, `storage`, `shelf_life`, `shipping_eur` (Versand pro Bestellung, nicht pro Gericht), `available`, `nut_flag` (Plausibilitätswarnung). Nur Produkte mit veröffentlichten Nährwerten und Gewicht.

## producer_quality.csv / .json
Qualitätsprofil je Hersteller. JSON: jedes Feld `{value, sources[], confidence: high|medium|low|none}`; `value: null` = nicht gefunden. `quality_score` 0–100 (Kriterien in `method_de`), `potential_score` = Obergrenze bei bestmöglicher Auflösung unbekannter Felder.

## online_providers.json
Online-Anbieter (Firma, Sitz, Lieferung nach Linz, Versandkosten, Lagerung, Quellen, Kennzahlen).
