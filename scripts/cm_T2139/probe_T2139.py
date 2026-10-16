import json,sys,time
from food_connectors.company.impressum import impressum
from food_connectors.company.registries import gleif_search
C=[("Hartl's Kulinarikum","Andreas Hartl","hartls-kulinarikum.at","AT"),
("Danke Bauer","Roman Fenz e.U.","dankebauer.com","AT"),
("Arche","Arche Naturprodukte GmbH","arche-naturkueche.de","DE"),
("Bioart","BIOART AG","bioart.at","AT"),
("Ökoland","Ökoland GmbH Nord","oekoland.de","DE"),
("Rapunzel","Rapunzel Naturkost GmbH","rapunzel.de","DE"),
("Schenkel","Schenkel Erich GmbH",None,"AT"),
("Petersilchen","Petersilchen GmbH","petersilchen.de","DE"),
("Egesun","EGESUN GmbH & Co. KG","egesun.de","DE"),
("myProduct","myProduct GmbH","myproduct.at","AT")]
out=[]
for brand,name,dom,cc in C:
    r={"brand":brand,"name":name,"domain":dom}
    try: r["gleif"]=gleif_search(name,cc)
    except Exception as e: r["gleif_err"]=str(e)[:100]
    if dom:
        try: r["imp"]=impressum(dom,name)
        except Exception as e: r["imp_err"]=str(e)[:100]
    out.append(r); print(json.dumps(r,ensure_ascii=False,default=str)[:1500],flush=True)
json.dump(out,open('/tmp/probe_T2139.json','w'),ensure_ascii=False,indent=1,default=str)
