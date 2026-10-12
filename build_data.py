import json,re,random
from docx import Document
p=Document('/mnt/data/Fiche_action_Galets_du_Climat_2026.docx')
lines=[x.text for x in p.paragraphs if 'Réponse attendue' in x.text]
themes=['Eau']*10+['Déchets']*10+['Océan']*10+['Biodiversité']*10+['Énergie']*10+['Climat']*10
pools={
'Eau':['Laisser couler l’eau','Un arrosoir','Jeter les déchets dans la ravine','Un bain prolongé','De l’eau non traitée','À midi en plein soleil'],
'Déchets':['Jeter dans la nature','Tout brûler','Utiliser un objet jetable','Les abandonner sur la plage','Les enfouir dans le sable','Les mélanger sans trier'],
'Océan':['Les toucher','Les déranger','Laisser les déchets','Marcher sur les coraux','Les ramasser pour les emporter','Ignorer les pollutions'],
'Biodiversité':['Les déranger','Les capturer','Détruire leur habitat','Introduire des espèces envahissantes','Nourrir les animaux sauvages','Abîmer les nids'],
'Énergie':['Laisser la lumière allumée','La voiture individuelle','Du pétrole','Une ampoule à incandescence','Laisser les appareils inutilisés allumés','Tout jeter'],
'Climat':['Uniquement les scientifiques','La météo d’un seul jour','Les émissions n’ont aucun effet','Supprimer tous les arbres','La voiture pour chaque court trajet','Personne']}
items=[]
for i,line in enumerate(lines):
 q,a=re.split(r'\s+— Réponse attendue :\s+',line,1)
 if a in ('Oui','Non'):
  opts=['Oui','Non']; correct=opts.index(a)
 else:
  distract=[v for v in pools[themes[i]] if v.lower()!=a.lower()]
  rng=random.Random(i+44);opts=[a]+rng.sample(distract,2);rng.shuffle(opts);correct=opts.index(a)
 items.append({'id':i+1,'route':1 if i<8 else 2 if i<24 else 3,'theme':themes[i],'question':q,'options':opts,'correct':correct,'explanation':f'Réponse attendue : {a}.'})
with open('/mnt/data/galets_climat_app/questions.json','w',encoding='utf-8') as f:json.dump(items,f,ensure_ascii=False,indent=2)
print('questions',len(items))
