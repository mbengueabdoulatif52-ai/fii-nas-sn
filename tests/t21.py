import os
import sys,subprocess,time,datetime;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import stub
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8771'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
A="{'users/u1/data/settings':{cats:{'Revenu':['Salaire'],'Dépenses variables':['Transport']},budget:{},custom:{},modules:{objectifs:true,dettes:true}},'users/u1/transactions/t1':{amt:3000,date:'2026-11-03',cat:'Dépenses variables',poste:'Transport',ts:'2026-11-03T10:00:00Z'}}"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':844},service_workers='block',has_touch=True,is_mobile=True);pg=ctx.new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    for k,v in [('**/firebase-app.js',stub.APP),('**/firebase-auth.js',stub.AUTH),('**/firebase-firestore.js',stub.FS(A))]:pg.route(k,(lambda v: lambda r: r.fulfill(body=v,content_type='text/javascript'))(v))
    pg.route('https://fonts.**',lambda r:r.abort());pg.goto('http://localhost:8771/');pg.wait_for_timeout(1000)
    pg.evaluate("goP('add',document.querySelectorAll('.ni')[2])");pg.wait_for_timeout(200)
    print('champ:',pg.evaluate("[document.getElementById('f-date').value,document.getElementById('f-date').type,HTMLInputElement.prototype.__lookupGetter__('value').call(document.getElementById('f-date'))]"))
    box=pg.locator('#f-date').bounding_box();pg.touchscreen.tap(box['x']+30,box['y']+box['height']/2);pg.wait_for_timeout(300)
    pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'dp1.png')
    pg.click("#cal-quick >> text=Hier");pg.wait_for_timeout(200)
    print('hier:',pg.evaluate("[document.getElementById('f-date').value,HTMLInputElement.prototype.__lookupGetter__('value').call(document.getElementById('f-date'))]"),'| reste:',pg.inner_text('#f-reste')[:30])
    pg.click('#f-date');pg.wait_for_timeout(200);pg.click("#picker button[aria-label='Mois précédent']");pg.click("#cal-body button >> text=/^3$/");pg.wait_for_timeout(200)
    print('3 oct:',pg.evaluate("[document.getElementById('f-date').value,HTMLInputElement.prototype.__lookupGetter__('value').call(document.getElementById('f-date'))]"))
    pg.fill('#f-amt','1000');pg.click('#bsave');pg.wait_for_timeout(400);print('tx enregistrée date:',pg.evaluate("txs.map(t=>t.date).join(',')"))
    # modification
    pg.evaluate("openEditTx('t1')");pg.wait_for_timeout(200);print('édition:',pg.evaluate("HTMLInputElement.prototype.__lookupGetter__('value').call(document.getElementById('e-date'))"))
    pg.evaluate("closeEditTx()")
    # objectif : mois avec min
    pg.evaluate("goP('obj',null);openAddObj()");pg.wait_for_timeout(300)
    print('échéance placeholder:',pg.get_attribute('#ob-ech','placeholder'),'| type:',pg.evaluate("document.getElementById('ob-ech').type"))
    pg.click('#ob-ech');pg.wait_for_timeout(200);pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'dp2.png')
    print('mois désactivés avant ce mois:',pg.evaluate("[...document.querySelectorAll('#cal-body button[disabled]')].map(b=>b.textContent).join(',')"))
    pg.click("#picker button[aria-label='Année suivante']");pg.click("#cal-body >> text=Mai");pg.wait_for_timeout(200)
    print('échéance:',pg.evaluate("[document.getElementById('ob-ech').value,HTMLInputElement.prototype.__lookupGetter__('value').call(document.getElementById('ob-ech'))]"))
    # dette : facultatif → Aucune date
    pg.evaluate("closeSheet();goP('det',null);openAddDette()");pg.wait_for_timeout(300)
    pg.click('#nd-ech');pg.wait_for_timeout(200);print('raccourcis dette:',pg.locator('#cal-quick button').all_inner_texts())
    pg.click("#cal-quick >> text=Aucune date");print('nd-ech vide:',repr(pg.evaluate("document.getElementById('nd-ech').value")),'| date prêt:',pg.evaluate("document.getElementById('nd-date').value"))
    print('errors',errs);b.close()
srv.kill()
