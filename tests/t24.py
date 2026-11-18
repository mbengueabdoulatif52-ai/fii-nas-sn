import os
import sys,subprocess,time;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import stub
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8773'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
import datetime
t=datetime.date.today();iso=lambda d:d.isoformat()
d5=iso(t-datetime.timedelta(days=5));d40=iso(t-datetime.timedelta(days=40))
A="{'users/u1/data/settings':{cats:{'Revenu':['Salaire'],'Dépenses variables':['Transport','Alimentation'],'Dépenses fixes':['Loyer','Abonnements']},budget:{},custom:{},modules:{comptes:true},comptes:[{id:'wv',nom:'Wave',type:'wave',solde0:200000},{id:'es',nom:'Espèces',type:'especes',solde0:20000}],recur:[{id:'rt',amt:1000,cat:'Dépenses variables',poste:'Transport',freq:'jour',debut:'%s',dernier:'%s',compte:'es',auto:false,pause:false},{id:'rn',amt:3500,cat:'Dépenses fixes',poste:'Abonnements',cmt:'Netflix',freq:'mois',jour:%d,debut:'%s',dernier:'%s',compte:'wv',auto:true,pause:false}]}}"%(d5,d5,t.day,d40,d40)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':844},service_workers='block',has_touch=True,is_mobile=True);pg=ctx.new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('dialog',lambda d:d.accept())
    for k,v in [('**/firebase-app.js',stub.APP),('**/firebase-auth.js',stub.AUTH),('**/firebase-firestore.js',stub.FS(A))]:pg.route(k,(lambda v: lambda r: r.fulfill(body=v,content_type='text/javascript'))(v))
    pg.route('https://fonts.**',lambda r:r.abort());pg.goto('http://localhost:8773/');pg.wait_for_timeout(1500)
    print('auto txs',pg.evaluate("txs.map(t=>t.id+' '+t.amt)"))
    pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'r1.png')
    pg.evaluate("openRecurConfirm('rt')");pg.wait_for_timeout(200)
    pg.locator('#cpt-sheet button[data-d]').first.click();pg.fill('#rc-amt','1500');pg.wait_for_timeout(100);pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'r2.png')
    pg.click('#rc-go');pg.wait_for_timeout(600)
    print('after confirm',pg.evaluate("txs.filter(t=>t.recur==='rt').map(t=>t.date.slice(5)+' '+t.amt+' '+t.compte)"),pg.evaluate("recur[0].dernier"))
    print('dues',pg.evaluate("recurDues().length"))
    # form : nouvelle récurrente hebdo
    pg.evaluate("goP('add',document.querySelectorAll('.ni')[2])");pg.wait_for_timeout(300)
    pg.fill('#f-amt','15000');pg.evaluate("fRec.on=true;fRec.freq='semaine';renderFormRecur()");pg.wait_for_timeout(100)
    pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'r3.png',full_page=True)
    pg.click('#bsave');pg.wait_for_timeout(600)
    print('recur',pg.evaluate("recur.map(r=>r.poste+' '+r.freq+' '+r.jour+' '+r.compte)"))
    pg.evaluate("goP('pro',null)");pg.wait_for_timeout(300)
    pg.locator('#recur-ui').scroll_into_view_if_needed();pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'r4.png')
    pg.evaluate("openRecurEdit('rt')");pg.wait_for_timeout(200);pg.evaluate("reSave(true)");pg.wait_for_timeout(300)
    print('pause',pg.evaluate("recur.find(r=>r.id==='rt').pause"))
    print('errors',errs);b.close()
srv.kill()
