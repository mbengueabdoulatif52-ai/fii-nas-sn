# Mode enveloppes : démarrage, répartition « comme d'habitude », dépense, enveloppe dans le rouge, puiser dans l'épargne, invariant
import os,sys,subprocess,time,json,datetime as dt;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from stub import page
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8771'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
st={'users/u1/data/settings':{'cats':{'Revenu':['Salaire'],'Dépenses fixes':['Loyer'],'Dépenses variables':['Alimentation','Imprévus'],'Epargne':['Tabaski']},
 'budget':{'2026-11':{'Salaire':400000,'Loyer':100000,'Alimentation':60000,'Imprévus':10000,'Tabaski':20000}},'custom':{},'modules':{'objectifs':True},
 'objectifs':[{'id':'o1','nom':'Tabaski','poste':'Tabaski','cible':250000,'echeance':'2027-05','depart':130000}]}}
T=[(400000,'2026-11-01','Revenu','Salaire'),(100000,'2026-11-02','Dépenses fixes','Loyer'),(20000,'2026-11-26','Dépenses variables','Alimentation'),(400000,'2026-12-01','Revenu','Salaire')]
for i,(a,d,c,p) in enumerate(T): st[f'users/u1/transactions/t{i}']={'amt':a,'date':d,'cat':c,'poste':p,'ts':d+'T10:00:00Z'}
E=lambda pg,s:pg.evaluate(s)
try:
  with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg,errs=page(b,json.dumps(st),now=dt.datetime(2026,11,26,14))
    E(pg,"goP('pro',document.querySelectorAll('.ni')[4])");pg.wait_for_timeout(200)
    print('caché par défaut:',not pg.locator('#env-card').is_visible())
    for _ in range(7): pg.click('#version-app')
    pg.wait_for_timeout(200);print('visible en développeur:',pg.locator('#env-card').is_visible())
    pg.click('#env-ui >> text=Passer aux enveloppes');pg.wait_for_timeout(300)
    print('futur signalé:','1 transaction datée dans le futur' in pg.inner_text('#cpt-sheet'))
    print('épargne pré-remplie:',pg.input_value('[data-ep="Tabaski"]'))
    pg.click('text=Les remettre à aujourd\'hui');pg.wait_for_timeout(500)
    print('redaté:',E(pg,"txs.find(t=>t.id==='t3').date"))
    pg.fill('#es-tot','650 000');pg.wait_for_timeout(100);print('info:',pg.inner_text('#es-info'))
    pg.click('#es-go');pg.wait_for_timeout(900)
    C=E(pg,"(()=>{const C=envCalc();return{ar:C.ar,tot:C.tot,tab:C.sol['Tabaski']}})()");print('après démarrage:',C)
    print('répartir ouvert:','Répartir' in pg.inner_text('#cpt-sheet'))
    pg.click('text=Comme d\'habitude');pg.wait_for_timeout(200);print('reste:',pg.inner_text('#rp-reste').replace('\n',' '))
    pg.click('#rp-go');pg.wait_for_timeout(500)
    C=E(pg,"(()=>{const C=envCalc();return{ar:C.ar,tot:C.tot,sol:C.sol}})()");print('après répartition:',C)
    print('accueil:',pg.inner_text('#env-dash').replace('\n',' | ')[:220])
    print('hero caché:',not pg.locator('#hero').is_visible(),'· onglet:',E(pg,"document.querySelectorAll('.ni')[3].innerText"))
    # dépense de 15 000 en Imprévus (enveloppe à 10 000) via le formulaire
    E(pg,"goP('add',document.querySelectorAll('.ni')[2])");pg.wait_for_timeout(300)
    pg.fill('#f-amt','15000');pg.locator('#page-add .chip.v').click();pg.wait_for_timeout(200);pg.select_option('#f-poste','Imprévus');pg.wait_for_timeout(200)
    print('saisie:',pg.inner_text('#f-reste').replace('\n',' '))
    pg.click('#page-add .btn-p, #page-add button:has-text("Enregistrer")');pg.wait_for_timeout(700)
    print('imprévus:',E(pg,"envSolde('Imprévus')"))
    E(pg,"goP('dash',document.querySelectorAll('.ni')[0])");pg.wait_for_timeout(300)
    E(pg,"openEnv('Imprévus')");pg.wait_for_timeout(200);pg.click('#cpt-sheet >> text=Combler');pg.wait_for_timeout(200)
    pg.select_option('#dp-de','Tabaski');pg.wait_for_timeout(100);print('puiser:',pg.inner_text('#dp-info'),'· montant',pg.input_value('#dp-amt'))
    pg.click('#dp-go');pg.wait_for_timeout(500)
    C=E(pg,"(()=>{const C=envCalc();return{ar:C.ar,tot:C.tot,imp:C.sol['Imprévus'],tab:C.sol['Tabaski'],obj:progObj(objectifs[0])}})()");print('après comblement:',C)
    E(pg,"openEnv('Tabaski')");pg.wait_for_timeout(200);print('enveloppe épargne:','puisé 5' in pg.inner_text('#cpt-sheet').replace(' ',' '))
    # invariant : total = départ + entrées − dépenses depuis le départ
    print('invariant:',E(pg,"envCalc().tot")==650000-15000)
    E(pg,"closeSheet();goP('bud',document.querySelectorAll('.ni')[3])");pg.wait_for_timeout(300);print('onglet enveloppes:','À répartir' in pg.inner_text('#env-page'))
    # désactivation
    E(pg,"goP('pro',document.querySelectorAll('.ni')[4])");pg.click('#env-ui >> text=Revenir au budget par mois');pg.wait_for_timeout(300)
    pg.click('#cfm button:has-text("Revenir au budget")');pg.wait_for_timeout(400);print('désactivé:',not E(pg,'envOn()'),E(pg,"document.querySelectorAll('.ni')[3].innerText"))
    print('errors',errs)
finally: srv.terminate()
