import os
import sys,subprocess,time,json;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import stub
from playwright.sync_api import sync_playwright
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..');OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')
srv=subprocess.Popen(['python3','-m','http.server','8788'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
st={'users/u1/data/settings':{'cats':{'Revenu':['Salaire'],'Dépenses variables':['Transport']},'budget':{'2026-11':{'Transport':9999}},'custom':{},'modules':{}},
    'users/u1/transactions/p1':{'amt':5000,'date':'2026-11-02','cat':'Dépenses variables','poste':'Transport','ts':'2026-11-02T1','createdById':'u1'}}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':390,'height':844},service_workers='block').new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    for k,v in [('**/firebase-app.js',stub.APP),('**/firebase-auth.js',stub.AUTH),('**/firebase-firestore.js',stub.FS(json.dumps(st)))]:pg.route(k,(lambda v: lambda r: r.fulfill(body=v,content_type='text/javascript'))(v))
    pg.route('https://fonts.**',lambda r:r.abort());pg.goto('http://localhost:8788/');pg.wait_for_timeout(1500)
    J=lambda js:pg.evaluate(js)
    pg.click('.topbar-l');pg.wait_for_timeout(200);pg.screenshot(path=OUT+'f1.png')
    J("openCreerFoyer()");pg.fill('#cf-nom','Foyer Mbengue');J("creerFoyer();0");pg.wait_for_timeout(1200)
    fid=J("espace&&espace.fid");print('espace:',J("JSON.stringify(espace)"),'| path:',J("dataPath()"))
    print('perso caché: txs',J("txs.length"),'budget',J("JSON.stringify(budget)"),'| cats revenu',J("JSON.stringify(CATS['Revenu'])"))
    code=J("foyerDoc&&foyerDoc.code");print('code:',code,'| codes doc:',J(f"JSON.stringify(window.__store['codes/{code}'])"),'| mes foyers:',J("JSON.stringify(window.__store['users/u1/data/foyers'])"))
    pg.screenshot(path=OUT+'f2.png');J("closeSheet()")
    # ajout d'une transaction dans le foyer
    J("goP('add',document.querySelectorAll('.ni')[2])");pg.fill('#f-amt','12500');J("saveTx();0");pg.wait_for_timeout(600)
    k=[x for x in J("Object.keys(window.__store)") if x.startswith('foyers/'+fid+'/transactions/')];print('tx foyer:',len(k))
    # demande d'un autre utilisateur
    J(f"window.__store['foyers/{fid}/demandes/u2']={{nom:'Awa',foyer:'Foyer Mbengue',date:new Date().toISOString(),statut:'attente'}}")
    J("demandesFoyer=[{uid:'u2',nom:'Awa',statut:'attente',date:new Date().toISOString()}];goP('dash',document.querySelectorAll('.ni')[0])");pg.wait_for_timeout(300)
    print('bandeau demande:',J("document.getElementById('foyer-dash').innerText.split('\\n')[0]"))
    pg.screenshot(path=OUT+'f3.png')
    J("openFoyerMembres()");pg.wait_for_timeout(200);pg.screenshot(path=OUT+'f4.png')
    J("repondreDemande('u2',true);0");pg.wait_for_timeout(600)
    print('roles:',J(f"JSON.stringify(window.__store['foyers/{fid}'].roles)"),'| statut demande:',J(f"window.__store['foyers/{fid}/demandes/u2'].statut"))
    # droits d'un membre
    J("espace.role='membre';majEnteteEspace()")
    print('membre peut modifier la sienne:',J("peutModifierTx({createdById:uid})"),'| autre:',J("peutModifierTx({createdById:'u2'})"),'| budget:',J("peutBudget()"))
    J("goP('bud',document.querySelectorAll('.ni')[3])");pg.wait_for_timeout(300)
    print('budget lecture visible:',J("getComputedStyle(document.getElementById('bud-lecture')).display"),'| bouton enregistrer:',J("getComputedStyle(document.querySelector('#page-bud .save-dock')).display"))
    J("espace.role='lect';majEnteteEspace()");print('lecteur isAdmin:',J("isAdmin()"))
    J("espace.role='resp';majEnteteEspace();changerEspace(null)");pg.wait_for_timeout(800)
    print('retour perso:',J("dataPath()"),'txs',J("txs.length"),'budget',J("JSON.stringify(budget)"))
    print('errors',errs);b.close()
srv.kill()
