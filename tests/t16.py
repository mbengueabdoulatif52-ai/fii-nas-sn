import os
import sys,subprocess,time;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import stub
from playwright.sync_api import sync_playwright
stub.AUTH=stub.AUTH.replace("displayName:'Awa Diop'","displayName:'abdou latif mbengue'")
srv=subprocess.Popen(['python3','-m','http.server','8771'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
P=[('Aides versées',157000,135000),('Achats divers',36400,10000),('Alimentation',54000,50000),('Dons',16900,10000),('Prêts',25000,10000),('Loisir',9000,8000)]
T=[f"'users/u1/transactions/r1':{{amt:776200,date:'2026-11-01',cat:'Revenu',poste:'Salaire net',ts:'2026-11-01T10:00:00Z'}}",f"'users/u1/transactions/a0':{{amt:250000,date:'2026-11-02',cat:'Dépenses fixes',poste:'Mensualité de prêt',ts:'2026-11-02T10:00:00Z'}}"]+[f"'users/u1/transactions/a{i}':{{amt:{a},date:'2026-11-0{3+i%5}',cat:'Dépenses variables',poste:'{p}',ts:'2026-11-03T10:00:00Z'}}" for i,(p,a,bud) in enumerate(P)]
B=",".join(f"'{p}':{bud}" for p,a,bud in P)+",'Mensualité de prêt':250000"
A="{'users/u1/data/settings':{cats:{'Revenu':['Salaire net'],'Dépenses fixes':['Mensualité de prêt'],'Dépenses variables':["+",".join(f"'{p}'" for p,a,b in P)+"]},budget:{'2026-11':{"+B+"}},custom:{}},'users/u1/transactions/old':{amt:900000,date:'2025-01-05',cat:'Dépenses fixes',poste:'Mensualité de prêt',ts:'2025-01-05T10:00:00Z'},"+",".join(T)+"}"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg,errs=stub.page(b,A);pg.wait_for_timeout(900)
    print('ordre:',pg.evaluate("[...document.querySelectorAll('#page-dash > div')].filter(d=>d.innerHTML.trim()&&d.offsetHeight).map(d=>d.id||d.className).join(' > ')"))
    print('nom:',pg.inner_text('#uname'),'| ligne début:',pg.locator('text=Depuis le début').count())
    print('À surveiller:',pg.inner_text('#watch').replace('\n',' | '))
    pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'w.png',full_page=True);print(errs);b.close()
srv.kill()
