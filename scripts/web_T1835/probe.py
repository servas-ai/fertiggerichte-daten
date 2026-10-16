"""Daten-Squad T1835 probe: official website + legal notice for companies without website.
Uses food-connectors impressum.find_imprint (robots.txt respected, no cookies/JS/login, sequential per host).
A domain is accepted only if its legal-notice page carries one of OUR already-verified identifiers
(UID, LEI, FN/HRB number) or the full legal-name core verbatim."""
import sys, json, re, time, csv, concurrent.futures as cf
sys.path.insert(0, "/workspace/food-connectors")
import importlib; I = importlib.import_module("food_connectors.company.impressum")
C = {  # slug -> candidate domains (verification decides, not this list)
 "maresi-austria-gmbh": ["maresi.at"], "pastificio-rana-spa": ["giovannirana.it", "rana.it", "giovannirana.de"],
 "nestle-oesterreich-gmbh": ["nestle.at"], "felix-austria-gesellschaft-mbh": ["felix.at"],
 "alnatura-gmbh": ["alnatura.de"], "ehrmann-gmbh": ["ehrmann.de"], "dm-drogerie-markt-gmbh-co-kg": ["dm.de"],
 "weinbergmaier-gmbh": ["weinbergmaier.at"], "hofmann-menue-manufaktur-gmbh": ["hofmann-menue.de"],
 "berglandmilch-egen": ["berglandmilch.at"], "mpreis-warenvertriebs-gmbh": ["mpreis.at"],
 "mars-austria-og": ["mars.com", "bensoriginal.at"], "molkerei-alois-mueller-gmbh-co-kg": ["muellermilch.de", "landliebe.de"],
 "noem-ag": ["noem.at"], "dr-oetker-gmbh": ["oetker.at"], "kreyenhop-kluge-gmbh-cokg": ["kreyenhopkluge.de", "kreyenhop-kluge.de", "kk-asia.de"],
 "marks-and-spencer-services-sro": ["marksandspencer.cz"], "zott-se-co-kg": ["zott.de"],
 "bertagni-1882-spa": ["bertagni.it", "bertagni1882.it"], "princes-foods-bv": ["princes.nl", "princesfoods.nl"],
 "staudinger-delikatessen-gmbh": ["staudinger.at", "staudinger-delikatessen.at"], "tops-foods": ["topsfoods.be", "tops-foods.com"],
 "adriatic-group-gmbh": ["adriatic-group.at", "adriaticgroup.at"], "barilla-g-e-r-fratelli-societa-per-azioni": ["barilla.com", "barillagroup.com"],
 "biovegan-gmbh": ["biovegan.de"], "dr-schaer-spa": ["schaer.com", "drschaer.com"], "glatz-gmbh": ["glatz.at", "njami.at"],
 "tress-lebensmittel-gmbh-co-kg": ["tressbrueder.de"], "andros-deutschland-gmbh": ["andros.de"],
 "dairy-4-fun-sro": ["dairy4fun.cz"], "danone-deutschland-gmbh": ["danone.de"], "delamaris-doo": ["delamaris.si"],
 "doppelt-sp-z-oo": ["doppelt.pl"], "estyria-naturprodukte-gmbh": ["estyria.at"], "euryza-gmbh": ["euryza.de", "reis-fit.de"],
 "franu-espana-sl": ["franui.com", "franui.es"], "franz-ablinger-co-fleischhauereibetrieb-gesellschaft-mbh": ["ablinger.at", "ablinger-fleisch.at"],
 "greenforce-future-food-ag": ["greenforce.com"], "galana-nv-beldessert": ["galana.be", "galana.com"],
 "la-crepe-de-broceliande-8-rue-pierre-legaultboisgervilly3536": ["lacrepedebroceliande.fr", "crepe-broceliande.fr"],
 "planted-foods-ag": ["eatplanted.com", "planted.ch"], "riso-gallo-spa": ["risogallo.it", "risogallo.com"],
 "riso-scotti-spa": ["risoscotti.it", "risoscotti.com"], "ruegenwalder-muehle-carl-mueller-gmbh-co-kg": ["ruegenwalder.de"],
 "winkelbauer-gmbh": ["winkelbauer.at"], "efko-frischfrucht-und-delikatessen-gmbh": ["efko.at"],
 "followfood-gmbh": ["followfood.de", "followfood.com"], "rewe-international-ag": ["rewe-group.at"],
 "spar-oesterreichische-warenhandels-aktiengesellschaft": ["spar.at"], "unimarkt-gmbh": ["unimarkt.at"],
 "gastrotech": ["gastrotech.cz"],
}
rows = {r["slug"]: r for r in json.load(open("/workspace/fertiggerichte-daten/data/companies.json"))}
def norm(s): return re.sub(r"\s+", " ", (s or "")).lower()
def tokens(r):
    t = []
    if r.get("uid"): t.append(("uid", r["uid"]))
    if r.get("lei"): t.append(("lei", r["lei"]))
    for k in ("fn", "hrb", "register_id"):
        v = (r.get(k) or "").replace("FN ", "").strip()
        if v and len(v) >= 4: t.append((k, v))
    return t
def check(slug):
    r = rows[slug]; res = {"slug": slug, "legal_name": r.get("legal_name"), "tries": []}
    for dom in C[slug]:
        try: url, h = I.find_imprint(dom)
        except Exception as e: res["tries"].append({"domain": dom, "error": str(e)[:100]}); continue
        if not url: res["tries"].append({"domain": dom, "error": "no imprint with ids"}); continue
        t = I._text(h); tc = re.sub(r"[\s.]", "", t).lower(); hits = []
        for k, v in tokens(r):
            if re.sub(r"[\s.]", "", v).lower() in tc: hits.append(k)
        name_hit = I._name_on_page(r.get("legal_name") or r["name"], t)
        vats = sorted({re.sub(r"[\s.]", "", v) for v in I.VAT_RX.findall(t)})
        res["tries"].append({"domain": dom, "imprint_url": url, "id_hits": hits, "name_on_page": name_hit, "vats_on_page": vats,
                             "fn_on_page": sorted({f"FN {a}{b.lower()}" for a, b in I.FN_RX.findall(t)})})
        if hits or name_hit: res["accepted"] = res["tries"][-1]; break
        time.sleep(1)
    return res
out = []
with cf.ThreadPoolExecutor(4) as ex:
    for res in ex.map(check, list(C)):
        out.append(res); a = res.get("accepted")
        print(res["slug"], "->", (a["imprint_url"], a["id_hits"], a["name_on_page"]) if a else [x.get("error") or ("ids?", x.get("vats_on_page")) for x in res["tries"]], flush=True)
json.dump(out, open("/workspace/fertiggerichte-daten/scripts/web_T1835/probe_out.json", "w"), ensure_ascii=False, indent=1)
