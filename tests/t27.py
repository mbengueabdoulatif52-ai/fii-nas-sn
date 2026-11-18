import os
import sys,subprocess,time,json;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import stub
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8776'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
bud={}
for y in range(2026,2032):
    for m in range(1,13):bud['%d-%02d'%(y,m)]={'Transport':30000}
A="{'users/u1/data/settings':{cats:{'Revenu':['Salaire'],'Dépenses variables':['Transport']},budget:%s,budgetDetails:{'2028-03':{'Transport':[{label:'BRT',amt:5000}]}},custom:{},modules:{}}}"%json.dumps(bud)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':390,'height':800},service_workers='block').new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('dialog',lambda d:d.accept())
    for k,v in [('**/firebase-app.js',stub.APP),('**/firebase-auth.js',stub.AUTH),('**/firebase-firestore.js',stub.FS(A))]:pg.route(k,(lambda v: lambda r: r.fulfill(body=v,content_type='text/javascript'))(v))
    pg.route('https://fonts.**',lambda r:r.abort());pg.goto('http://localhost:8776/');pg.wait_for_timeout(1300)
    pg.evaluate("goP('bud',document.querySelectorAll('.ni')[3])");pg.wait_for_timeout(300)
    print('bouton visible',pg.evaluate("getComputedStyle(document.getElementById('bud-eff-btn')).display"))
    pg.evaluate("openEffacerBudgets()");pg.wait_for_timeout(300)
    print('défaut',pg.evaluate("[document.getElementById('eb-deb').value,document.getElementById('eb-fin').value]"),pg.evaluate("document.getElementById('eb-prev').textContent"))
    pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'e1.png')
    pg.evaluate("const i=document.getElementById('eb-deb');i.value='2026-10';ebApercu()")
    print('passé:',pg.evaluate("document.getElementById('eb-prev').textContent"),pg.evaluate("document.getElementById('eb-go').style.display"))
    pg.evaluate("const i=document.getElementById('eb-deb');i.value='2026-12';ebApercu()")
    pg.evaluate("effacerBudgets();0");pg.wait_for_timeout(200);pg.click('#cfm [data-r="1"]');pg.wait_for_timeout(500)
    print('bouton après',pg.evaluate("getComputedStyle(document.getElementById('bud-eff-btn')).display"))
    l=pg.evaluate("Object.keys(budget).sort()");print('reste',l[0],l[-1],len(l),pg.evaluate("Object.keys(budgetDetails)"))
    print('stocké',len(pg.evaluate("Object.keys(window.__store['users/u1/data/settings'].budget)")))
    print(errs);b.close()
srv.kill()
