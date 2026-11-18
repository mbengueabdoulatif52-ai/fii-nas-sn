import os
import sys,subprocess,time;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from stub import page
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8771'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
tx=lambda i,amt,cat,poste,d,extra='':f"'users/u1/transactions/t{i}':{{amt:{amt},date:'2026-11-{d:02d}',cat:'{cat}',poste:'{poste}',ts:'2026-11-{d:02d}T10:00:00Z'{extra}}}"
T=[tx(1,250000,'Revenu','Salaire',1,",compte:'wv'"),tx(2,60000,'Dépenses fixes','Loyer',2,",compte:'wv'"),tx(3,48000,'Dépenses variables','Alimentation',5,",compte:'es'"),tx(4,22500,'Dépenses variables','Transport',8,",compte:'om'"),tx(5,10000,'Epargne','Epargne',9,",objectif:'o1'"),tx(6,6000,'Dépenses variables','Loisirs',10)]
A="{'users/u1/data/settings':{cats:{'Revenu':['Salaire'],'Dépenses fixes':['Loyer'],'Dépenses variables':['Alimentation','Transport','Loisirs'],'Epargne':['Epargne']},budget:{'2026-11':{'Loyer':60000,'Alimentation':70000,'Transport':20000,'Loisirs':20000}},custom:{},modules:{comptes:true,objectifs:true,dettes:true},comptes:[{id:'wv',nom:'Wave',type:'wave',solde0:20000},{id:'om',nom:'Orange Money',type:'om',solde0:40000},{id:'es',nom:'Espèces',type:'especes',solde0:10000}],objectifs:[{id:'o1',nom:'Tabaski 2027',cible:250000,echeance:'2027-05',depart:75000}],dettes:[{id:'d1',sens:'pret',personne:'Moussa',montant:50000,date:'2026-10-03',echeance:'2026-10-30'},{id:'d2',sens:'emprunt',personne:'Boutique Lamine',montant:40000,date:'2026-11-01'}]},"+",".join(T)+"}"
B="{'users/u1/data/settings':{cats:{'Revenu':['Salaire'],'Dépenses fixes':['Loyer'],'Dépenses variables':['Alimentation','Transport']},budget:{},custom:{}},"+",".join(T[:4])+"}"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for n,i in [('d_full',A),('d_simple',B)]:
        pg,errs=page(b,i);pg.wait_for_timeout(900);pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+f'{n}.png',full_page=True);print(n,errs,pg.evaluate("document.body.scrollHeight"))
        if n=='d_full':
            pg.click('text=Tout le détail ›');pg.wait_for_timeout(300);print('détail visible:',pg.is_visible('#dc'))
            pg.evaluate("document.documentElement.classList.add('light');renderDash()");pg.wait_for_timeout(200);pg.click('text=Masquer le détail');pg.wait_for_timeout(200);pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'d_light.png',full_page=True)
            pg.evaluate("document.documentElement.classList.remove('light');goP('add',document.querySelectorAll('.ni')[2])");pg.wait_for_timeout(200);pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'d_add.png')
            pg.evaluate("goP('tx',document.querySelectorAll('.ni')[1])");pg.wait_for_timeout(200);pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'d_tx.png')
    b.close()
srv.kill()
