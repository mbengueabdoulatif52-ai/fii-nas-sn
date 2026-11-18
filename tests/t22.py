import os
import sys,subprocess,time;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import stub
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8771'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
A="{'users/u1/data/settings':{cats:{'Revenu':['Salaire'],'Dépenses variables':['Transport','Alimentation']},budget:{},custom:{},modules:{comptes:true},comptes:[{id:'wv',nom:'Wave',type:'wave',solde0:50000},{id:'es',nom:'Espèces',type:'especes',solde0:5000}]}}"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':760},service_workers='block',has_touch=True,is_mobile=True);pg=ctx.new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    for k,v in [('**/firebase-app.js',stub.APP),('**/firebase-auth.js',stub.AUTH),('**/firebase-firestore.js',stub.FS(A))]:pg.route(k,(lambda v: lambda r: r.fulfill(body=v,content_type='text/javascript'))(v))
    pg.route('https://fonts.**',lambda r:r.abort());pg.goto('http://localhost:8771/');pg.wait_for_timeout(1000)
    pg.evaluate("goP('add',document.querySelectorAll('.ni')[2])");pg.wait_for_timeout(300)
    r=pg.evaluate("(()=>{const b=document.getElementById('bsave').getBoundingClientRect(),n=document.getElementById('nav').getBoundingClientRect();return [Math.round(b.bottom),Math.round(n.top),innerHeight]})()")
    print('sans clavier: bas du bouton',r[0],'haut de la barre',r[1],'| visible:',r[0]<=r[1])
    pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'k1.png')
    # clavier : focus + zone d'affichage réduite (comme Android avec resizes-content)
    pg.focus('#f-amt');pg.set_viewport_size({'width':390,'height':450});pg.wait_for_timeout(300)
    r=pg.evaluate("(()=>{const b=document.getElementById('bsave').getBoundingClientRect();return [Math.round(b.bottom),innerHeight,getComputedStyle(document.getElementById('nav')).display,document.body.classList.contains('kbd')]})()")
    print('clavier: bas du bouton',r[0],'hauteur visible',r[1],'| barre:',r[2],'| kbd:',r[3])
    pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'k2.png')
    pg.keyboard.type('3500');pg.tap('#bsave');pg.wait_for_timeout(400);print('enregistré:',pg.evaluate("txs.length"))
    pg.set_viewport_size({'width':390,'height':760});pg.evaluate("goP('cpt',null);openVirement()");pg.wait_for_timeout(300)
    r=pg.evaluate("(()=>{const b=document.getElementById('vi-go').getBoundingClientRect();return [Math.round(b.bottom),innerHeight]})()");print('virement: bouton',r)
    print('errors',errs);b.close()
srv.kill()
