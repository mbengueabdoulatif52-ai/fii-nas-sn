import os
import sys,subprocess,time;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import stub
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8778'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
A="{'users/u1/data/settings':{cats:{'Revenu':['Salaire'],'Dépenses variables':['Transport']},budget:{'2026-11':{'Transport':1000},'2027-03':{'Transport':1000}},custom:{},modules:{comptes:true,objectifs:true},comptes:[{id:'wv',nom:'Wave',type:'wave',solde0:0}]}}"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':390,'height':800},service_workers='block').new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));dl=[];pg.on('dialog',lambda d:(dl.append(d.message),d.accept()))
    for k,v in [('**/firebase-app.js',stub.APP),('**/firebase-auth.js',stub.AUTH),('**/firebase-firestore.js',stub.FS(A))]:pg.route(k,(lambda v: lambda r: r.fulfill(body=v,content_type='text/javascript'))(v))
    pg.route('https://fonts.**',lambda r:r.abort());pg.goto('http://localhost:8778/');pg.wait_for_timeout(1300)
    # 1 module + annuler
    pg.evaluate("goP('pro',null)");pg.wait_for_timeout(200)
    pg.evaluate("toggleModule('objectifs')");pg.wait_for_timeout(300)
    print('désactivé',pg.evaluate("modules.objectifs"),pg.evaluate("document.getElementById('toast').innerText"))
    pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'c1.png')
    print('hit',pg.evaluate("(()=>{const b=document.querySelector('#toast button').getBoundingClientRect();const e=document.elementFromPoint(b.x+b.width/2,b.y+b.height/2);return e&&(e.id||e.tagName)+' '+(e.className||'')})()"));pg.evaluate("document.querySelector('#toast button').click()");pg.wait_for_timeout(300);print('après annuler',pg.evaluate("modules.objectifs"))
    # 2 déconnexion
    pg.evaluate("demanderDeconnexion();0");pg.wait_for_timeout(200);pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'c2.png')
    pg.click('#cfm [data-r="0"]');pg.wait_for_timeout(100);print('cfm fermé',pg.evaluate("!document.getElementById('cfm')"))
    # 3 supprimer compte : annuler puis confirmer
    pg.evaluate("supprimerCompte('wv');0");pg.wait_for_timeout(200);pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'c3.png')
    pg.mouse.click(200,50);pg.wait_for_timeout(100);print('toucher dehors: compte gardé',pg.evaluate("comptes.length"))
    pg.evaluate("supprimerCompte('wv');0");pg.wait_for_timeout(200);pg.click('#cfm [data-r="1"]');pg.wait_for_timeout(300);print('supprimé',pg.evaluate("comptes.length"))
    # 4 budget non enregistré
    pg.evaluate("goP('bud',document.querySelectorAll('.ni')[3])");pg.wait_for_timeout(300)
    pg.evaluate("budDirty=true;goP('dash',document.querySelectorAll('.ni')[0])");pg.wait_for_timeout(200)
    print('reste sur budget',pg.evaluate("document.getElementById('page-bud').classList.contains('active')"))
    pg.click('#cfm [data-r="1"]');pg.wait_for_timeout(300);print('parti accueil',pg.evaluate("document.getElementById('page-dash').classList.contains('active')"))
    print('boîtes natives:',dl,'errors',errs);b.close()
srv.kill()
