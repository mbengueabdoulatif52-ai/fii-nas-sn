import os
import sys,subprocess,time,json;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import stub
from playwright.sync_api import sync_playwright
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
srv=subprocess.Popen(['python3','-m','http.server','8789'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
# u1 a demandé à rejoindre F1 ; la demande est en attente au chargement
st={'users/u1/data/settings':{'cats':{'Revenu':['Salaire']},'budget':{},'custom':{},'modules':{}},
 'users/u1/data/foyers':{'liste':[],'demandes':['F1']},
 'foyers/F1':{'nom':'Foyer Test','code':'ABC-DEF','roles':{'u9':'resp'},'membres':{'u9':{'nom':'Abdou'}}},
 'foyers/F1/demandes/u1':{'nom':'Awa','foyer':'Foyer Test','statut':'attente','date':'2026-11-18T10:00:00Z'},
 'foyers/F1/data/settings':{'cats':{'Revenu':['Apports']},'budget':{},'custom':{},'modules':{}}}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':390,'height':844},service_workers='block').new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    for k,v in [('**/firebase-app.js',stub.APP),('**/firebase-auth.js',stub.AUTH),('**/firebase-firestore.js',stub.FS(json.dumps(st)))]:pg.route(k,(lambda v: lambda r: r.fulfill(body=v,content_type='text/javascript'))(v))
    pg.route('https://fonts.**',lambda r:r.abort());pg.goto('http://localhost:8789/');pg.wait_for_timeout(1500)
    print('avant:',pg.evaluate("JSON.stringify(mesFoyers)"),pg.evaluate("JSON.stringify(mesDemandes)"))
    # le responsable accepte (écriture dans le magasin, comme le ferait l'autre téléphone)
    pg.evaluate("const s=window.__store;s['foyers/F1'].roles.u1='membre';s['foyers/F1'].membres.u1={nom:'Awa'};s['foyers/F1/demandes/u1'].statut='accepte';window._fb.setDoc('x/y',{})")
    pg.wait_for_timeout(1200)
    print('après:',pg.evaluate("JSON.stringify(mesFoyers)"),'| toast:',pg.evaluate("document.getElementById('toast').textContent"))
    print('errors',errs);b.close()
srv.kill()
