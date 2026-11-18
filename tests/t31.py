import os
import sys,subprocess,time,datetime,json,random;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import stub
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8781'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
T=datetime.date.today();random.seed(3)
store={}
n=0
def tx(d,amt,cat,poste,cmt='',c='wv'):
    global n;n+=1;store['users/u1/transactions/t%d'%n]={'amt':amt,'date':d.isoformat(),'cat':cat,'poste':poste,'cmt':cmt,'compte':c,'ts':d.isoformat()+'T12:%02d:00Z'%(n%60)}
for i in range(1,60):
    d=T-datetime.timedelta(days=i)
    if d.weekday()==2 and i<10: continue
    tx(d,random.choice([500,700,1000,1200]),'Dépenses variables','Transport','bus')
    if random.random()<.6: tx(d,random.choice([1500,2500,4000]),'Dépenses variables','Alimentation')
    if d.weekday()==5: tx(d,8000,'Dépenses variables','Loisirs','sortie')
    if random.random()<.3: tx(d,random.choice([300,500,800]),'Dépenses variables','Divers','café')
lun=T-datetime.timedelta(days=T.weekday()+7)
tx(lun+datetime.timedelta(days=3),7000,'Dépenses variables','Transport','Taxi aéroport')
tx(lun+datetime.timedelta(days=1),150000,'Dépenses fixes','Loyer','loyer')
tx(T.replace(day=1),300000,'Revenu','Salaire','',)
ym=T.isoformat()[:7]
S={'cats':{'Revenu':['Salaire'],'Dépenses fixes':['Loyer','Électricité'],'Dépenses variables':['Transport','Alimentation','Loisirs','Divers'],'Epargne':['Fonds urgence']},
 'budget':{ym:{'Salaire':300000,'Loyer':150000,'Électricité':15000,'Transport':15000,'Alimentation':40000,'Loisirs':20000,'Fonds urgence':30000}},'custom':{},'modules':{'comptes':True,'dettes':True},
 'comptes':[{'id':'wv','nom':'Wave','type':'wave','solde0':200000}],
 'dettes':[{'id':'d1','sens':'emprunt','personne':'Moussa','montant':20000,'date':'2026-10-01','echeance':(T+datetime.timedelta(days=3)).isoformat()}],
 'recur':[{'id':'r1','amt':15000,'cat':'Dépenses fixes','poste':'Électricité','freq':'mois','jour':(T+datetime.timedelta(days=2)).day,'debut':'2026-10-01','dernier':T.isoformat(),'auto':False,'pause':False}]}
store['users/u1/data/settings']=S
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_context(viewport={'width':390,'height':844},service_workers='block').new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    for k,v in [('**/firebase-app.js',stub.APP),('**/firebase-auth.js',stub.AUTH),('**/firebase-firestore.js',stub.FS(json.dumps(store)))]:pg.route(k,(lambda v: lambda r: r.fulfill(body=v,content_type='text/javascript'))(v))
    pg.route('https://fonts.**',lambda r:r.abort());pg.goto('http://localhost:8781/');pg.wait_for_timeout(1800)
    print('carte:',pg.evaluate("document.getElementById('bilan-dash').innerText.replace(/\\n/g,' | ')"))
    pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'bl0.png')
    pg.evaluate("openBilan(bilanLundiCourant())");pg.wait_for_timeout(300)
    print(pg.evaluate("document.getElementById('cpt-sheet').innerText"))
    for i,(lib,amt,po) in enumerate([('Courses',5000,'Alimentation'),('Téléphone',150000,''),('Frigo',60000,'')]):
        pg.evaluate(f"document.getElementById('pp-lib').value='{lib}';document.getElementById('pp-amt').value='{amt}';document.getElementById('pp-poste').value='{po}';peutPermettre()")
        print('PP',lib,':',pg.evaluate("document.getElementById('pp-rep').innerText.replace(/\\n/g,' ')"))
    pg.evaluate("document.querySelector('#cpt-sheet > div').scrollTop=0");pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'bl1.png')
    pg.evaluate("document.querySelector('#cpt-sheet > div').scrollTop=700");pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'bl2.png')
    print(errs);b.close()
srv.kill()
