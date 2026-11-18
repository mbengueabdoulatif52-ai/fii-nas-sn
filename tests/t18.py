import os
import sys,subprocess,time;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import stub
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8771'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
A="""{'users/u1/data/settings':{cats:{'Revenu':['Salaire'],'Dépenses variables':['Transport'],'Epargne':['Epargne projet','Epargne de précaution']},budget:{},custom:{},modules:{objectifs:true},
objectifs:[{id:'o1',nom:'Tabaski 2027',cible:250000,echeance:'2027-05',depart:50000}]},
'users/u1/transactions/t1':{amt:10000,date:'2026-11-05',cat:'Epargne',poste:'Epargne projet',objectif:'o1',ts:'2026-11-05T10:00:00Z'},
'users/u1/transactions/t2':{amt:20000,date:'2026-11-06',cat:'Epargne',poste:'Epargne de précaution',ts:'2026-11-06T10:00:00Z'}}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg,errs=stub.page(b,A);pg.wait_for_timeout(1500);pg.evaluate('renderDash()');pg.wait_for_timeout(600)
    print('migration:',pg.evaluate("JSON.stringify(objectifs.map(o=>[o.nom,o.poste,progObj(o)]))"),'| t1:',pg.evaluate("JSON.stringify([txs.find(t=>t.id==='t1').poste,txs.find(t=>t.id==='t1').objectif])"),'| postes:',pg.evaluate("JSON.stringify(getAllPostes('Epargne'))"))
    # objectif depuis un poste existant
    pg.evaluate("goP('obj',null)");pg.wait_for_timeout(200);pg.evaluate("openAddObj()");pg.click("#ob-mode >> text=Un poste existant");pg.select_option('#ob-poste','Epargne de précaution');pg.fill('#ob-cible','500000');pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'f2.png');pg.click('#ob-go');pg.wait_for_timeout(400)
    print('précaution:',pg.evaluate("progObj(objectifs.find(o=>o.poste==='Epargne de précaution'))"))
    # nouveau but
    pg.evaluate("openAddObj()");pg.fill('#ob-nom','Mariage');pg.fill('#ob-cible','2000000');pg.evaluate("document.getElementById('ob-ech').value='2027-12'");pg.click('#ob-go');pg.wait_for_timeout(400)
    print('postes après:',pg.evaluate("JSON.stringify(getAllPostes('Epargne'))"))
    # formulaire
    pg.evaluate("goP('add',document.querySelectorAll('.ni')[2])");pg.wait_for_timeout(200)
    pg.click(".cat-chips >> text=Épargne");pg.wait_for_timeout(200)
    pg.click("#f-poste-list >> text=Mariage");pg.fill('#f-amt','10000');pg.dispatch_event('#f-amt','input');pg.wait_for_timeout(100)
    print('note:',pg.inner_text('#f-obj-note'),'| champ objectif visible:',pg.is_visible('#f-obj-wrap'))
    pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'f1.png');pg.click('#bsave');pg.wait_for_timeout(500)
    print('mariage:',pg.evaluate("progObj(objectifs.find(o=>o.poste==='Mariage'))"),'| tx sans champ objectif:',pg.evaluate("txs[0].objectif===undefined"))
    # budget
    pg.evaluate("goP('bud',document.querySelectorAll('.ni')[3])");pg.wait_for_timeout(300)
    pg.click("text=Appliquer l'effort des objectifs");pg.wait_for_timeout(200)
    print('budget proposé:',pg.evaluate("['Tabaski 2027','Mariage'].map(p=>document.getElementById('bi_'+btoa(encodeURIComponent(p))).value)"))
    pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'f3.png',full_page=True)
    print('errors',errs);b.close()
srv.kill()
