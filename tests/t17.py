import os
import sys,subprocess,time;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import stub
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8771'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
A="{'users/u1/data/settings':{cats:{'Revenu':['Salaire']},budget:{},custom:{},modules:{comptes:true,objectifs:true,dettes:true},comptes:[{id:'wv',nom:'Wave',type:'wave',solde0:0}]},'users/u1/transactions/t1':{amt:1000,date:'2026-11-03',cat:'Revenu',poste:'Salaire',ts:'2026-11-03T10:00:00Z'}}"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for w in [360,412]:
        ctx=b.new_context(viewport={'width':w,'height':800},service_workers='block',device_scale_factor=2);pg=ctx.new_page()
        for k,v in [('**/firebase-app.js',stub.APP),('**/firebase-auth.js',stub.AUTH),('**/firebase-firestore.js',stub.FS(A))]:pg.route(k,(lambda v: lambda r: r.fulfill(body=v,content_type='text/javascript'))(v))
        pg.route('https://fonts.**',lambda r:r.abort());pg.goto('http://localhost:8771/');pg.wait_for_timeout(1000)
        print(w,'hauteurs:',pg.evaluate("['obj-dash','det-dash'].map(i=>document.querySelector('#'+i+' .card').getBoundingClientRect().height)"))
        pg.locator('#tiles').screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+f'tiles{w}.png')
    b.close()
srv.kill()
