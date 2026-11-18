import os
import sys,subprocess,time,json;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import stub
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8783'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
st={'users/u1/data/settings':{'cats':{'Revenu':['Salaire'],'Dépenses variables':['Transport','Alimentation']},'budget':{'2026-11':{'Transport':15000,'Salaire':300000}},'custom':{},'modules':{'comptes':True},'comptes':[{'id':'wv','nom':'Wave','type':'wave','solde0':0}]}}
for i,(d,a,p,c) in enumerate([('2026-09-03',2500,'Transport','Yango Plateau'),('2026-10-11',7000,'Transport','yango aéroport'),('2026-11-02',2500,'Alimentation','pain'),('2026-11-05',300000,'Salaire','')]):
    st['users/u1/transactions/t%d'%i]={'amt':a,'date':d,'cat':'Revenu' if p=='Salaire' else 'Dépenses variables','poste':p,'cmt':c,'compte':'wv','ts':d+'T10:00:00Z'}
XL=open(os.environ.get('XLSX_JS','/tmp/xl/node_modules/xlsx/dist/xlsx.full.min.js')).read()
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':800},service_workers='block',accept_downloads=True);pg=ctx.new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    for k,v in [('**/firebase-app.js',stub.APP),('**/firebase-auth.js',stub.AUTH),('**/firebase-firestore.js',stub.FS(json.dumps(st)))]:pg.route(k,(lambda v: lambda r: r.fulfill(body=v,content_type='text/javascript'))(v))
    pg.route('**/xlsx.full.min.js',lambda r:r.fulfill(body=XL,content_type='text/javascript'))
    pg.route('https://fonts.**',lambda r:r.abort());pg.goto('http://localhost:8783/?action=entree');pg.wait_for_timeout(1500)
    print('raccourci:',pg.evaluate("document.querySelector('.page.active').id"),pg.evaluate("selCatVal"),pg.evaluate("location.search"))
    pg.evaluate("goP('tx',document.querySelectorAll('.ni')[1])");pg.fill('#tx-search','yango');pg.wait_for_timeout(200)
    print('recherche:',pg.evaluate("document.getElementById('tx-count').textContent"))
    pg.fill('#tx-search','2 500');pg.wait_for_timeout(200);print('montant:',pg.evaluate("document.getElementById('tx-count').textContent"))
    pg.fill('#tx-search','wave');pg.wait_for_timeout(200);print('compte:',pg.evaluate("document.getElementById('tx-count').textContent"))
    pg.evaluate("goP('pro',null);openExportExcel()");pg.wait_for_timeout(200)
    pg.evaluate("expPer='tout';expRender()")
    with pg.expect_download() as dl:pg.click('#exp-go')
    f=dl.value;path=f.path();print('fichier:',f.suggested_filename)
    import zipfile;z=zipfile.ZipFile(path);print('feuilles:',[n for n in z.namelist() if 'worksheets/sheet' in n])
    print(errs);b.close()
srv.kill()
