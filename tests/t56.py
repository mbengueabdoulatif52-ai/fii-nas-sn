# Passage de tous aux poches : annonce imposée à l'ouverture, point de départ, pas d'annonce pour qui est revenu au budget par mois ni dans un Foyer
import os,sys,subprocess,time,json,datetime as dt;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from stub import page
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8771'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
V='Dépenses variables'
base={'cats':{'Revenu':['Salaire'],'Dépenses fixes':['Loyer'],'Dépenses variables':['Alimentation','Transport'],'Epargne':['Épargne']},'budget':{'2026-11':{'Loyer':100000,'Alimentation':60000,'Transport':20000,'Épargne':15000}},'custom':{},'modules':{}}
N=lambda s:s.replace(' ',' ').replace('\xa0',' ')
def compte(settings):
  st={'users/u1/data/settings':settings,'users/u1/transactions/t1':{'amt':300000,'date':'2026-11-25','cat':'Revenu','poste':'Salaire','cmt':'','ts':'2026-11-25T09:00:00Z'},
      'users/u1/transactions/t2':{'amt':8000,'date':'2026-11-26','cat':V,'poste':'Alimentation','cmt':'Marché','ts':'2026-11-26T09:00:00Z'}}
  return json.dumps(st)
try:
  with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    # 1. testeur au budget par mois : annonce imposée
    pg,errs=page(b,compte(base),now=dt.datetime(2026,11,27,18),annonce=True);pg.wait_for_timeout(500)
    print('annonce visible:',pg.is_visible('#env-annonce'),'·',N(pg.inner_text('#env-annonce')).split('\n')[1])
    pg.screenshot(path='/tmp/annonce.png')
    pg.click('#env-annonce >> text=Commencer');pg.wait_for_timeout(300)
    print('point de départ:',N(pg.inner_text('#cpt-sheet')).split('\n')[0],'· annonce partie:',not pg.is_visible('#env-annonce'))
    pg.evaluate('closeSheet()');pg.wait_for_timeout(300)
    print('fermé sans démarrer → annonce revient:',pg.is_visible('#env-annonce'))
    pg.click('#env-annonce >> text=Commencer');pg.wait_for_timeout(300)
    pg.evaluate("document.getElementById('es-paie').value='2026-11-25'");pg.fill('#es-tot','292 000');pg.evaluate('envStartMaj()');pg.click('#es-go');pg.wait_for_timeout(800)
    print('après démarrage: poches',pg.evaluate('envOn()'),'· répartir ouvert:',N(pg.inner_text('#cpt-sheet')).split('\n')[0] if pg.is_visible('#cpt-sheet') else '-')
    pg.evaluate('closeSheet()');pg.wait_for_timeout(300)
    print('plus d\'annonce:',not pg.is_visible('#env-annonce'),'· carte Poches du Profil visible:',pg.evaluate("(()=>{renderEnvProfil();return document.getElementById('env-card').style.display!=='none'})()"))
    print('errors',errs)
    # 2. revenu au budget par mois : pas d'annonce
    s2=dict(base,env={'actif':False,'depart':'2026-11-20','ar0':0,'initial':{},'habit':{},'mv':[]})
    pg,errs=page(b,compte(s2),now=dt.datetime(2026,11,27,18),annonce=True);pg.wait_for_timeout(500)
    print('revenu au budget par mois → annonce:',pg.is_visible('#env-annonce'),'· poches:',pg.evaluate('envOn()'),'· errors',errs)
    # 3. nouveau compte : bienvenue puis annonce
    pg,errs=page(b,'{}',now=dt.datetime(2026,11,27,18),annonce=True);pg.wait_for_timeout(800)
    print('nouveau: bienvenue',pg.is_visible('#onb'),'· annonce pendant la bienvenue:',pg.is_visible('#env-annonce'))
    pg.click('#onb-go');pg.wait_for_timeout(900)
    print('après la bienvenue → annonce:',pg.is_visible('#env-annonce'),'· errors',errs)
finally: srv.terminate()
