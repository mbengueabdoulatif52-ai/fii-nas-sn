import os
import sys,subprocess,time;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import stub
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8771'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
A="{'users/u1/data/settings':{cats:{'Revenu':['Salaire'],'Dépenses fixes':['Loyer'],'Dépenses variables':['Alimentation'],'Epargne':['Tontine']},budget:{'2026-11':{'Salaire':776200,'Loyer':700000,'Alimentation':100000,'Tontine':39400},'2026-12':{'Salaire':776200,'Loyer':600000,'Alimentation':100000,'Tontine':31200}},custom:{}},'users/u1/transactions/t1':{amt:776200,date:'2026-11-01',cat:'Revenu',poste:'Salaire',ts:'2026-11-01T10:00:00Z'},'users/u1/transactions/t2':{amt:815025,date:'2026-11-02',cat:'Dépenses fixes',poste:'Loyer',ts:'2026-11-02T10:00:00Z'}}"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg,errs=stub.page(b,A);pg.wait_for_timeout(900)
    pg.evaluate("goP('bud',document.querySelectorAll('.ni')[3])");pg.wait_for_timeout(300)
    pg.locator('#bud-solde').screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'bs1.png')
    pg.evaluate("setBYM('2026',12)");pg.wait_for_timeout(300)
    pg.locator('#bud-solde').screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'bs2.png')
    print(pg.inner_text('#bud-solde').replace('\n',' | '),errs);b.close()
srv.kill()
