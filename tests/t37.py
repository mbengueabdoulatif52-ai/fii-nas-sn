import os
import sys,subprocess,time;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import stub
from playwright.sync_api import sync_playwright
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..');OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')
srv=subprocess.Popen(['python3','-m','http.server','8787'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
A="{'users/u1/data/settings':{cats:{'Revenu':['Salaire'],'Dépenses variables':['Transport']},budget:{},custom:{},modules:{}},'users/u1/transactions/a':{amt:1000,date:'2026-11-01',cat:'Dépenses variables',poste:'Transport',ts:'2026-11-01T1'}}"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':390,'height':800},service_workers='block').new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:print('CONSOLE',m.text))
    for k,v in [('**/firebase-app.js',stub.APP),('**/firebase-auth.js',stub.AUTH),('**/firebase-firestore.js',stub.FS(A))]:pg.route(k,(lambda v: lambda r: r.fulfill(body=v,content_type='text/javascript'))(v))
    appels=[]
    def api(r):appels.append(r.request.post_data);r.fulfill(status=200,body='{"ok":true}',content_type='application/json')
    pg.route('**/api/supprimer',api)
    pg.route('https://fonts.**',lambda r:r.abort());pg.goto('http://localhost:8787/');pg.wait_for_timeout(1300)
    pg.evaluate("window._fb.auth.currentUser={uid:'u1',email:'awa@utilisateurs.fii-nas-sn.vercel.app',providerData:[{providerId:'password'}],getIdToken:async()=>'tok'}")
    pg.evaluate("goP('pro',null);openConfidentialite()");pg.wait_for_timeout(200)
    print('confidentialité:','mbenguearchibuilding@gmail.com' in pg.evaluate("document.getElementById('cpt-sheet').innerText"))
    pg.screenshot(path=OUT+'conf.png');pg.evaluate("closeSheet();openSupprimerCompte()");pg.wait_for_timeout(200)
    pg.screenshot(path=OUT+'suppr.png')
    pg.evaluate("supprimerMonCompte().catch(e=>console.log('E',e.message));0");pg.wait_for_timeout(300);print('sans mdp:',pg.inner_text('#sc-err'))
    pg.evaluate("window._fb.EmailAuthProvider.credential=()=>({})");pg.fill('#sc-mdp','secret123');pg.click('#sc-go');pg.wait_for_timeout(800)
    print('api appelée:',len(appels),'| écran:',pg.evaluate("document.body.innerText.slice(0,40)").replace('\n',' '))
    print('errors',errs);b.close()
srv.kill()
