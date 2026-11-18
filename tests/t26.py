import os
import sys,subprocess,time;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import stub
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8775'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
A="{'users/u1/data/settings':{cats:{'Revenu':['Salaire','Ventes'],'Dépenses fixes':['Loyer','Électricité','Eau','Internet'],'Dépenses variables':['Transport','Alimentation','Santé','Loisirs','Vêtements'],'Epargne':['Fonds urgence','Tabaski']},budget:{'2026-11':{'Transport':30000,'Salaire':300000}},custom:{},modules:{}}}"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':390,'height':760},service_workers='block',is_mobile=True,has_touch=True).new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    for k,v in [('**/firebase-app.js',stub.APP),('**/firebase-auth.js',stub.AUTH),('**/firebase-firestore.js',stub.FS(A))]:pg.route(k,(lambda v: lambda r: r.fulfill(body=v,content_type='text/javascript'))(v))
    pg.route('https://fonts.**',lambda r:r.abort());pg.goto('http://localhost:8775/');pg.wait_for_timeout(1300)
    pg.evaluate("goP('bud',document.querySelectorAll('.ni')[3])");pg.wait_for_timeout(300)
    print('en haut:',pg.evaluate("document.getElementById('bud-mini').classList.contains('on')"))
    sel='#bi_'+pg.evaluate("btoa(encodeURIComponent('Tabaski'))").replace('=','\\=')
    pg.locator(sel).scroll_into_view_if_needed();pg.wait_for_timeout(200)
    pg.locator(sel).click();pg.keyboard.type('25000');pg.wait_for_timeout(300)
    print('en bas:',pg.evaluate("document.getElementById('bud-mini').classList.contains('on')"),pg.evaluate("document.getElementById('bud-mini').innerText.replace(/\\n/g,' | ')"))
    pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'m1.png')
    pg.evaluate("window.scrollTo(0,0)");pg.wait_for_timeout(300)
    print('remonté:',pg.evaluate("document.getElementById('bud-mini').classList.contains('on')"))
    pg.evaluate("goP('dash',document.querySelectorAll('.ni')[0])");pg.wait_for_timeout(200)
    print('autre page visible:',pg.evaluate("getComputedStyle(document.getElementById('bud-mini')).display!=='none'&&document.getElementById('bud-mini').offsetParent!==null"))
    print(errs);b.close()
srv.kill()
