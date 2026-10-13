"""Generate a Frictionless Data Package (datapackage.json) from data/*.csv (types inferred)."""
import csv, json, os, glob
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DESC = {"products":"Fertiggerichte im österreichischen Handel","prices":"Preisbeobachtungen mit fetched_at","nutrition":"Nährwerte je 100 g",
 "producers":"Hersteller mit Werken (ÖVIS-Zulassungscodes)","companies":"Rechtsträger aus GLEIF/Firmenbuch inkl. Konzernmutter",
 "establishments":"Statistik Austria / ÖVIS Liste zugelassener Betriebe","logos":"Logo-Index mit Quelle"}
PK = {"products":"product_id","establishments":"approval_code","logos":"slug","companies":"slug","producers":"slug"}
def typ(vals):
    vals=[v for v in vals if v not in ("",None)]
    if not vals: return "string"
    for t,f in (("integer",int),("number",float)):
        try: [f(v) for v in vals]; return t
        except ValueError: pass
    if set(vals) <= {"True","False"}: return "boolean"
    return "string"
res=[]
for p in sorted(glob.glob(f"{D}/*.csv")):
    n=os.path.basename(p)[:-4]; rows=list(csv.DictReader(open(p)))
    fields=[{"name":k,"type":typ([r[k] for r in rows])} for k in rows[0]]
    s={"fields":fields}
    if n in PK: s["primaryKey"]=PK[n]
    if n in ("prices","nutrition"): s["foreignKeys"]=[{"fields":"product_id","reference":{"resource":"products","fields":"product_id"}}]
    res.append({"name":n,"path":f"data/{n}.csv","format":"csv","encoding":"utf-8","description":DESC.get(n,""),"schema":s})
pkg={"name":"fertiggerichte-daten","title":"Fertiggerichte Österreich – offener Datensatz","licenses":[{"name":"CC-BY-4.0","path":"https://creativecommons.org/licenses/by/4.0/","title":"Eigene Daten"}],
 "sources":[{"title":"Open Food Facts (ODbL)","path":"https://world.openfoodfacts.org"},{"title":"GLEIF (CC0)","path":"https://www.gleif.org"},
  {"title":"Statistik Austria ÖVIS","path":"https://vis.statistik.at"},{"title":"heisse-preise.io","path":"https://heisse-preise.io"},{"title":"Händler-Onlineshops (Billa, Spar, Hofer, Lidl, dm)","path":""}],
 "resources":res}
json.dump(pkg,open(os.path.join(os.path.dirname(D),"datapackage.json"),"w"),ensure_ascii=False,indent=1); print(len(res),"resources")
