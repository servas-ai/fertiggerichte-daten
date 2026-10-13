import sys,json,urllib.parse,subprocess
for t in sys.argv[1:]:
    u="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url|extmetadata|size&iiurlwidth=1000&format=json&titles="+urllib.parse.quote(t)
    d=json.loads(subprocess.run(["curl","-s","-A","servas-logo-bot/1.0 (Martin-Hausleitner@users.noreply.github.com)",u],capture_output=True,text=True).stdout)
    for p in d["query"]["pages"].values():
        ii=p.get("imageinfo",[{}])[0]; m=ii.get("extmetadata",{})
        print(json.dumps({"title":t,"url":ii.get("url"),"thumb":ii.get("thumburl"),"page":ii.get("descriptionurl"),"license":m.get("LicenseShortName",{}).get("value"),"size":[ii.get("width"),ii.get("height")]},ensure_ascii=False))
