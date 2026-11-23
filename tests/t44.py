# Bilan de la semaine : dépassements nets, « tu peux encore dépenser », fin du mois, « Je peux me le permettre ? »
import os,sys,subprocess,time,json,datetime;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from stub import page
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8771'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
today=datetime.date.today();lun=today-datetime.timedelta(days=today.weekday()+7)
ym=today.strftime('%Y-%m');d=lambda k:(lun+datetime.timedelta(days=k)).isoformat()
d1=today.replace(day=1).isoformat()
st={'users/u1/data/settings':{'cats':{'Revenu':['Salaire'],'Dépenses fixes':['Loyer'],'Dépenses variables':['Imprévus','Dons','Alimentation','Transport'],'Epargne':['Epargne projet']},
  'budget':{ym:{'Salaire':400000,'Loyer':135000,'Imprévus':10000,'Dons':10000,'Alimentation':60000,'Transport':30000,'Epargne projet':100000}},'custom':{},'modules':{}}}
T=[(400000,d1,'Revenu','Salaire'),(135000,d1,'Dépenses fixes','Loyer'),(86625,d(1),'Dépenses variables','Imprévus'),(10000,d1,'Dépenses variables','Imprévus'),(16500,d(2),'Dépenses variables','Dons'),(28000,d1,'Dépenses variables','Dons'),(2550,d(3),'Dépenses variables','Alimentation'),(20000,d1,'Dépenses variables','Alimentation'),(750,d(4),'Dépenses variables','Transport')]
for i,(a,dt,c,p) in enumerate(T): st[f'users/u1/transactions/t{i}']={'amt':a,'date':dt,'cat':c,'poste':p,'ts':dt+'T10:00:00Z'}
try:
  with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg,errs=page(b,json.dumps(st));pg.wait_for_timeout(500)
    B=pg.evaluate(f"(()=>{{const B=bilanCalc('{lun.isoformat()}');return {{h:B.horsBudget,dm:B.depasseMois,rv:B.resteVarNet,t:bilanTitre(B)}}}})()")
    print(B)
    pg.evaluate(f"openBilan('{lun.isoformat()}')");pg.wait_for_timeout(400)
    txt=pg.inner_text('#cpt-sheet') if pg.locator('#cpt-sheet').count() else pg.inner_text('body')
    for k in ['Tu peux encore dépenser','Budget du mois','tiendront leur budget','déjà dépassé leur budget','budget du mois dépassé de']: print(k,':',k in txt)
    pg.fill('#pp-lib','Tele');pg.fill('#pp-amt','50000');pg.evaluate('peutPermettre()');print('PP:',pg.inner_text('#pp-rep'))
    pg.fill('#pp-amt','5000');pg.evaluate('peutPermettre()');print('PP5000:',pg.inner_text('#pp-rep'))
    print('errors',errs)
finally: srv.terminate()
