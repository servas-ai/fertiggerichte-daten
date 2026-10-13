import json
B='https://www.interspar.at/'
N=None
# id,brand,name,price,weight_g,kcal,prot,fat,sat,carb,sugar,fiber,salt,cat,ident,img
R=[
('145664','Inzersdorfer','Inzersdorfer Rindsgulasch 400 G',6.99,400,110,10,5.5,1.6,4.7,0.9,N,1.1,'Dose','AT 62028 EG','e4/f4/04/1789092037/A_145664_HB.jpg'),
('145701','Inzersdorfer','Inzersdorfer Schweinsgulasch 400 G',5.29,400,123,9.6,7,2.4,5.1,1,N,1.1,'Dose',N,'e3/37/2c/1789092032/A_145701_HB.jpg'),
('145763','Inzersdorfer','Inzersdorfer Bohnen mit Speck 400 G',3.49,400,158,6.1,8,2.7,13,1.2,N,1.2,'Dose',N,'40/de/0f/1789092034/A_145763_HB.jpg'),
('145794','Inzersdorfer','Inzersdorfer Reisfleisch 400 G',5.29,400,181,6.7,7.6,1.9,21,1.1,N,1.2,'Dose',N,'8b/7a/e5/1789092035/A_145794_HB.jpg'),
('145855','Inzersdorfer','Inzersdorfer Weinbeuschel 400 G',3.49,400,83,5.5,4.7,1.1,4.6,0.7,N,1.1,'Dose',N,'3e/a8/49/1789092036/A_145855_HB.jpg'),
('145930','Inzersdorfer','Inzersdorfer Rindsgulasch 2 Portionen 800 G',10.49,800,111,9.7,5.8,1.6,4.7,0.6,N,1.2,'Dose','AT 62028 EG','1f/0d/09/1789092032/A_145930_HB.jpg'),
('147491','Inzersdorfer','Inzersdorfer Würstel in Gulaschsaft 400 G',5.29,400,154,4.7,13,4.8,4.2,0,N,1.4,'Dose','AT 62028 EG','0c/0c/2b/1789092034/A_147491_HB.jpg'),
('152747','Inzersdorfer','Inzersdorfer Ravioli in Tomatensauce 400 G',2.79,400,94,2.1,4,0.9,12,4.3,N,1.4,'Dose',N,'01/b6/a9/1789464892/A_152747_HB.jpg'),
('178426','Inzersdorfer','Inzersdorfer Ravioli in Tomatensauce 2 Portionen 800 G',4.29,800,94,2.1,4,0.9,12,4.3,N,1.4,'Dose','AT 62028 EG','07/92/c5/1789459443/A_178426_HB.jpg'),
('2020000585336','Inzersdorfer','Inzersdorfer Chili con Carne 2 Portionen 800 G',5.49,800,89,4.2,3.7,1.1,8.6,1.9,N,1.3,'Schale/Becher (unbestätigt)','AT 62028 EG','ec/ec/dd/1789085401/A_2020000585336_HB.jpg'),
('2991603','Inzersdorfer','Inzersdorfer Chili con Carne 400 G',3.49,400,94,3.8,4.3,1.4,8.9,2,N,1.3,'Dose','AT 62028 EG','b6/bf/42/1789462245/A_2991603_HB.jpg'),
('2020000961727','Inzersdorfer','Inzersdorfer gelbes Curry mit Huhn 400 G',5.29,400,121,5.3,5.4,1.5,12,6.2,N,1.1,'Fertiggericht','AT 62028 EG','6e/55/5f/1789069655/A_2020000961727_HB.jpg'),
('5246021','Felix','Felix Chili con Carne 400 G',3.49,400,101,5.3,4.3,1.7,8.8,1.8,N,1.2,'Dose','CZ 402 ES','cd/db/88/1789092319/A_5246021_HB.jpg'),
('5274895','Felix','Felix Chili con Carne 800 G',6.49,800,101,5.3,4.3,1.7,8.8,1.8,N,1.2,'Dose','CZ 402 ES','da/8a/3e/1789460051/A_5274895_HB.jpg'),
('7182662','Felix','Felix Höllenfeuer Chili con Carne 800 G',6.49,800,103,5.4,4.4,1.7,8.9,2.1,N,1.0,'Dose','CZ 402 ES','61/b1/71/1789465843/A_7182662_HB.jpg'),
('7442063','S-BUDGET','S-BUDGET Chili con Carne 400 G',2.19,400,93,3.7,5.2,1.5,6.6,1.1,2.4,1.2,'Dose','AT 62028 EU','52/d3/52/1789090551/A_7442063_HB.jpg'),
('5274802','Felix','Felix Erdäpfelgulasch 800 G',6.49,800,104,3.1,6.2,1.5,8.5,1.2,N,1.2,'Dose',N,'92/e2/e4/1789460052/A_5274802_HB.jpg'),
('7181290','Felix','Felix Erdäpfelgulasch 400 G',3.49,400,104,3.1,6.2,1.5,8.6,1.3,N,1.2,'Dose',N,'8a/d4/09/1789465842/A_7181290_HB.jpg'),
('7177651','Felix','Felix Fleischravioli 400 G',3.49,400,84,2.4,2.6,0.5,12,4.1,N,1.1,'Dose','AT 10127 EG','a5/0a/26/1789089445/A_7177651_HB.jpg'),
('2020004338648','Lorado','Lorado Ravioli in Tomatensauce 800 G',2.49,800,76,1.9,0.9,0.3,14,2.5,1.1,0.84,'Fertiggericht (Menge lt. Produktdaten 0,850 kg)',N,'a5/37/b5/1789340689/A_2020004338648_HB.jpg'),
('4971221','SPAR','SPAR Lasagne Bolognese 400 G',2.99,400,133,5.5,4.8,2.2,16,2.9,1.5,0.7,'Fertiggericht','DE BE 20362 EU','aa/ff/43/1789460840/A_4971221_HB.jpg'),
('7842306','S-BUDGET','S-BUDGET Lasagne Bolognese 1 KG',3.99,1000,139,5.8,6.8,2.8,13,2.3,1.4,0.97,'Schale, gekühlt','AT 41586 EG','be/e7/7e/1789090032/G_9100000809281_HB.jpg'),
('2020004350831','DESPAR','DESPAR Lasagne alle verdure 600 G',4.79,600,128,5.4,4.4,2.7,16,3.7,1.4,0.8,'Fertiggericht','IT T5F7C UE','e7/7f/f7/1789340772/G_9100000979823_HB.jpg'),
('2020003990526','Schär','Schär Lasagne glutenfrei 300 G',4.99,300,128,5.2,5.5,2.3,14,2.8,1.5,0.76,'Fertiggericht (Nährwerte pro 100 g, Portion 1)',N,'a6/90/d0/1789076965/A_2020003990526_HB.jpg'),
('2020003170256','DESPAR','DESPAR herzhafte Cannelloni Ricotta & Spinat 600 G',4.79,600,142,6,7.8,3.6,11,4.4,1.7,1.1,'Fertiggericht',N,'18/32/04/1789482645/A_2020003170256_HB.jpg'),
('2020005794535','Little Lunch','Little Lunch Thai Curry Eintopf asiatische Art 350 G',3.49,350,N,N,N,N,N,N,N,N,'Eintopf (keine Nährwerte auf Produktseite)',N,'15/1d/01/1789408723/A_2020005794535_HB.jpg'),
('2020003995460','SPAR PREMIUM','SPAR PREMIUM Edition Johanna Maier Süsskartoffel- Eintopf Vegan 400 G',4.99,400,77,1.8,2.2,0.2,12,7.4,1.3,0.69,'Eintopf, Becher gekühlt',N,'10/70/70/1790174680/G_9100000938493_HB.jpg'),
('2020000747239','Küchenbrüder','Küchenbrüder Veganer Bio Linseneintopf 400 G',4.29,380,80,3.7,2.1,0.3,11,2.2,N,0.61,'Eintopf, Becher gekühlt (Menge lt. Produktdaten 0,380 kg; sat <0,3)',N,'a5/87/98/1789078986/A_2020000747239_HB.jpg'),
('2020005809079','Nabio','Nabio Linseneintopf mit Gemüse 400 G',2.49,400,58,3.1,0.7,0.1,8.2,1.5,3.3,1.1,'Eintopf (sat <0,1)',N,'98/0d/94/1790194942/A_2020005809079_HB.jpg'),
('2020005809192','Nabio','Nabio Erbseneintopf mit Gemüse 400 G',2.49,400,65,3.8,0.8,0.1,9.1,1,3.2,0.8,'Eintopf (sat <0,1)',N,'b8/77/8c/1790189502/A_2020005809192_HB.jpg'),
('2020003995446','SPAR PREMIUM','SPAR PREMIUM Edition Johanna Maier Ratatouille Gemüse-Eintopf Vegan 400 G',3.99,400,58,1.2,3.6,0.5,4.4,3.5,1.3,0.97,'Eintopf, Becher gekühlt',N,'be/b4/52/1789076979/A_2020003995446_HB.jpg'),
('7442131','S-BUDGET','S-BUDGET Gulaschsuppe 400 G',1.55,400,77,3.8,4.2,1.1,5.5,0.4,0.8,1.1,'Suppe/Dose','AT 40676 EU','74/da/55/1789090557/A_7442131_HB.jpg'),
('131995','Inzersdorfer','Inzersdorfer Gulaschsuppe 4 Portionen 800 G',5.79,800,82,3.5,4.2,1,7.2,1.5,N,1.1,'Suppe/Dose','AT 62028 EG','3d/20/c5/1789074363/A_131995_HB.jpg'),
('232104','Inzersdorfer','Inzersdorfer Suppentopf Gulaschsuppe 400 G',2.99,400,82,3.5,4.2,1,7.2,1.5,N,1.1,'Suppe/Dose','AT 62028 EG','dc/9f/cf/1789459499/A_232104_HB.jpg'),
('234481','Inzersdorfer','Inzersdorfer Suppentopf Bohnensuppe 400 G',2.99,400,110,4.5,4.4,1.4,11,1.2,N,1.2,'Suppe/Dose','AT 62028 EG','84/ed/g0/1789459521/A_234481_HB.jpg'),
('234603','Inzersdorfer','Inzersdorfer Suppentopf Leberknödelsuppe mit 4 Knödeln 400 G',2.99,400,85,3.7,5.6,2.3,5,0,N,1.6,'Suppe/Dose','AT 62028 EG','ea/fa/e7/1789459514/A_234603_HB.jpg'),
('2020005546127','Inzersdorfer','Inzersdorfer Wiener Suppentopf 400 G',2.99,400,41,1.9,1.8,0.4,4.1,0.6,N,1.2,'Suppe/Dose','AT 62028 EU','00/09/cb/1789457034/A_2020005546127_HB.jpg'),
('2020001891719','SPAR Natur*pur','SPAR Natur*pur Bio-Gulaschsuppe 370 G',3.29,350,90,4,4.4,1,7.5,3,1.9,1.3,'Suppe (Nährwerte pro 100 ml; Name 370 G, Produktdaten Menge 0,350)',N,'ea/13/29/1789092875/A_2020001891719_HB.jpg'),
('2020005809215','Nabio','Nabio Gulaschsuppe Vegan 400 G',2.99,400,52,2.5,0.8,0.1,7.1,3.5,2.5,1.2,'Suppe (sat <0,1)',N,'00/01/61/1790193519/A_2020005809215_HB.jpg'),
('5577637','Felix','Felix Gulaschsuppe 800 G',6.49,800,80,3.4,4.4,0.8,6.2,2,N,1.3,'Suppe/Dose','CZ 402 ES','04/77/af/1789459124/A_5577637_HB.jpg'),
]
out=[]
for r in R:
    i,b,n,p,w,k,pr,f,s,c,su,fi,sa,cat,idn,img=r
    out.append(dict(name=n,brand=b,price_eur=p,pack_weight_g=w,kcal_per_100g=k,protein_g=pr,fat_g=f,sat_fat_g=s,carbs_g=c,sugar_g=su,fiber_g=fi,salt_g=sa,
      inverkehrsbringer=None,identitaetskennzeichen=idn,category_note=cat,image_url=B+'media/'+img,product_url=B+'p/'+i))
json.dump(out,open('spar_browser_meals.json','w'),ensure_ascii=False,indent=1)
print(len(out)); print(json.dumps(out,ensure_ascii=False,separators=(',',':')))
