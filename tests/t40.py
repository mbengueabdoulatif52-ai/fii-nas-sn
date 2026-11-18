import os
import sys,subprocess,time,json;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import stub
from playwright.sync_api import sync_playwright
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
srv=subprocess.Popen(['python3','-m','http.server','8790'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
st={'users/u1/data/settings':{'cats':{'Revenu':['Salaire']},'budget':{},'custom':{},'modules':{}},
 'users/u1/data/foyers':{'liste':['F1'],'demandes':[]},
 'foyers/F1':{'nom':'Foyer Test','code':'ABC-DEF','roles':{'u9':'resp','u1':'membre'},'membres':{'u9':{'nom':'Abdou'},'u1':{'nom':'Awa'}}},
 'foyers/F1/data/settings':{'cats':{'Revenu':['Apports'],'Dépenses variables':['Transport']},'budget':{},'custom':{},'modules':{}},
 'foyers/F1/transactions/a1':{'amt':100000,'date':'2026-11-18','cat':'Revenu','poste':'Apports','ts':'2026-11-18T10:00:00Z','createdById':'u9','createdBy':'Abdou'},
 'foyers/F1/transactions/a2':{'amt':5000,'date':'2026-11-18','cat':'Dépenses variables','poste':'Transport','ts':'2026-11-18T11:00:00Z','createdById':'u1','createdBy':'Awa'}}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':390,'height':844},service_workers='block').new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.add_init_script("localStorage.setItem('fiinas-espace-u1','F1')")
    for k,v in [('**/firebase-app.js',stub.APP),('**/firebase-auth.js',stub.AUTH),('**/firebase-firestore.js',stub.FS(json.dumps(st)))]:pg.route(k,(lambda v: lambda r: r.fulfill(body=v,content_type='text/javascript'))(v))
    pg.route('https://fonts.**',lambda r:r.abort());pg.goto('http://localhost:8790/');pg.wait_for_timeout(1800)
    print('espace',pg.evaluate("JSON.stringify(espace)"),'txs',pg.evaluate("txs.map(t=>t.id+':'+t.createdById)"))
    pg.evaluate("goP('tx',document.querySelectorAll('.ni')[1])");pg.wait_for_timeout(300)
    pg.click(".txi >> text=Apports");pg.wait_for_timeout(300)
    print('modale apport Abdou:',pg.evaluate("document.getElementById('edit-modal').style.display"),'| toast:',pg.evaluate("document.getElementById('toast').textContent"))
    pg.evaluate("closeEditTx()");pg.click(".txi >> text=Transport");pg.wait_for_timeout(300)
    print('modale ouverte (sa dépense):',pg.evaluate("document.getElementById('edit-modal').style.display"))
    print(errs);b.close()
srv.kill()
