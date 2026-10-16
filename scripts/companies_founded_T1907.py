"""Daten-Squad 2026-10-16T1907: company founding date, shareholders (legal entities) and share capital from official registers.
Sources: GLEIF level-1 `entity.creationDate` (legal entity creation), evi.gv.at /f/<FN> (official Austrian Firmenbuch
publication platform; robots allows /f/, /s search never used; 1 req/s), Wikidata (CC0) only via identifier match
(LEI P1278, EU VAT P3608, Firmenbuchnummer P5285 — no name matching). Evidence: raw/companies_founded_2026-10-16T1907.json.
Rules (nothing inferred, never overwrite a filled field):
 * founded = GLEIF creationDate (UTC timestamp of local midnight → local calendar day). If evi.gv.at shows an earlier
   Firmenbuch entry date than GLEIF's creation date, the GLEIF date cannot be the founding → conflict, not taken.
 * else founded = evi.gv.at Eintragungsdatum, but only when ≥ 1996-01-01: entries dated 1991–1995 are the bulk transfer of
   existing companies into the electronic Firmenbuch (FBG 1991), not founding dates → not taken.
 * else Wikidata P571 inception of the identifier-matched item (year precision kept as year).
 * owners (empty only) = shareholders on evi.gv.at that are register entities (linked /f/<FN>); natural persons are counted,
   not named (an unlinked entry counts as an entity only when its name carries a legal form). share_capital / business_line / register_status from evi.gv.at (JSON only).
 * employees (empty only) = Wikidata P1128 with point in time, identifier-matched item."""
import csv, io, json, datetime, re
LEGAL = re.compile(r"(?<!\w)(GmbH|m\.b\.H\.|AG|SE|KG|OG|eGen|B\.V\.|N\.V\.|S\.A\.|AB|Aktiebolag|ApS|Ltd|Limited|Inc|S\.p\.A\.|Societe|Société|Privatstiftung|Holdings?)(?!\w)", re.I)
NOW = "2026-10-16T19:40:00Z"
P = json.load(open("scripts/fe_T1907/probe_out.json")); E = json.load(open("scripts/fe_T1907/evi_out.json"))
F = json.load(open("scripts/fe_T1907/probe_fn_out.json"))
WD = {}
for src in (P["wikidata"], F):
    for s, v in src.items(): WD.setdefault(s, []).extend(v)
def gday(ts):
    t = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return (t + datetime.timedelta(days=1)).date() if t.hour >= 12 else t.date()
def eday(x):
    try: return datetime.datetime.strptime(x, "%d.%m.%Y").date()
    except Exception: return None
d = json.load(open("data/companies.json", encoding="utf-8")); U = {}; CONFLICT = {}; SKIP_OLD = {}
for r in d:
    s = r["slug"]; u = {}; g = P["gleif"].get(s); e = E.get(s) if not (E.get(s) or {}).get("error") else None
    ed = eday(e["eintragungsdatum"]) if e and e.get("eintragungsdatum") else None
    if not (r.get("founded") or "").strip():
        if g and g.get("creationDate"):
            gd = gday(g["creationDate"])
            if ed and ed < gd:
                CONFLICT[s] = f"GLEIF creationDate {gd} later than Firmenbuch entry {ed} (evi.gv.at) → not taken"
            else:
                u["founded"] = gd.isoformat(); u["founded_source"] = f"GLEIF legal entity creation date (LEI {g['lei']})"
        if "founded" not in u and ed:
            if ed >= datetime.date(1996, 1, 1):
                u["founded"] = ed.isoformat(); u["founded_source"] = f"Firmenbuch Eintragungsdatum, evi.gv.at/f/{e['url'].rsplit('/',1)[1]}"
            else: SKIP_OLD[s] = f"evi.gv.at Eintragungsdatum {ed} = FBG-1991 bulk transfer window, not a founding date"
        if "founded" not in u and s in WD and s not in CONFLICT:
            inc = sorted({x["inception"] for x in WD[s] if x.get("inception")})
            if len(inc) == 1:
                u["founded"] = inc[0][:4]; u["founded_source"] = f"Wikidata P571 ({WD[s][0]['item'].rsplit('/',1)[1]}, matched by {WD[s][0]['matched_by']})"
            elif len(inc) > 1: CONFLICT[s] = f"Wikidata P571 has several values {inc} → not taken"
    if e:
        ents = [x["name"] for x in e.get("gesellschafter_links", []) if (x["href"] or "").startswith("/f/") or LEGAL.search(x["name"])]
        cnt = int((e.get("gesellschafter_count") or "0").split()[0] or 0)
        if not (r.get("owners") or "").strip() and cnt:
            nat = cnt - len(ents); parts = ents + ([f"{nat} natürliche Person" + ("en" if nat > 1 else "")] if nat > 0 else [])
            u["owners"] = "; ".join(parts) + " (Gesellschafter lt. Firmenbuch/evi.gv.at)"; u["owners_source"] = e["url"]
        for k, v in (("share_capital", e.get("stammkapital")), ("business_line", e.get("geschaeftszweig")), ("register_status", e.get("status"))):
            if v and not r.get(k): u[k] = v
        if ed: u["register_entry_date"] = ed.isoformat()
    if s in WD and not (r.get("employees") or "").strip():
        em = sorted({(x["emp"], x.get("empTime", "")[:4]) for x in WD[s] if x.get("emp")})
        if len(em) == 1:
            n, y = em[0]; u["employees"] = f"ca. {int(float(n)):,}".replace(",", ".") + (f" ({y}, Wikidata {WD[s][0]['item'].rsplit('/',1)[1]})" if y else "")
    if u: U[s] = u
for r in d:
    if r["slug"] in U:
        for k, v in U[r["slug"]].items():
            if k in ("founded", "owners", "employees") and (r.get(k) or "").strip(): continue
            r[k] = v
        src = [x for x in (E.get(r["slug"], {}).get("url"),) if x and r["slug"] in U]
        if r.get("lei") and "GLEIF" in (U[r["slug"]].get("founded_source") or ""): src.append(f"https://api.gleif.org/api/v1/lei-records/{r['lei']}")
        if "Wikidata" in (U[r["slug"]].get("founded_source", "") + U[r["slug"]].get("employees", "")): src.append(WD[r["slug"]][0]["item"])
        r["sources"] = list(dict.fromkeys((r.get("sources") or []) + src))
open("data/companies.json", "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
J = {r["slug"]: r for r in d}
p = "data/companies.csv"; raw = open(p, encoding="utf-8", newline="").read(); nl = "\r\n" if "\r\n" in raw else "\n"
rows = list(csv.DictReader(io.StringIO(raw))); fields = list(rows[0].keys())
for r in rows:
    if r["slug"] in U:
        for k in fields:
            if k in U[r["slug"]]: r[k] = "" if J[r["slug"]].get(k) is None else str(J[r["slug"]].get(k))
out = io.StringIO(); w = csv.DictWriter(out, fieldnames=fields, lineterminator=nl); w.writeheader(); w.writerows(rows)
open(p, "w", encoding="utf-8", newline="").write(out.getvalue())
json.dump({"run": "Daten-Squad T1907", "generated_at": NOW, "rules": __doc__, "applied": U, "conflicts_not_taken": CONFLICT,
           "evi_pre1996_not_taken": SKIP_OLD, "gleif": P["gleif"], "wikidata": WD, "evi": E},
          open("raw/companies_founded_2026-10-16T1907.json", "w"), ensure_ascii=False, indent=1)
c = lambda k: sum(1 for r in d if (r.get(k) or "").strip())
print("updated", len(U), "| founded", c("founded"), "owners", c("owners"), "employees", c("employees"), "revenue", c("revenue"), "share_capital", c("share_capital"))
print("conflicts", CONFLICT); print("pre1996", len(SKIP_OLD))
