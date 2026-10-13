# hourly T16: fill producer for new Leitgeb's rows (Gurkerl label lists brand only) from official register:
# Firmenbuch FN 662213v (https://www.evi.gv.at/f/662213v) + Impressum https://kaerntnernudel.co.at/impressum/
import json
cn=json.load(open('/workspace/fertig/connectors_new.json')); n=0
for r in cn:
    if r.get('added_slot')=='2026-10-13T16' and 'Leitgeb' in r['name'] and not r.get('manufacturer'):
        r['manufacturer']="Leitgeb's Nudelspezialitäten aus dem Metnitztal GmbH, Industriestraße 18, 9360 Friesach"
        r['manufacturer_source']='Firmenbuch FN 662213v (evi.gv.at/f/662213v); kaerntnernudel.co.at/impressum (2026-10-13)'
        n+=1
json.dump(cn,open('/workspace/fertig/connectors_new.json','w'),ensure_ascii=False,indent=1)
print('filled',n)
