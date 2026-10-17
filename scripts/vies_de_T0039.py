"""Daten-Squad T0039 (2026-10-17): re-run DE VIES for the 5 DE UIDs printed on legal notices
(T2139 myProduct producers) that were MS_UNAVAILABLE at T2139/T2203. VIES check-status DE = Available
at 00:58Z; REST ms/DE/vat/<n> returned isValid=true for all 5. Germany's VIES does not disclose
name/address ('---'), so validity only is recorded; identity rests on the legal notice (UID + register no.)."""
import csv, json
EV = json.load(open('raw/vies_de_2026-10-17T0039.json'))
res = {e['vat']: e for e in EV}
NOTE = "VIES valid (DE; name/address not disclosed by DE — identity from legal notice) {ts}"
def patch(r):
    e = res.get(r.get('uid'))
    if not e or not e.get('isValid'): return False
    r['uid_vies_name'] = NOTE.format(ts=e['requestDate'])
    r['uid_vies_address'] = '--- (not disclosed by DE VIES)'
    r['uid_checked_at'] = e['requestDate']
    if r['slug'] == 'petersilchen-gmbh':
        r['registry_status'] = ("verified_vies_impressum (HRB 11924 AG Paderborn + UID DE124612378 on the legal notice; "
                                "UID VIES-valid 2026-10-17T01:04Z; no GLEIF record)")
    if isinstance(r.get('sources'), list) and e['url'] not in r['sources']:
        r['sources'].append(e['url'])
    return True
J = json.load(open('data/companies.json')); n = sum(patch(r) for r in J)
json.dump(J, open('data/companies.json', 'w'), ensure_ascii=False, indent=1)
rows = list(csv.DictReader(open('data/companies.csv'))); f = list(rows[0].keys()); m = sum(patch(r) for r in rows)
w = csv.DictWriter(open('data/companies.csv', 'w', newline=''), fieldnames=f); w.writeheader(); w.writerows(rows)
print('json', n, 'csv', m)
