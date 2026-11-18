import os
import sys,subprocess,time,json,datetime;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import stub
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8784'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
T=datetime.date.today();cur=T.isoformat()[:7]
def md(n):
    y,m=T.year,T.month+n
    while m<1:m+=12;y-=1
    while m>12:m-=12;y+=1
    return '%d-%02d'%(y,m)
st={'users/u1/data/settings':{'cats':{'Revenu':['Salaire'],'Dépenses fixes':['Loyer'],'Dépenses variables':['Transport','Alimentation','Vêtements','Divers'],'Epargne':['Fonds urgence']},
 'budget':{md(-1):{'Salaire':300000,'Loyer':150000,'Transport':15000,'Alimentation':40000,'Vêtements':10000,'Fonds urgence':30000},cur:{'Salaire':300000,'Loyer':150000,'Transport':15000,'Alimentation':40000,'Vêtements':10000,'Fonds urgence':30000}},
 'custom':{},'modules':{'dettes':True},'dettes':[{'id':'d1','sens':'emprunt','personne':'Moussa','montant':20000,'date':'2026-10-01'}],
 'recur':[{'id':'r1','amt':500,'cat':'Dépenses variables','poste':'Alimentation','freq':'jour','debut':'2026-10-01','dernier':T.isoformat(),'auto':False,'pause':False}]}}
n=0
for k in (-2,-1,0):
    ym=md(k)
    for (p,c,a) in [('Salaire','Revenu',300000),('Loyer','Dépenses fixes',150000),('Transport','Dépenses variables',21000),('Alimentation','Dépenses variables',35000),('Divers','Dépenses variables',6000),('Fonds urgence','Epargne',20000)]:
        n+=1;st['users/u1/transactions/t%d'%n]={'amt':a,'date':ym+'-10','cat':c,'poste':p,'cmt':'','ts':ym+'-10T10:%02d:00Z'%n}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':844},service_workers='block');pg=ctx.new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    for k,v in [('**/firebase-app.js',stub.APP),('**/firebase-auth.js',stub.AUTH),('**/firebase-firestore.js',stub.FS(json.dumps(st)))]:pg.route(k,(lambda v: lambda r: r.fulfill(body=v,content_type='text/javascript'))(v))
    pg.route('https://fonts.**',lambda r:r.abort())
    # simule le 26 et le 3 en remplaçant todayStr
    pg.goto('http://localhost:8784/');pg.wait_for_timeout(1500)
    pg.evaluate("window._todayReal=todayStr;todayStr=()=>_todayReal().slice(0,8)+'26';renderDash()");pg.wait_for_timeout(200)
    print('prep carte:',pg.evaluate("document.getElementById('prep-dash').innerText.replace(/\\n/g,' | ')"))
    pg.evaluate("openPrepBudget()");pg.wait_for_timeout(200);print(pg.evaluate("document.getElementById('cpt-sheet').innerText"))
    pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'pm1.png')
    pg.click('#pb-go');pg.wait_for_timeout(400);print('budget suivant:',pg.evaluate(f"JSON.stringify(budget['{md(1)}'])"))
    pg.evaluate("todayStr=()=>_todayReal().slice(0,8)+'03';renderDash()");pg.wait_for_timeout(200)
    print('bilan mois carte:',pg.evaluate("document.getElementById('bilanm-dash').innerText.replace(/\\n/g,' | ')"))
    pg.evaluate(f"openBilanMois('{md(-1)}')");pg.wait_for_timeout(200);print(pg.evaluate("document.getElementById('cpt-sheet').innerText"))
    pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'pm2.png');pg.evaluate("closeSheet()")
    pg.evaluate("lancerGuide()");pg.wait_for_timeout(500);pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'g1.png')
    pg.evaluate("guideI++;guideEtape()");pg.wait_for_timeout(200);pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'g2.png')
    pg.evaluate("finGuide()");print('guide fini',pg.evaluate("localStorage.getItem('fiinas-guide')"))
    print(errs);b.close()
srv.kill()
