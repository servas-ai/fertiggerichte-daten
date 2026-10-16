# Data Dictionary

Automatisch aus `datapackage.json` + Beschreibungen. Leere Felder = nicht verifiziert.

## companies
Rechtsträger aus GLEIF/Firmenbuch inkl. Konzernmutter; ergänzt um FN/UID aus öffentlichen Impressen (UID via EU VIES geprüft, Evidenz `raw/impressum_vies_*.json`)

| Feld | Typ | Beschreibung |
|---|---|---|
| slug | string |  |
| name | string |  |
| role | string |  |
| legal_name | string |  |
| lei | string | Legal Entity Identifier (GLEIF) |
| fn | string | Firmenbuchnummer (nur AT, Register RA000017) |
| register_id | string |  |
| register_authority | string |  |
| legal_form_code | string |  |
| country | string |  |
| address | string |  |
| entity_status | string |  |
| parent_direct | string |  |
| parent_ultimate | string | Oberste Konzernmutter laut GLEIF Level 2 |
| founded | string | Gründung: ISO-Datum des Rechtsträgers (GLEIF creationDate bzw. Firmenbuch-Eintragung ab 1996) oder Jahr/Freitext; Basis in JSON `founded_source` |
| owners | string | Gesellschafter: Rechtsträger namentlich, natürliche Personen nur gezählt (evi.gv.at/Firmenbuch; JSON `owners_source`) |
| employees | string |  |
| revenue | string |  |
| website | string |  |
| product_count | integer |  |
| median_price_eur | number |  |
| median_eur_per_10g_protein | number |  |
| fetched_at | string | Abrufdatum (ISO) |
| brands | string |  |
| chains | string |  |
| plants_count | integer |  |
| uid | string | EU-UID/VAT-Nr. aus dem Impressum, live via EU VIES geprüft (gültig + Name passt) |
| uid_vies_name | string | In VIES registrierter Name (AT; DE liefert keinen Namen) |
| uid_vies_address | string | In VIES registrierte Adresse |
| uid_checked_at | string | Zeitpunkt der VIES-Prüfung |
| imprint_url | string | Quelle: Impressum/Offenlegung der Firma |
| register_court | string | Firmenbuch-/Registergericht laut Impressum |
| hrb | string | Deutsche Handelsregisternummer laut Impressum |
| registry_status | string | verified_gleif | verified_gleif+vies | verified_vies_imprint | fn_from_imprint | not_found_in_gleif |
| founded_source (JSON) | string | Quelle für `founded` (GLEIF LEI, evi.gv.at/f/<FN> oder Wikidata-QID mit Identifier-Match) |
| owners_source (JSON) | string | evi.gv.at-Seite der Gesellschafter-Angabe |
| share_capital (JSON) | string | Stammkapital/Grundkapital lt. Firmenbuch (evi.gv.at) |
| business_line (JSON) | string | Geschäftszweig lt. Firmenbuch (evi.gv.at) |
| register_status (JSON) | string | Firmenbuch-Status lt. evi.gv.at (z. B. Eingetragen) |
| register_entry_date (JSON) | string | Eintragungsdatum lt. evi.gv.at (vor 1996 = FBG-1991-Übernahme, kein Gründungsdatum) |

## establishments
Statistik Austria / ÖVIS Liste zugelassener Betriebe

| Feld | Typ | Beschreibung |
|---|---|---|
| approval_code | string |  |
| company | string |  |
| street | string |  |
| postcode | integer |  |
| town | string |  |
| state | string |  |
| list | string |  |
| source | string | Datenquelle / Lizenzhinweis |

## external_datasets
Externe offene Datensätze (Katalog)

| Feld | Typ | Beschreibung |
|---|---|---|
| id | string |  |
| name | string |  |
| url | string |  |
| license | string |  |
| size | string |  |
| freshness | string |  |
| use | string |  |

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

## off_ready_meals_at


| Feld | Typ | Beschreibung |
|---|---|---|
| ean | integer |  |
| name | string |  |
| brand | string |  |
| category | string |  |
| size_g | number |  |
| kcal | number |  |
| protein | number |  |
| fat | number |  |
| satfat | number |  |
| carbs | number |  |
| sugar | number |  |
| fiber | number |  |
| salt | number |  |
| producer_id | string |  |
| image_url | string |  |
| source_url | string |  |
| fetched_at | string | Abrufdatum (ISO) |

## online_mealprep
Online-Meal-Prep Anbieter und Gerichte

| Feld | Typ | Beschreibung |
|---|---|---|
| name | string |  |
| brand | string |  |
| store | string |  |
| price_eur | number |  |
| size_g | number |  |
| price_per_kg | number |  |
| url | string |  |
| image_url | string |  |
| kcal_100 | number |  |
| protein_100 | number |  |
| fat_100 | number |  |
| satfat_100 | number |  |
| carbs_100 | number |  |
| sugar_100 | number |  |
| fiber_100 | number |  |
| salt_100 | number |  |
| protein_pack | number |  |
| kcal_pack | integer |  |
| eur_per_10g_protein | number | Preis-Leistung: € pro 10 g Protein (Packung) |
| nutriscore | string |  |
| manufacturer | string |  |
| producer_id | string |  |
| origin | string |  |
| bio | boolean |  |
| veg | string |  |
| prep | string |  |
| instantpot | string |  |
| category | string |  |
| price_source | string |  |
| price_date | string |  |
| nut_source | string |  |
| packaging | string |  |
| online | boolean |  |
| available | boolean |  |
| storage | string |  |
| shelf_life | string |  |
| shipping_eur | number |  |
| nut_flag | string |  |

## prices
Preisbeobachtungen mit fetched_at

| Feld | Typ | Beschreibung |
|---|---|---|
| product_id | string | Stabiler Hash aus URL+Name+Kette |
| chain | string | Handelsketten-Label |
| price_eur | number |  |
| price_per_kg_eur | number |  |
| price_status | string |  |
| fetched_at | string | Abrufdatum (ISO) |
| price_source | string |  |

## producer_quality
Hersteller-Qualitätsrecherche

| Feld | Typ | Beschreibung |
|---|---|---|
| slug | string |  |
| name | string |  |
| plant | string |  |
| quality_score | integer |  |
| potential_score | integer |  |
| certification | string |  |
| cert_confidence | string |  |
| other_certs | string |  |
| sourcing | string |  |
| sourcing_confidence | string |  |
| technology | string |  |
| recalls | string |  |
| sources | string |  |

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
| chain | string | Handelsketten-Label |
| dish | string |  |
| storage | string |  |
| pack_size_g | number |  |
| producer | string |  |
| origin | string |  |
| bio | boolean |  |
| vegan | boolean |  |
| url | string |  |
| image_url | string |  |
| source | string | Datenquelle / Lizenzhinweis |

## stores
Filialen Linz+Umland (OpenStreetMap Overpass, ODbL)

| Feld | Typ | Beschreibung |
|---|---|---|
| osm_type | string | OSM Elementtyp (node/way) |
| osm_id | integer | OSM ID |
| chain | string | Handelsketten-Label |
| name | string |  |
| street | string |  |
| housenumber | string |  |
| postcode | integer |  |
| city | string |  |
| lat | number | Breitengrad |
| lon | number | Längengrad |
| opening_hours | string | OSM opening_hours |
| brand_wikidata | string | Wikidata-ID der Marke |
| source | string | Datenquelle / Lizenzhinweis |
| fetched_at | string | Abrufdatum (ISO) |
