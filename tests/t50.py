# Cas réel d'Abdou : démarrage le 26 nov. à 716 200 F (dont 25 300 d'épargne), tout réparti, 295 000 F dépensés le jour même
import os,sys,subprocess,time,json,datetime as dt;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from stub import page
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8771'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
rep={'Loyer':135000,'Aides versées':140000,'Mensualités de prêt':227000,'Electricité':15000,'Eau':10000,'Abonnements':34900,'Assurances':20000,'Frais bancaires':8000,'Téléphone et internet':3500,'Alimentation':10000,'Transport':5000,'Santé':7000,'Famille et dons':30000,'Loisirs':7000,'Voitures':5000,'Imprévus':33500}
assert sum(rep.values())==690900
env={'actif':True,'depart':'2026-11-26','ids0':[],'ar0':690900,'initial':{'Epargne':25300},'habit':{},'mv':[{'id':'m'+str(i),'d':'2026-11-26','de':'_','vers':p,'amt':v,'t':'rep'} for i,(p,v) in enumerate(rep.items())]}
st={'users/u1/data/settings':{'cats':{'Revenu':['Salaire'],'Dépenses fixes':['Loyer','Aides versées','Mensualités de prêt','Electricité','Eau','Abonnements','Assurances','Frais bancaires','Téléphone et internet'],'Dépenses variables':['Alimentation','Transport','Santé','Famille et dons','Loisirs','Voitures','Imprévus'],'Epargne':['Epargne']},'budget':{},'custom':{},'modules':{},'env':env}}
for i,(a,p,c) in enumerate([(140000,'Aides versées','Dépenses fixes'),(20000,'Famille et dons','Dépenses variables'),(135000,'Loyer','Dépenses fixes')]):
    st[f'users/u1/transactions/t{i}']={'amt':a,'date':'2026-11-26','cat':c,'poste':p,'ts':'2026-11-26T15:00:00Z'}
try:
  with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg,errs=page(b,json.dumps(st),now=dt.datetime(2026,11,26,16))
    C=pg.evaluate("(()=>{const C=envCalc();return{tot:C.tot,ar:C.ar}})()");print('total:',C,'attendu 421 200')
    t=pg.inner_text('#env-dash').replace(' ',' ');print('sans paie expliqué:','Aucune paie notée' in t)
    print('pas de fausse alerte (don ponctuel):','Ne tiendra pas' not in t)
    print('tableaux budget masqués:',not pg.locator('#dm').is_visible())
    pg.evaluate("setVue(true)");pg.wait_for_timeout(300);g=pg.inner_text('#graphs').replace(' ',' ')
    print('graphique:',[l for l in g.split('\n') if 'prévu' in l][:2],'· trop tôt:','Trop tôt pour juger' in g)
    pg.evaluate("setVue(false);goP('bud',document.querySelectorAll('.ni')[3])");pg.wait_for_timeout(300)
    print('départ visible:','716 200' in pg.inner_text('#env-page').replace(' ',' '))
    pg.evaluate("openEnvDepart()");pg.fill('#ed-tot','720 000');pg.wait_for_timeout(100);print('info:',pg.inner_text('#ed-info'))
    pg.click('#ed-go');pg.wait_for_timeout(400);print('après correction:',pg.evaluate("envCalc().ar"),'(attendu 3 800)')
    pg.evaluate("env.dernierePaie='2026-11-25';renderCurrent()");pg.evaluate("goP('dash',document.querySelectorAll('.ni')[0])");pg.wait_for_timeout(300)
    print('période avec paie déclarée:',pg.evaluate("JSON.stringify((({mode,debut,fin,jour})=>({mode,debut,fin,jour}))(envPeriode()))"))
    pg.evaluate("setVue(true)");pg.wait_for_timeout(300);print('rythme:',[l for l in pg.inner_text('#graphs').replace('\u202f',' ').split('\n') if 'dépensés' in l])
    print('errors',errs)
finally: srv.terminate()
