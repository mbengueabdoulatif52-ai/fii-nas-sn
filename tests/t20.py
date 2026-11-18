import os
import sys,subprocess,time;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import stub
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8771'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
P=['Achats divers','Alimentation','Entretien auto','Santé','Dons','Loisir','Prêts','Remboursement','Imprévus','Transport','Voiture','Sport','Investissements']
A="{'users/u1/data/settings':{cats:{'Revenu':['Salaire'],'Dépenses fixes':['Loyer'],'Dépenses variables':["+",".join(f"'{p}'" for p in P)+"],'Epargne':['Tontine']},budget:{},custom:{},modules:{comptes:true},comptes:[{id:'wv',nom:'Wave',type:'wave',solde0:50000},{id:'es',nom:'Espèces',type:'especes',solde0:5000}]},'users/u1/transactions/t1':{amt:3000,date:'2026-11-05',cat:'Dépenses variables',poste:'Transport',ts:'2026-11-05T10:00:00Z'}}"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':844},service_workers='block',has_touch=True,is_mobile=True);pg=ctx.new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    for k,v in [('**/firebase-app.js',stub.APP),('**/firebase-auth.js',stub.AUTH),('**/firebase-firestore.js',stub.FS(A))]:pg.route(k,(lambda v: lambda r: r.fulfill(body=v,content_type='text/javascript'))(v))
    pg.route('https://fonts.**',lambda r:r.abort());pg.goto('http://localhost:8771/');pg.wait_for_timeout(1000)
    # 1. mois (tap)
    box=pg.locator('#gm').bounding_box();pg.touchscreen.tap(box['x']+box['width']/2,box['y']+box['height']/2);pg.wait_for_timeout(300)
    print('mois ouvert:',pg.locator('#picker').count(),'| groupes:',pg.locator('#picker .pk-h').all_inner_texts()[:4])
    pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'pk1.png')
    pg.click("#picker .pk-i >> text=Octobre 2026");pg.wait_for_timeout(300);print('mois choisi:',pg.evaluate("curYM()"),'| fermé:',pg.locator('#picker').count()==0)
    # 2. poste dans le formulaire
    pg.evaluate("goP('add',document.querySelectorAll('.ni')[2])");pg.wait_for_timeout(200)
    box=pg.locator('#f-poste').bounding_box();pg.touchscreen.tap(box['x']+20,box['y']+box['height']/2);pg.wait_for_timeout(300)
    print('poste ouvert, recherche:',pg.locator('#picker-q').count())
    pg.fill('#picker-q','sante');pg.wait_for_timeout(100);print('filtré:',pg.evaluate("[...document.querySelectorAll('#picker .pk-i')].filter(i=>i.style.display!=='none').map(i=>i.textContent)"))
    pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'pk2.png')
    pg.click("#picker .pk-i >> text=Santé");pg.wait_for_timeout(200);print('poste:',pg.input_value('#f-poste'),'| note reste:',pg.inner_text('#f-reste')[:40])
    # 3. fenêtre de modification (au-dessus d'une modale)
    pg.evaluate("openEditTx('t1')");pg.wait_for_timeout(200)
    box=pg.locator('#e-cat').bounding_box();pg.mouse.click(box['x']+20,box['y']+box['height']/2);pg.wait_for_timeout(200)
    pg.click("#picker .pk-i >> text=Revenu");pg.wait_for_timeout(200);print('catégorie éditée:',pg.input_value('#e-cat'),'| postes:',pg.evaluate("[...document.getElementById('e-poste').options].map(o=>o.value).join(',')"))
    # 4. virement
    pg.keyboard.press('Escape');pg.evaluate("closeEditTx();goP('cpt',null);openVirement()");pg.wait_for_timeout(200)
    box=pg.locator('#vi-vers').bounding_box();pg.mouse.click(box['x']+20,box['y']+box['height']/2);pg.wait_for_timeout(200)
    print('virement liste:',pg.locator('#picker .pk-i').all_inner_texts())
    pg.locator('#picker').click(position={'x':10,'y':10});pg.wait_for_timeout(200);print('fermé en touchant dehors:',pg.locator('#picker').count()==0)
    print('errors',errs);b.close()
srv.kill()
