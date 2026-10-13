"""CLI: food-company <name> [--country AT] | --vies ATU12345678 | --northdata NAME"""
import argparse, json
from . import registries as r

def main(argv=None):
    p = argparse.ArgumentParser(prog="food company")
    p.add_argument("name", nargs="?")
    p.add_argument("--country")
    p.add_argument("--vies"); p.add_argument("--northdata", action="store_true")
    p.add_argument("--children", help="LEI: list direct children")
    a = p.parse_args(argv)
    if a.vies: out = r.vies_check(a.vies)
    elif a.children: out = r.gleif_children(a.children)
    elif a.northdata: out = r.northdata_page(a.name)
    else: out = r.company(a.name, a.country)
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__": main()
