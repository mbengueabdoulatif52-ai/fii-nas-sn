import os
import sys,subprocess,time,json,datetime,random;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import stub
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8786'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
random.seed(1);T=datetime.date.today();st={}
P=['Transport','Alimentation','Loisirs','Divers','Santé']
for i in range(4000):
    d=T-datetime.timedelta(days=random.randint(0,1100))
    st['users/u1/transactions/t%d'%i]={'amt':random.randint(2,200)*100,'date':d.isoformat(),'cat':'Dépenses variables','poste':random.choice(P),'cmt':random.choice(['bus','yango','marché','']),'compte':random.choice(['wv','es']),'ts':d.isoformat()+'T10:00:00Z'}
bud={}
for k in range(36):
    y,m=T.year,T.month-k
    while m<1:m+=12;y-=1
    bud['%d-%02d'%(y,m)]={p:30000 for p in P}
st['users/u1/data/settings']={'cats':{'Revenu':['Salaire'],'Dépenses variables':P},'budget':bud,'custom':{},'modules':{'comptes':True,'dettes':True,'objectifs':True},'comptes':[{'id':'wv','nom':'Wave','type':'wave','solde0':500000},{'id':'es','nom':'Espèces','type':'especes','solde0':50000}]}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':390,'height':800},service_workers='block').new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    for k,v in [('**/firebase-app.js',stub.APP),('**/firebase-auth.js',stub.AUTH),('**/firebase-firestore.js',stub.FS(json.dumps(st)))]:pg.route(k,(lambda v: lambda r: r.fulfill(body=v,content_type='text/javascript'))(v))
    pg.route('https://fonts.**',lambda r:r.abort());pg.goto('http://localhost:8786/');pg.wait_for_timeout(2500)
    for name,js in [('accueil',"renderDash()"),('historique mois',"goP('tx',document.querySelectorAll('.ni')[1])"),('recherche tous mois',"document.getElementById('tx-search').value='yango';renderTX()"),('budget',"goP('bud',document.querySelectorAll('.ni')[3])"),('bilan semaine',"openBilan(bilanLundiCourant())"),('soldes comptes',"comptes.map(c=>soldeCompte(c))")]:
        ms=pg.evaluate(f"(()=>{{const t=performance.now();{js};return Math.round(performance.now()-t)}})()");print(f'{name}: {ms} ms')
    print('nb tx',pg.evaluate("txs.length"),'| DOM historique',pg.evaluate("document.querySelectorAll('#txl *').length"))
    print(errs);b.close()
srv.kill()
