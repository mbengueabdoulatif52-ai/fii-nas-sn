# Mode enveloppes : période depuis la paie, alerte « ne tiendra pas », bilan de la période précédente, de la semaine, graphiques
import os,sys,subprocess,time,json,datetime as dt;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from stub import page
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8771'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
V,F,R,E='Dépenses variables','Dépenses fixes','Revenu','Epargne'
env={'actif':True,'depart':'2026-10-20','ids0':[],'ar0':50000,'initial':{'Tabaski':100000},'habit':{'Loyer':100000,'Alimentation':60000,'Transport':20000,'Imprévus':10000,'Tabaski':20000},
 'mv':[{'id':'a1','d':'2026-10-26','de':'_','vers':'Loyer','amt':100000,'t':'rep'},{'id':'a2','d':'2026-10-26','de':'_','vers':'Alimentation','amt':60000,'t':'rep'},{'id':'a3','d':'2026-10-26','de':'_','vers':'Transport','amt':20000,'t':'rep'},{'id':'a4','d':'2026-10-26','de':'_','vers':'Imprévus','amt':10000,'t':'rep'},{'id':'a5','d':'2026-10-26','de':'_','vers':'Tabaski','amt':20000,'t':'rep'},
      {'id':'b1','d':'2026-11-20','de':'Tabaski','vers':'Imprévus','amt':15000,'t':'dep'},
      {'id':'c1','d':'2026-11-26','de':'_','vers':'Alimentation','amt':40000,'t':'rep'},{'id':'c2','d':'2026-11-26','de':'_','vers':'Loyer','amt':100000,'t':'rep'}]}
st={'users/u1/data/settings':{'cats':{'Revenu':['Salaire','Commerce'],'Dépenses fixes':['Loyer'],'Dépenses variables':['Alimentation','Transport','Imprévus'],'Epargne':['Tabaski']},'budget':{},'custom':{},'modules':{'objectifs':True},
 'objectifs':[{'id':'o1','nom':'Tabaski','poste':'Tabaski','cible':250000,'depart':0}],'env':env}}
T=[(300000,'2026-09-26',R,'Salaire'),(300000,'2026-10-26',R,'Salaire'),(15000,'2026-11-10',R,'Commerce'),(300000,'2026-11-26',R,'Salaire'),(100000,'2026-10-27',F,'Loyer'),(25000,'2026-11-18',V,'Imprévus')]
T+=[(2000,f'2026-{m:02d}-{d:02d}',V,'Alimentation') for (m,d) in [(10,x) for x in range(26,32)]+[(11,x) for x in range(1,30)]]
T+=[(1500,f'2026-11-{d:02d}',V,'Transport') for d in range(1,12)]
for i,(a,d,c,p) in enumerate(T): st[f'users/u1/transactions/t{i}']={'amt':a,'date':d,'cat':c,'poste':p,'ts':d+'T10:00:00Z'}
def voir(now,label):
    pg,errs=page(b,json.dumps(st),now=now);pg.wait_for_timeout(700)
    t=pg.inner_text('#env-dash').replace(' ',' ')
    print('==',label);print(t.split('Mes poches')[0].replace('\n',' | '))
    return pg,errs
try:
  with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg,errs=voir(dt.datetime(2026,11,30,12),'lundi 30 nov (jour 5 de la période)')
    print('période:',pg.evaluate("JSON.stringify((({mode,debut,fin,n,jour,reste})=>({mode,debut,fin,n,jour,reste}))(envPeriode()))"))
    pg.evaluate("setVue(true)");pg.wait_for_timeout(400)
    g=pg.inner_text('#graphs').replace(' ',' ');print('graphes:',g.replace('\n',' | ')[:600])
    print('errors',errs);pg.context.close()
    pg,errs=voir(dt.datetime(2026,12,10,12),'10 déc (jour 15, plus de bilan précédent)');print('errors',errs);pg.context.close()
    st['users/u1/data/settings']['env']['periode']='mois'
    pg,errs=voir(dt.datetime(2026,12,2,12),'mode mois, 2 déc');print('errors',errs);pg.context.close()
finally: srv.terminate()
