import sys, re, subprocess, json, urllib.parse
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
def get(u):
    r=subprocess.run(["curl","-sL","-m","20","-A",UA,"-w","\n__CODE__%{http_code} %{url_effective}",u],capture_output=True,text=True,errors="ignore")
    out=r.stdout; i=out.rfind("\n__CODE__")
    return out[:i], out[i+9:].strip() if i>=0 else ("", "ERR")
for u in sys.argv[1:]:
    html,code=get(u)
    base=code.split(" ",1)[-1]
    rb,rc=get(urllib.parse.urljoin(base,"/robots.txt"))
    dis=[l for l in rb.splitlines() if l.lower().startswith("disallow") ][:6] if rc.startswith("200") else rc
    print("=====",u,"->",code,"| robots:",dis)
    t=re.search(r"<title[^>]*>(.*?)</title>",html,re.S|re.I); print("title:",(t.group(1).strip()[:100] if t else None))
    cands=set()
    for m in re.finditer(r'''(?:src|href|content|data-src|srcset)=["']([^"' ]+)''',html):
        s=m.group(1)
        if re.search(r'logo|brand|\.svg',s,re.I) and not re.search(r'\.(js|css)(\?|$)',s): cands.add(urllib.parse.urljoin(base,s))
    for m in re.finditer(r'og:image["\'][^>]*content=["\']([^"\']+)|content=["\']([^"\']+)["\'][^>]*og:image',html): cands.add("OG "+(m.group(1) or m.group(2)))
    for c in sorted(cands)[:25]: print("  ",c)
    if "<svg" in html.lower():
        n=len(re.findall(r"<svg",html,re.I)); print("  inline svgs:",n)
