# Enveloppes : accueil trié (rouge, puis dernières utilisées), dépensé / reste ; détail avec dépenses ; Historique « Cette période »
import os,sys,subprocess,time,json,datetime as dt;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from stub import page
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8771'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
V,F='Dépenses variables','Dépenses fixes'
rep={'Loyer':135000,'Alimentation':10000,'Transport':5000,'Santé':7000,'Famille et dons':30000}
env={'actif':True,'depart':'2026-11-26','dernierePaie':'2026-11-25','ids0':[],'ar0':187000,'initial':{},'habit':{},'mv':[{'id':'m'+str(i),'d':'2026-11-26','de':'_','vers':p,'amt':v,'t':'rep'} for i,(p,v) in enumerate(rep.items())]}
st={'users/u1/data/settings':{'cats':{'Revenu':['Salaire'],'Dépenses fixes':['Loyer'],'Dépenses variables':['Alimentation','Transport','Santé','Famille et dons'],'Epargne':['Epargne']},'budget':{},'custom':{},'modules':{},'env':env}}
T=[(135000,'2026-11-26',F,'Loyer',''),(15000,'2026-11-26',V,'Famille et dons','Don mosquée'),(5000,'2026-11-26',V,'Famille et dons','Tonton Modou'),(6500,'2026-11-27',V,'Transport','Taxi'),(3500,'2026-11-28',V,'Alimentation','Marché')]
for i,(a,d,c,p,cm) in enumerate(T): st[f'users/u1/transactions/t{i}']={'amt':a,'date':d,'cat':c,'poste':p,'cmt':cm,'ts':d+'T15:00:00Z'}
try:
  with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg,errs=page(b,json.dumps(st),now=dt.datetime(2026,11,28,18))
    t=pg.inner_text('#env-dash').replace(' ',' ').split('Mes enveloppes')[1].split('Toutes')[0]
    print(t.replace('\n',' | '))
    pg.evaluate("openEnv('Famille et dons')");pg.wait_for_timeout(200)
    d=pg.inner_text('#cpt-sheet').replace(' ',' ');print('---',d.replace('\n',' | ')[:420])
    pg.click("#cpt-sheet >> text=Tout l'historique de Famille et dons");pg.wait_for_timeout(300);print('historique filtré:',pg.evaluate('txPosteFilter'))
    pg.evaluate("clearPosteFilter()");pg.wait_for_timeout(100)
    pg.click('#tx-periode button');pg.wait_for_timeout(200);print('cette période:',pg.locator('#page-tx').inner_text().count('Loyer')>0, pg.evaluate('txPeriode'))
    print('errors',errs)
finally: srv.terminate()
