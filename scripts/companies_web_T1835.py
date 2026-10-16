"""Daten-Squad 2026-10-16T1835: company master data — official website, legal-notice URL, registered address (DE rows)
and VAT ids printed on the company's own legal notice.
Sources: the companies' public legal notices (food-connectors impressum.find_imprint: robots.txt respected, no cookies/JS/login,
<=1 req/s), EU VIES REST. Evidence: raw/companies_web_2026-10-16T1835.json (probe + verify passes).
Acceptance rules (nothing inferred):
 * website/imprint_url: the legal-notice page on that domain carries one of the identifiers ALREADY verified for the row
   (LEI, FN, HRB/HRA, national register no.) — Ehrmann is the one group case (page = Ehrmann SE at the identical registered
   street address; website set with website_basis, no UID taken).
 * uid: printed on that page AND VIES valid AND (VIES name match 1.0 for AT/IT, or — DE VIES returns no name — the full
   legal name is printed on the page).
 * address (DE rows with UID but no address; DE VIES returns none): first postal address under the legal name on the
   row's own imprint_url page. Lotao skipped (legal notice now names Bio-Zentrale Naturprodukte GmbH), Kikkoman fetch failed."""
import csv, io, json
NOW = "2026-10-16T18:58:00Z"
V = json.load(open("scripts/web_T1835/verify_out.json"))
WEB_ONLY_PROBE = {"adriatic-group-gmbh": ("https://adriaticgroup.at", "https://adriaticgroup.at/de/impressum", "probe: FN + legal name on page (verify re-fetch timed out)"),
                  "spar-oesterreichische-warenhandels-aktiengesellschaft": ("https://spar.at", "https://spar.at/impressum.html", "probe: FN on page (verify re-fetch timed out)")}
REJECT = {"glatz-gmbh": "glatz.at/impressum-gruppe names Glatz Unternehmensgruppe GmbH (VIES ATU39297505, name match 0.5), no Glatz GmbH identifier/address → not taken"}
U = {}
for s, r in V.items():
    if s in REJECT or r.get("error"): continue
    u = {}
    if r["id_hits"]:
        u.update(website=r["website"], imprint_url=r["imprint_url"], website_basis="own legal notice carries " + ", ".join(f"{k}={v}" for k, v in r["id_hits"].items()))
    elif s == "ehrmann-gmbh" and r["street_on_page"] and r["postcode_on_page"]:
        u.update(website=r["website"], website_basis="group site: legal notice = EHRMANN SE (HRB 18947 AG Memmingen) at the identical registered address A.-Ehrmann-Straße 2, 87770 Oberschönegg; Ehrmann GmbH itself not named → no UID taken")
    for x in r.get("vies", []):
        if not x.get("valid"): continue
        ok = (x.get("name_match") == 1.0) or (x["uid"].startswith("DE") and not x.get("vies_name") and r["name_on_page"] and r["id_hits"])
        if ok and s != "ehrmann-gmbh":
            u.update(uid=x["uid"], uid_vies_name=x.get("vies_name") or "--- (DE VIES returns no name; legal name + register no. printed on the legal notice)",
                     uid_vies_address=(x.get("vies_address") or "").replace("\n", ", ") or "--- (DE VIES returns no address)",
                     uid_checked_at=x.get("checked_at") or NOW, uid_source="own legal notice + EU VIES (T1835)")
            break
    if u: U[s] = u
for s, (w, i, b) in WEB_ONLY_PROBE.items(): U[s] = dict(website=w, imprint_url=i, website_basis=b)
ADDR = {"frosta-tiefkuehlkost-gmbh": "Am Lunedeich 116, 27572 Bremerhaven, DE", "allos-hof-manufaktur-gmbh": "Hoerneckestraße 39, 28217 Bremen, DE",
 "frosta-ag": "Am Lunedeich 116, 27572 Bremerhaven, DE", "youcook-gmbh": "Statthalterhofweg 71, 50858 Köln, DE",
 "iglo-gmbh": "Osterbekstraße 90c, 22083 Hamburg, DE", "heiderbeck": "Gewerbering 4, 82140 Olching, DE",
 "landliebe-gmbh": "Zollerstraße 7, 86850 Fischach, DE", "hamker-vertriebsgesellschaft-mbh": "Heinrich-Hamker-Straße 20, 49152 Bad Essen, DE",
 "hammermuehle-gmbh": "Hauptstrasse 181, 67489 Kirrweiler, DE", "plant-based-power-gmbh": "Hauptstraße 41, 83395 Freilassing, DE",
 "biogourmet-gmbh": "Ochsenweg 1, 71729 Erdmannhausen, DE", "kontakt-everygmbh": "Ritterstraße 9–10, 10969 Berlin, DE",
 "meica-gmbh": "Meicastraße 6, 26188 Edewecht, DE", "planted-foods-gmbh": "Birkenstr. 22, 10559 Berlin, DE",
 "rila-die-genussentdecker": "Hinterm Teich 5, 32351 Stemwede-Levern, DE", "whollees-gmbh": "Lippmannstr. 8, 22769 Hamburg, DE",
 "zum-dorfkrug-produktions-und-handelsgesellschaft-mbh-co-kg": "Rudolf-Diesel-Str. 6-10, 21629 Neu Wulmstorf, DE"}
for s, a in ADDR.items(): U.setdefault(s, {}).update(address=a, address_source="own legal notice (imprint_url), T1835")
p = "data/companies.json"; raw = open(p, encoding="utf-8").read(); d = json.loads(raw)
for r in d:
    if r["slug"] in U:
        for k, v in U[r["slug"]].items():
            if k in ("website", "imprint_url", "address", "uid") and r.get(k): continue  # never overwrite
            r[k] = v
        src = [x for x in (U[r["slug"]].get("imprint_url"), r.get("imprint_url")) if x]
        r["sources"] = list(dict.fromkeys((r.get("sources") or []) + src))
open(p, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1) + ("\n" if raw.endswith("\n") else ""))
J = {r["slug"]: r for r in d}
p = "data/companies.csv"; raw = open(p, encoding="utf-8", newline="").read(); nl = "\r\n" if "\r\n" in raw else "\n"
rows = list(csv.DictReader(io.StringIO(raw))); fields = list(rows[0].keys())
for r in rows:
    if r["slug"] in U:
        for k in fields:
            if k in U[r["slug"]]: r[k] = "" if J[r["slug"]].get(k) is None else str(J[r["slug"]].get(k))
out = io.StringIO(); w = csv.DictWriter(out, fieldnames=fields, lineterminator=nl); w.writeheader(); w.writerows(rows)
open(p, "w", encoding="utf-8", newline="").write(out.getvalue())
ev = {"run": "Daten-Squad T1835", "generated_at": NOW, "rules": __doc__, "applied": U, "rejected": REJECT,
      "verify": V, "probe_log_part1": open("scripts/web_T1835/probe_part1.log").read().splitlines(),
      "probe_log_part2": open("scripts/web_T1835/probe2.log").read().splitlines(),
      "address_candidates": json.load(open("scripts/web_T1835/addr_out.json")),
      "manual_checks": {"oetker.at/impressum": "curl: ATU 26533105 + FN 115931 m on page (= row FN)",
                        "felix.at / berglandmilch.at / dm.de impressum": "client-side rendered, no ids in HTML → not taken",
                        "nestle.at": "HTTP 403 (bot protection, not bypassed)", "hofmann-menue.de": "HTTP 500 / timeout",
                        "lotao.com legal notice": "names Bio-Zentrale Naturprodukte GmbH, not LPP Lotao → address not taken"}}
json.dump(ev, open("raw/companies_web_2026-10-16T1835.json", "w"), ensure_ascii=False, indent=1)
print("updated", len(U))
