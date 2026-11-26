# Poches : pointage des comptes et prêt abandonné ; poches et comptes restent d'accord. (Base : t53) Tout passe par « À répartir » ; poches et comptes restent d'accord ; carte accueil ; reprendre
import os,sys,subprocess,time,json,datetime as dt;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from stub import page
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8771'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
def b36(n):
  c='0123456789abcdefghijklmnopqrstuvwxyz';s=''
  while n:s=c[n%36]+s;n//=36
  return s
ms=lambda iso:int(dt.datetime.fromisoformat(iso+'+00:00').timestamp()*1000)
V='Dépenses variables'
t0=ms('2026-11-26T08:00:00')
# Avant le démarrage : prêt de 30 000 à Ibou le 20/11 depuis Wave (Wave avait 330 000, il en reste 300 000 au démarrage)
dettes=[{'id':'d'+b36(ms('2026-11-20T10:00:00')),'sens':'pret','personne':'Ibou','montant':30000,'date':'2026-11-20','compte':'w','credit':False},
  {'id':'d'+b36(ms('2026-11-26T07:00:00')),'sens':'pret','personne':'Avant (même jour)','montant':4000,'date':'2026-11-26','compte':'w','credit':False}]
env={'actif':True,'t0':t0,'depart':'2026-11-26','ids0':[],'ar0':296000,'initial':{},'habit':{},'mv':[{'id':'r1','d':'2026-11-26','de':'_','vers':'Alimentation','amt':50000,'t':'rep'},{'id':'r2','d':'2026-11-26','de':'_','vers':'Santé','amt':20000,'t':'rep'}]}
st={'users/u1/data/settings':{'cats':{'Revenu':['Salaire'],'Dépenses fixes':['Loyer'],'Dépenses variables':['Alimentation','Santé','Équipement'],'Epargne':['Tabaski']},'budget':{},'custom':{},
  'modules':{'comptes':True,'dettes':True},'comptes':[{'id':'w','nom':'Wave','type':'mobile','solde0':330000}],'dettes':dettes,'env':env},
  'users/u1/transactions/t1':{'amt':10000,'date':'2026-11-27','cat':V,'poste':'Alimentation','cmt':'Marché','compte':'w','ts':'2026-11-27T10:00:00Z'}}
N=lambda s:s.replace(' ',' ').replace('\xa0',' ')
try:
  with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg,errs=page(b,json.dumps(st),now=dt.datetime(2026,11,28,18))
    chk=lambda lab:print(lab,pg.evaluate("(()=>{const C=envCalc();return {ar:C.ar,tot:C.tot,comptes:totalComptes(),accord:C.tot===totalComptes()}})()"))
    chk('départ (dettes d\'avant ignorées) :')
    pg.evaluate("(async()=>{const{db,collection,addDoc}=window._fb;await addDoc(collection(db,dataPath()+'/mouvements'),{type:'ajustement',compte:'w',amt:-3000,date:'2026-11-28',ts:'2026-11-28T17:00:00Z'});})()");pg.wait_for_timeout(500)
    chk('après pointage −3 000 :')
    i=pg.evaluate("dettes.find(d=>d.personne==='Ibou').id")
    pg.evaluate(f"openAbandon && openAbandon('{i}')");pg.wait_for_timeout(300)
    pg.click('#ab-go');pg.wait_for_timeout(600)
    chk('après abandon du prêt à Ibou (20 000 restants) :')
    print('errors',errs)
finally: srv.terminate()
