import os
import sys,subprocess,time;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import stub
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8774'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
A="{'users/u1/data/settings':{cats:{'Revenu':['Salaire'],'Dépenses variables':['Transport','Alimentation']},budget:{'2026-11':{'Transport':30000,'Salaire':300000}},custom:{},modules:{}}}"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':390,'height':844},service_workers='block').new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('dialog',lambda d:d.accept())
    for k,v in [('**/firebase-app.js',stub.APP),('**/firebase-auth.js',stub.AUTH),('**/firebase-firestore.js',stub.FS(A))]:pg.route(k,(lambda v: lambda r: r.fulfill(body=v,content_type='text/javascript'))(v))
    pg.route('https://fonts.**',lambda r:r.abort());pg.goto('http://localhost:8774/');pg.wait_for_timeout(1300)
    pg.evaluate("goP('bud',document.querySelectorAll('.ni')[3])");pg.wait_for_timeout(300)
    tot="document.getElementById('bt_'+btoa(encodeURIComponent('Dépenses variables'))).textContent"
    print('total avant',pg.evaluate(tot))
    pg.locator('#bi_'+pg.evaluate("btoa(encodeURIComponent('Alimentation'))").replace('=','\\=')).type('50000')
    print('total après saisie',pg.evaluate(tot))
    k=pg.evaluate("btoa(encodeURIComponent('2026-11|Transport'))")
    pg.evaluate(f"toggleBudDetail('{k}');document.getElementById('dl_{k}').value='Carte BRT';document.getElementById('da_{k}').value='5 000'")
    pg.evaluate(f"addBudDetail('2026-11','Transport','{k}')");pg.wait_for_timeout(400)
    print('Transport',pg.evaluate("budget['2026-11'].Transport"),'| Alimentation gardée:',pg.evaluate("budVal('Alimentation')"),'| total',pg.evaluate(tot))
    pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'b1.png')
    pg.evaluate(f"document.getElementById('dl_{k}').value='Taxi';document.getElementById('da_{k}').value='40000';addBudDetail('2026-11','Transport','{k}')");pg.wait_for_timeout(400)
    print('Transport après dépassement',pg.evaluate("budget['2026-11'].Transport"))
    pg.evaluate("removeBudDetail('2026-11','Transport',1)");pg.wait_for_timeout(300)
    print('après retrait Taxi',pg.evaluate("budget['2026-11'].Transport"))
    pg.evaluate("removeBudDetail('2026-11','Transport',0)");pg.wait_for_timeout(300)
    print('après retrait BRT',pg.evaluate("budget['2026-11'].Transport"),pg.evaluate("JSON.stringify(budgetDetails)"))
    print(errs);b.close()
srv.kill()
