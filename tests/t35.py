import os
import sys,subprocess,time;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import stub
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8785'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
A="{'users/u1/data/settings':{cats:{'Revenu':['Salaire'],'Dépenses variables':['Transport']},budget:{},custom:{},modules:{comptes:true},comptes:[{id:'wv',nom:'Wave',type:'wave',solde0:0}]},'users/u1/transactions/a':{amt:1,date:'2026-11-01',cat:'Revenu',poste:'Salaire',ts:'2026-11-01T1'},'users/u1/transactions/b':{amt:1,date:'2026-11-01',cat:'Revenu',poste:'Salaire',ts:'2026-11-01T2'},'users/u1/transactions/c':{amt:1,date:'2026-11-01',cat:'Revenu',poste:'Salaire',ts:'2026-11-01T3'}}"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':390,'height':800},service_workers='block').new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('about:blank')
    for k,v in [('**/firebase-app.js',stub.APP),('**/firebase-auth.js',stub.AUTH),('**/firebase-firestore.js',stub.FS(A))]:pg.route(k,(lambda v: lambda r: r.fulfill(body=v,content_type='text/javascript'))(v))
    pg.route('https://fonts.**',lambda r:r.abort());pg.goto('http://localhost:8785/');pg.wait_for_timeout(1500)
    back=lambda:(pg.evaluate("history.back()"),pg.wait_for_timeout(350))
    pg.evaluate("goP('cpt',null);openVirement&&openAddCompte()");pg.wait_for_timeout(200)
    back();print('fenêtre fermée',pg.evaluate("!document.getElementById('cpt-sheet')"),'page',pg.evaluate("document.querySelector('.page.active').id"))
    back();print('retour accueil',pg.evaluate("document.querySelector('.page.active').id"))
    back();print('toast',pg.evaluate("document.getElementById('toast').textContent"),pg.url)
    back();pg.wait_for_timeout(400);print('après 2e appui:',pg.url)
    print(errs);b.close()
srv.kill()
