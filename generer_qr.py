import sys, pathlib, csv
import qrcode
if len(sys.argv)!=2 or not sys.argv[1].startswith('https://'):
 print('Usage : python generer_qr.py https://adresse-publique-de-votre-jeu.fr');sys.exit(1)
base=sys.argv[1].rstrip('/');out=pathlib.Path(__file__).parent/'qr_codes';out.mkdir(exist_ok=True)
with (out/'correspondance.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Galet','Parcours','Lien'])
 for i in range(1,61):
  url=f'{base}/galet/{i}';img=qrcode.make(url);img.save(out/f'GAL-{i:03d}.png');w.writerow([f'GAL-{i:03d}',1 if i<=8 else 2 if i<=24 else 3,url])
print('60 QR codes créés dans',out)
