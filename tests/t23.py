import os
import sys,subprocess,time;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import stub
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8772'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
A="{'users/u1/data/settings':{cats:{'Revenu':['Salaire'],'Dépenses variables':['Transport','Alimentation']},budget:{},custom:{},modules:{comptes:true},comptes:[{id:'wv',nom:'Wave',type:'wave',solde0:42300},{id:'om',nom:'Orange Money',type:'om',solde0:15000},{id:'es',nom:'Espèces',type:'especes',solde0:20000}]}}"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':800},service_workers='block',has_touch=True,is_mobile=True);pg=ctx.new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    for k,v in [('**/firebase-app.js',stub.APP),('**/firebase-auth.js',stub.AUTH),('**/firebase-firestore.js',stub.FS(A))]:pg.route(k,(lambda v: lambda r: r.fulfill(body=v,content_type='text/javascript'))(v))
    pg.route('https://fonts.**',lambda r:r.abort());pg.goto('http://localhost:8772/');pg.wait_for_timeout(1000)
    pg.evaluate("goP('cpt',null)");pg.wait_for_timeout(200);pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'p0.png')
    pg.evaluate("openPointage()");pg.wait_for_timeout(200)
    pg.fill('#pt-r-wv','42300');pg.fill('#pt-r-om','13800');pg.fill('#pt-r-es','11000')
    pg.wait_for_timeout(100);pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'p1.png')
    pg.click('#pt-go');pg.wait_for_timeout(200)
    # OM -1200: frais ; Espèces -9000 : 6000 dépenses + 3000 je ne sais pas
    pg.evaluate("ptType('om',0,'frais')");pg.evaluate("ptType('es',0,'dep')");pg.evaluate("ptAjouter('es',true)")
    pg.evaluate("PT.lignes.es[0].amt=6000;PT.lignes.es[1].amt=3000;ptEtape2()");pg.wait_for_timeout(200)
    pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'p2.png',full_page=False)
    pg.click('#pt-go');pg.wait_for_timeout(600)
    print('soldes',pg.evaluate("comptes.map(c=>c.nom+':'+soldeCompte(c))"))
    print('txs',pg.evaluate("txs.map(t=>t.poste+' '+t.amt+' '+t.compte)"))
    print('mouvs',pg.evaluate("mouvs.map(m=>m.type+' '+(m.amt||''))"))
    # second test: erreur de compte  Wave -5000, OM +5000
    pg.evaluate("openPointage()");pg.fill('#pt-r-wv','37300');pg.fill('#pt-r-om','18800');pg.click('#pt-go');pg.wait_for_timeout(200)
    pg.evaluate("ptType('wv',0,'compte')");pg.wait_for_timeout(200);pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'p3.png')
    pg.click('#pt-go');pg.wait_for_timeout(600)
    print('soldes2',pg.evaluate("comptes.map(c=>c.nom+':'+soldeCompte(c))"))
    pg.evaluate("goP('cpt',null)");pg.wait_for_timeout(300);pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'p4.png',full_page=True)
    pg.evaluate("goP('dash',document.querySelectorAll('.ni')[0]);mouvs=mouvs.filter(m=>m.type!=='pointage');renderPointBanner()");pg.wait_for_timeout(200)
    print('banner',pg.evaluate("document.getElementById('point-banner').innerText.slice(0,40)"))
    print('errors',errs);b.close()
srv.kill()
