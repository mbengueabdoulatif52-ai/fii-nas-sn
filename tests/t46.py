# Accueil : bascule Résumé / Graphiques, mémorisée, quatre graphiques cohérents
import os,sys,subprocess,time,json,datetime as dt;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from stub import page
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8771'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
st={'users/u1/data/settings':{'cats':{'Revenu':['Salaire'],'Dépenses fixes':['Loyer'],'Dépenses variables':['Alimentation','Dons'],'Epargne':['Epargne']},
 'budget':{'2026-11':{'Salaire':300000,'Loyer':100000,'Alimentation':60000,'Dons':10000}},'custom':{},'modules':{}}}
T=[(300000,'2026-11-01','Revenu','Salaire'),(100000,'2026-11-02','Dépenses fixes','Loyer'),(30000,'2026-11-05','Dépenses variables','Alimentation'),(25000,'2026-11-12','Dépenses variables','Dons'),(200000,'2026-10-01','Revenu','Salaire'),(250000,'2026-10-03','Dépenses fixes','Loyer')]
for i,(a,d,c,p) in enumerate(T): st[f'users/u1/transactions/t{i}']={'amt':a,'date':d,'cat':c,'poste':p,'ts':d+'T10:00:00Z'}
try:
  with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg,errs=page(b,json.dumps(st),now=dt.datetime(2026,11,20,12))
    print('bascule visible:',pg.locator('#vue-sw').is_visible(),'graphs caché:',not pg.locator('#graphs').is_visible())
    pg.click('#vue-sw >> text=Graphiques');pg.wait_for_timeout(300)
    g=pg.inner_text('#graphs').replace(' ',' ')
    print('hero caché:',not pg.locator('#hero').is_visible())
    print('rythme:','155 000 F dépensés au 20' in g and 'budget 170 000 F' in g)
    print('dons rouge:','25 000 / 10 000' in g and '1 poste au-delà' in g)
    print('anneau:','Loyer' in g and '65 %' in g)
    print('6 mois:','Moyenne avant' in g and '−50 000' in g)
    pg.reload();pg.wait_for_timeout(1200);print('mémorisé:',pg.locator('#graphs').is_visible())
    pg.click('#vue-sw >> text=Résumé');pg.wait_for_timeout(200);print('retour résumé:',pg.locator('#hero').is_visible())
    print('errors',errs)
finally: srv.terminate()
