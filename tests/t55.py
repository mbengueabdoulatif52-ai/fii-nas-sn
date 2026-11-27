# Relevé PDF des poches (base : t53). Tout passe par « À répartir » ; poches et comptes restent d'accord ; carte accueil ; reprendre
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
env={'actif':True,'t0':t0,'depart':'2026-11-26','ids0':[],'ar0':296000,'initial':{},'habit':{},'mv':[{'id':'r1','d':'2026-11-26','de':'_','vers':'Alimentation','amt':50000,'t':'rep'},{'id':'r2','d':'2026-11-26','de':'_','vers':'Santé','amt':20000,'t':'rep'},{'id':'r3','d':'2026-11-26','de':'_','vers':'Tabaski','amt':25300,'t':'rep'}]}
st={'users/u1/data/settings':{'cats':{'Revenu':['Salaire'],'Dépenses fixes':['Loyer'],'Dépenses variables':['Alimentation','Santé','Équipement'],'Epargne':['Tabaski']},'objectifs':[{'id':'o1','nom':'Tabaski 2027','poste':'Tabaski','cible':50000,'echeance':'2027-05'}],'budget':{},'custom':{},
  'modules':{'comptes':True,'dettes':True},'comptes':[{'id':'w','nom':'Wave','type':'mobile','solde0':330000}],'dettes':dettes,'env':env},
  'users/u1/transactions/t1':{'amt':10000,'date':'2026-11-27','cat':V,'poste':'Alimentation','cmt':'Marché','compte':'w','ts':'2026-11-27T10:00:00Z'}}
N=lambda s:s.replace(' ',' ').replace('\xa0',' ')
try:
  with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg,errs=page(b,json.dumps(st),now=dt.datetime(2026,11,28,18))
    chk=lambda lab:print(lab,pg.evaluate("(()=>{const C=envCalc();return {ar:C.ar,tot:C.tot,comptes:totalComptes(),accord:C.tot===totalComptes()}})()"))
    chk('départ (dettes d\'avant ignorées) :')
    k=[0]
    def nouveau(sens,qui,amt,credit=None):
      k[0]+=1;pg.clock.set_fixed_time(dt.datetime(2026,11,28,18,0,k[0]))
      pg.evaluate("openAddDette()");pg.wait_for_timeout(200)
      if sens=='emprunt':pg.click('#nd-seg >> text=emprunté');pg.wait_for_timeout(100)
      if credit:pg.click('#nd-credit-wrap input[type=checkbox]');pg.wait_for_timeout(100);pg.select_option('#nd-poste',credit)
      pg.fill('#nd-pers',qui);pg.fill('#nd-amt',str(amt));pg.evaluate("renderNdNote()");pg.wait_for_timeout(100)
      print('  aperçu :',N(pg.inner_text('#nd-env')).replace('\n',' | '))
      pg.click('#nd-go');pg.wait_for_timeout(500)
    nouveau('pret','Modou',20000);chk('après prêt 20 000 :')
    nouveau('emprunt','Fatou',50000);chk('après emprunt 50 000 :')
    nouveau('emprunt','Baba',150000,credit='Dépenses variables|Équipement');chk('après achat à crédit 150 000 :')
    print('  poche Équipement :',pg.evaluate("envSolde('Équipement')"))
    def remb(qui,amt):
      i=pg.evaluate(f"dettes.find(d=>d.personne==={json.dumps(qui)}).id");pg.wait_for_timeout(600);pg.evaluate(f"closeSheet();openRemb({json.dumps(i)})");pg.wait_for_timeout(300)
      pg.fill('#rb-amt',str(amt));pg.evaluate(f"rbEnvMaj({json.dumps(i)})");print('  aperçu :',N(pg.inner_text('#rb-env')).replace('\n',' | '))
      pg.click('#rb-go');pg.wait_for_timeout(500)
      if pg.is_visible('#rb-err'):print('  rb-err:',pg.inner_text('#rb-err'))
    remb('Modou',5000);chk('après Modou rend 5 000 :')
    remb('Ibou',10000);chk('après Ibou (prêt d\'avant) rend 10 000 :')
    remb('Fatou',25000);chk('après je rends 25 000 à Fatou :')
    remb('Baba',150000);chk('après je paie Baba 150 000 :')
    pg.evaluate("closeSheet();goP('dash',document.querySelectorAll('.ni')[0])");pg.wait_for_timeout(300)
    pg.evaluate("(async()=>{const{db,doc,setDoc}=window._fb;await setDoc(doc(db,dataPath()+'/transactions/e1'),{amt:10000,date:'2026-11-28',cat:'Epargne',poste:'Tabaski',cmt:'Virement épargne',compte:'w',ts:'2026-11-28T16:00:00Z'});})()");pg.wait_for_timeout(500)
    chk('après versement épargne 10 000 :')
    pg.add_script_tag(path='/tmp/jsp/node_modules/jspdf/dist/jspdf.umd.min.js');pg.wait_for_timeout(300)
    with pg.expect_download() as dl: pg.evaluate('exportPDF()')
    dl.value.save_as('/tmp/releve.pdf');print('pdf:',dl.value.suggested_filename)
    print('identité:',pg.evaluate("(()=>{const d0=envDebutPeriode(),a=envCalc(d0).tot,e=envFluxPeriode(d0),f=envCalc().tot;const dep=txEnv().filter(t=>t.date>=d0&&(ENV_DEP.includes(t.cat)||t.cat==='Epargne')).reduce((s,t)=>s+t.amt,0);return {debut:a,entre:e,fin:f,sorti:a+e-f,depenses_et_versements:dep}})()"))
    print('errors',errs)
finally: srv.terminate()
