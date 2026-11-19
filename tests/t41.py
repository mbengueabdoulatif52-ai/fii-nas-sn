import os
import sys,subprocess,time,json;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import stub
from playwright.sync_api import sync_playwright
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
srv=subprocess.Popen(['python3','-m','http.server','8791'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
st={'users/u1/data/settings':{'cats':{'Revenu':['Salaire'],'Dépenses variables':['Transport']},'budget':{},'custom':{},'modules':{'comptes':True},'comptes':[{'id':'om','nom':'Orange Money','type':'om','solde0':10000},{'id':'wv','nom':'Wave','type':'wave','solde0':0}]}}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':390,'height':844},service_workers='block').new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    for k,v in [('**/firebase-app.js',stub.APP),('**/firebase-auth.js',stub.AUTH),('**/firebase-firestore.js',stub.FS(json.dumps(st)))]:pg.route(k,(lambda v: lambda r: r.fulfill(body=v,content_type='text/javascript'))(v))
    pg.route('https://fonts.**',lambda r:r.abort());pg.goto('http://localhost:8791/');pg.wait_for_timeout(1800)
    pg.evaluate("renderFormComptes()");pg.wait_for_timeout(300)
    print('choix:',pg.evaluate("[...document.querySelectorAll('#f-cpt-wrap .cpt-ch')].map(b=>b.textContent)"))
    pg.evaluate("payOne('add',null)");print('résultat:',pg.evaluate("JSON.stringify(payResult('add'))"))
    print(errs);b.close()
srv.kill()
