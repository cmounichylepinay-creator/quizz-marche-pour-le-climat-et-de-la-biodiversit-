"""Les Galets du Climat — prototype Flask avec stockage SQLite partagé."""
import os, json, sqlite3, secrets, csv, io
from pathlib import Path
from datetime import datetime, timezone
from flask import Flask, request, session, redirect, url_for, render_template_string, flash, Response, abort

ROOT=Path(__file__).resolve().parent
QUESTIONS={q['id']:q for q in json.loads((ROOT/'questions.json').read_text(encoding='utf-8'))}
ROUTES={1:('Vert · 2 km',8),2:('Orange · 4 km',16),3:('Bleu · 9 km',36)}
app=Flask(__name__)
app.secret_key=os.getenv('SECRET_KEY','DEMO_CHANGEZ_CETTE_CLE_AVANT_PUBLICATION')
DB=Path(os.getenv('DATABASE_PATH',str(ROOT/'scores.sqlite3')))
ADMIN_KEY=os.getenv('ADMIN_KEY','demo-admin')
CSS='''<style>:root{font-family:system-ui,Segoe UI,Arial,sans-serif;color:#18392f;background:#f2f8f3}*{box-sizing:border-box}body{margin:0}header{background:#176b4a;color:white;padding:22px 18px}header h1{margin:0;font-size:1.6rem}main{max-width:800px;margin:auto;padding:20px 14px 70px}.card{background:white;border:1px solid #d9e8de;border-radius:16px;padding:22px;margin:14px 0;box-shadow:0 3px 12px #143b2410}h2{margin-top:0}label{display:block;margin:12px 0 6px;font-weight:600}input,select{padding:12px;border:1px solid #9db6a7;border-radius:9px;width:100%;font-size:1rem}.btn,button{display:inline-block;border:0;border-radius:10px;background:#18724c;color:white;text-decoration:none;padding:12px 17px;font-weight:700;cursor:pointer;margin:9px 5px 0 0}.secondary{background:#e5f2e9;color:#145b3b}.muted{color:#547263}.pill{display:inline-block;background:#e5f2e9;border-radius:20px;padding:5px 10px;margin:4px}.answer{display:block;padding:12px;border:1px solid #c9ded0;border-radius:10px;margin:8px 0;font-weight:400}.answer input{width:auto;margin-right:9px}.score{font-size:2rem;font-weight:800;color:#176b4a}table{width:100%;border-collapse:collapse}th,td{text-align:left;border-bottom:1px solid #e0e9e2;padding:10px 6px}footer{text-align:center;color:#668074;padding:20px;font-size:.8rem}.alert{background:#fff5da;padding:12px;border-radius:8px}</style>'''
BASE='''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Les Galets du Climat</title>'''+CSS+'''</head><body><header><h1>🌿 Les Galets du Climat</h1><div>Marche pour le climat · Sainte-Suzanne · 14 novembre 2026</div></header><main>{% with messages=get_flashed_messages() %}{% for m in messages %}<div class="alert">{{m}}</div>{% endfor %}{% endwith %}{{content|safe}}</main><footer>Prototype à tester avant la manifestation · Ne pas courir · Respecter le parcours balisé</footer></body></html>'''
def db():
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;return c
def init_db():
 with db() as c:
  c.execute('CREATE TABLE IF NOT EXISTS players (id TEXT PRIMARY KEY, nickname TEXT NOT NULL, route INTEGER NOT NULL, created TEXT NOT NULL)')
  c.execute('CREATE TABLE IF NOT EXISTS answers (player_id TEXT NOT NULL, stone_id INTEGER NOT NULL, chosen INTEGER NOT NULL, correct INTEGER NOT NULL, created TEXT NOT NULL, PRIMARY KEY(player_id,stone_id))')
init_db()
def page(content,**kwargs):return render_template_string(BASE,content=render_template_string(content,**kwargs))
def player():
 pid=session.get('pid')
 if not pid:return None
 with db() as c:return c.execute('SELECT * FROM players WHERE id=?',(pid,)).fetchone()
def stats(pid):
 with db() as c:r=c.execute('SELECT COUNT(*) n, COALESCE(SUM(correct),0) wins FROM answers WHERE player_id=?',(pid,)).fetchone()
 return r['n'],r['wins'],5*r['n']+10*r['wins']
@app.get('/')
def home():
 p=player()
 if p:
  n,w,pts=stats(p['id']);name,maxq=ROUTES[p['route']]
  return page('''<div class="card"><h2>Bienvenue, {{p['nickname']}} !</h2><span class="pill">Parcours {{name}}</span><p class="score">{{pts}} points</p><p>{{n}} galet(s) validé(s) sur {{maxq}} · {{(100*pts/(15*maxq))|round(1)}} % du score maximal</p><p>Scanne le QR code d'un galet trouvé pour répondre à sa question.</p><a class="btn" href="{{url_for('catalogue')}}">Voir les galets (mode test)</a><a class="btn secondary" href="{{url_for('ranking')}}">Classement</a></div><div class="card"><h3>À l'arrivée</h3><p>Présente les galets ramassés à l'équipe organisatrice. Les résultats restent provisoires jusqu'à vérification.</p></div>''',p=p,n=n,pts=pts,maxq=maxq,name=name)
 return page('''<div class="card"><h2>Prêt pour la chasse aux galets ?</h2><p>Inscris un pseudonyme, choisis ton parcours, puis découvre les galets peints par les enfants des quartiers.</p><form method="post" action="{{url_for('register')}}"><label>Pseudonyme</label><input name="nickname" maxlength="30" minlength="2" required placeholder="Ex. : Ti Tangue"><label>Mon itinéraire</label><select name="route"><option value="1">Vert — 2 km — 8 galets</option><option value="2">Orange — 4 km — 16 galets</option><option value="3">Bleu — 9 km — 36 galets</option></select><button>Commencer ma partie</button></form></div><div class="card"><h3>Règles</h3><p>5 points par galet scanné et validé, 10 points supplémentaires si la réponse est juste. Une tentative par galet. Classement général selon le pourcentage de points possibles sur son parcours. Les 5 premiers sont récompensés après vérification.</p></div>''')
@app.post('/inscription')
def register():
 if player():return redirect(url_for('home'))
 nick=request.form.get('nickname','').strip();route=request.form.get('route','')
 if len(nick)<2 or len(nick)>30 or route not in ('1','2','3'):abort(400)
 pid=secrets.token_urlsafe(20)
 with db() as c:c.execute('INSERT INTO players VALUES (?,?,?,?)',(pid,nick,int(route),datetime.now(timezone.utc).isoformat()))
 session['pid']=pid;return redirect(url_for('home'))
@app.get('/galet/<int:sid>')
def stone(sid):
 q=QUESTIONS.get(sid)
 if not q:abort(404)
 p=player()
 if not p:
  flash('Inscris-toi avant de répondre, puis scanne à nouveau le galet.');return redirect(url_for('home'))
 if p['route']!=q['route']:
  return page('<div class="card"><h2>Galet hors parcours</h2><p>Ce galet appartient à un autre itinéraire. Retourne sur ton parcours balisé.</p><a class="btn" href="/">Accueil</a></div>')
 with db() as c:existing=c.execute('SELECT * FROM answers WHERE player_id=? AND stone_id=?',(p['id'],sid)).fetchone()
 return page('''<div class="card"><span class="pill">Galet n° {{'%03d'|format(q['id'])}}</span><span class="pill">{{q['theme']}}</span><h2>{{q['question']}}</h2>{% if existing %}<p><strong>{{'Bonne réponse ! +15 points' if existing['correct'] else 'Réponse incorrecte : +5 points de découverte'}}</strong></p><p>{{q['explanation']}}</p><p class="muted">Ce galet a déjà été comptabilisé pour toi.</p>{% else %}<form method="post" action="{{url_for('answer',sid=q['id'])}}">{% for option in q['options'] %}<label class="answer"><input type="radio" name="choice" value="{{loop.index0}}" required>{{option}}</label>{% endfor %}<button>Valider ma réponse</button></form>{% endif %}<a class="btn secondary" href="/">Mon score</a></div>''',q=q,existing=existing)
@app.post('/galet/<int:sid>/reponse')
def answer(sid):
 p=player();q=QUESTIONS.get(sid)
 if not p:return redirect(url_for('home'))
 if not q or q['route']!=p['route']:abort(404)
 try:chosen=int(request.form.get('choice','-1'))
 except ValueError:abort(400)
 if chosen<0 or chosen>=len(q['options']):abort(400)
 with db() as c:c.execute('INSERT OR IGNORE INTO answers VALUES (?,?,?,?,?)',(p['id'],sid,chosen,int(chosen==q['correct']),datetime.now(timezone.utc).isoformat()))
 return redirect(url_for('stone',sid=sid))
@app.get('/test/galets')
def catalogue():
 p=player()
 if not p:return redirect(url_for('home'))
 qs=[q for q in QUESTIONS.values() if q['route']==p['route']]
 return page('''<div class="card"><h2>Catalogue de test — {{len(qs)}} galets</h2><p class="alert">Cette page sert uniquement aux essais. À masquer le jour de la marche : les participants devront scanner les QR codes physiques.</p>{% for q in qs %}<a class="pill" href="{{url_for('stone',sid=q['id'])}}">Galet {{'%03d'|format(q['id'])}} · {{q['theme']}}</a>{% endfor %}</div>''',qs=qs)
def ranks():
 with db() as c:rows=c.execute('''SELECT p.id,p.nickname,p.route,COUNT(a.stone_id) n,COALESCE(SUM(a.correct),0) wins FROM players p LEFT JOIN answers a ON a.player_id=p.id GROUP BY p.id''').fetchall()
 out=[]
 for r in rows:
  pts=5*r['n']+10*r['wins'];out.append(dict(r)|{'points':pts,'percent':round(100*pts/(15*ROUTES[r['route']][1]),2)})
 return sorted(out,key=lambda r:(-r['percent'],-r['points'],r['created'] if 'created' in r else ''))
@app.get('/classement')
def ranking():
 return page('''<div class="card"><h2>Classement provisoire</h2><p>Les 5 premiers sont indiqués à titre informatif. Contrôle des galets physiques et question bonus en cas d'égalité avant remise des prix.</p><table><tr><th>Rang</th><th>Pseudo</th><th>Parcours</th><th>Score</th></tr>{% for r in rows %}<tr><td>{{loop.index}}{% if loop.index<=5 %} 🏅{% endif %}</td><td>{{r.nickname}}</td><td>{{r.route}}</td><td>{{r.percent}} %</td></tr>{% endfor %}</table></div>''',rows=ranks()[:30])
@app.get('/admin')
def admin():
 if request.args.get('key')!=ADMIN_KEY:abort(403)
 return page('''<div class="card"><h2>Administration — provisoire</h2><p>Classement calculé sur les réponses enregistrées. Vérifier les galets physiques avant de proclamer les 5 gagnants. La question bonus est administrée par les organisateurs.</p><table><tr><th>Rang</th><th>Pseudo</th><th>Parcours</th><th>Galets</th><th>Points</th><th>%</th></tr>{% for r in rows %}<tr><td>{{loop.index}}</td><td>{{r.nickname}}</td><td>{{r.route}}</td><td>{{r.n}}</td><td>{{r.points}}</td><td>{{r.percent}}</td></tr>{% endfor %}</table><a class="btn" href="{{url_for('export',key=key)}}">Exporter CSV</a></div>''',rows=ranks(),key=ADMIN_KEY)
@app.get('/admin/export.csv')
def export():
 if request.args.get('key')!=ADMIN_KEY:abort(403)
 buf=io.StringIO();w=csv.writer(buf,delimiter=';');w.writerow(['Rang','Pseudonyme','Parcours','Galets','Bonnes réponses','Points','Pourcentage'])
 for i,r in enumerate(ranks(),1):w.writerow([i,r['nickname'],r['route'],r['n'],r['wins'],r['points'],r['percent']])
 return Response('\ufeff'+buf.getvalue(),mimetype='text/csv',headers={'Content-Disposition':'attachment; filename=classement_galets.csv'})
if __name__=='__main__':app.run(host='0.0.0.0',port=int(os.getenv('PORT','5000')),debug=False)
