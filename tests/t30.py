import os
import sys,subprocess,time,datetime;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import stub
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8780'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
d=datetime.date.today().isoformat();ym=d[:7]
tx=",".join("'users/u1/transactions/t%d':{amt:%d,date:'%s',cat:'Dépenses variables',poste:'%s',ts:'%sT1%d:00:00Z'}"%(i,a,d,p,d,i) for i,(p,a) in enumerate([('Transport',40000),('Alimentation',90000),('Santé',30000),('Loisirs',20000),('Transport',1000)]))
A="{'users/u1/data/settings':{cats:{'Revenu':['Salaire'],'Dépenses variables':['Transport','Alimentation','Santé','Loisirs']},budget:{'%s':{'Transport':30000,'Alimentation':50000,'Santé':10000,'Loisirs':5000}},custom:{},modules:{}},%s}"%(ym,tx)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':390,'height':800},service_workers='block').new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    for k,v in [('**/firebase-app.js',stub.APP),('**/firebase-auth.js',stub.AUTH),('**/firebase-firestore.js',stub.FS(A))]:pg.route(k,(lambda v: lambda r: r.fulfill(body=v,content_type='text/javascript'))(v))
    pg.route('https://fonts.**',lambda r:r.abort());pg.goto('http://localhost:8780/');pg.wait_for_timeout(1500)
    print(pg.evaluate("document.getElementById('watch').innerText.replace(/\\n/g,' | ')"))
    pg.locator('#watch div[onclick]').last.click();pg.wait_for_timeout(200)
    print('déplié',pg.evaluate("document.getElementById('watch').innerText.replace(/\\n/g,' | ')"))
    pg.locator('#watch div[onclick*=Transport]').click();pg.wait_for_timeout(400)
    print('page',pg.evaluate("document.querySelector('.page.active').id"),pg.evaluate("txPosteFilter"),pg.evaluate("document.getElementById('page-tx').innerText.slice(0,200).replace(/\\n/g,' | ')"))
    print(errs);b.close()
srv.kill()
