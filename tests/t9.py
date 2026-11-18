import os
import sys,subprocess,time;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from stub import page
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8771'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
A="""{'users/u1/data/settings':{cats:{'Revenu':['Salaire'],'Dépenses variables':['Alimentation','Famille et dons']},budget:{},custom:{},modules:{comptes:true,dettes:true},
comptes:[{id:'wv',nom:'Wave',type:'wave',solde0:151000},{id:'es',nom:'Espèces',type:'especes',solde0:10000},{id:'bq',nom:'CBAO',type:'banque',solde0:150000}]}}"""
S=lambda pg:pg.evaluate("comptes.map(c=>c.nom+':'+soldeCompte(c)).join(' | ')")
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg,errs=page(b,A);pg.wait_for_timeout(800)
    pg.evaluate("goP('add',document.querySelectorAll('.ni')[2])");pg.wait_for_timeout(300)
    pg.click("#f-cpt-wrap >> text=Espèces")
    pg.fill('#f-amt','40000');pg.dispatch_event('#f-amt','input')
    pg.click('#bsave');pg.wait_for_timeout(300)
    print('warn affiché:',pg.locator('#f-cpt-wrap-warn').inner_text()[:60].replace('\n',' / '))
    pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'p1_warn.png',full_page=True)
    pg.click("#f-cpt-wrap-warn >> text=Payer avec plusieurs comptes");pg.wait_for_timeout(200)
    print('parts:',pg.evaluate("JSON.stringify(PAY.add.parts)"),pg.inner_text('#f-cpt-wrap-st'))
    pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'p2_multi.png',full_page=True)
    pg.click('#bsave');pg.wait_for_timeout(500)
    print('après dépense répartie:',S(pg),pg.evaluate("JSON.stringify(txs[0].parts)"))
    # répartition invalide
    pg.evaluate("goP('add',document.querySelectorAll('.ni')[2])");pg.wait_for_timeout(200)
    pg.fill('#f-amt','5000');pg.dispatch_event('#f-amt','input');pg.click("#f-cpt-wrap >> text=+ Payer avec plusieurs comptes");pg.wait_for_timeout(100)
    inp=pg.locator('#f-cpt-wrap input.finp').nth(0);inp.fill('1000');inp.dispatch_event('input');inp=pg.locator('#f-cpt-wrap input.finp').nth(1);inp.fill('1000');inp.dispatch_event('input')
    pg.click('#bsave');pg.wait_for_timeout(200);print('invalide:',pg.inner_text('#fmsg'))
    # banque découvert : pas de blocage
    pg.click("#f-cpt-wrap >> text=Un seul compte");pg.click("#f-cpt-wrap >> text=CBAO");pg.fill('#f-amt','200000');pg.dispatch_event('#f-amt','input');pg.wait_for_timeout(100)
    print('note banque:',pg.locator('#f-cpt-wrap').inner_text().split('\n')[-2])
    pg.click('#bsave');pg.wait_for_timeout(400);print('après banque:',S(pg))
    # « enregistrer quand même »
    pg.evaluate("goP('add',document.querySelectorAll('.ni')[2])");pg.wait_for_timeout(200)
    pg.click("#f-cpt-wrap >> text=Espèces");pg.fill('#f-amt','3000');pg.dispatch_event('#f-amt','input');pg.click('#bsave');pg.wait_for_timeout(200)
    pg.click("#f-cpt-wrap-warn >> text=Corriger le solde d'Espèces");pg.fill('#f-cpt-wrap-cor','5000');pg.click("#f-cpt-wrap-warn >> text=OK");pg.wait_for_timeout(300)
    print('après correction, warn:',pg.locator('#f-cpt-wrap-warn').inner_text()[:30],'|',S(pg))
    pg.click('#bsave');pg.wait_for_timeout(400);print('après dépense espèces:',S(pg))
    # prêt réparti
    pg.evaluate("goP('det',null)");pg.wait_for_timeout(200);pg.evaluate("openAddDette()")
    pg.fill('#nd-pers','Moussa');pg.fill('#nd-amt','60000');pg.dispatch_event('#nd-amt','input')
    pg.click("#nd-cpt-wrap >> text=Espèces");pg.click('#nd-go');pg.wait_for_timeout(200)
    print('warn prêt:',pg.locator('#nd-cpt-wrap-warn').inner_text()[:40].replace('\n',' / '))
    pg.click("#nd-cpt-wrap-warn >> text=Payer avec plusieurs comptes");pg.wait_for_timeout(100)
    print('note prêt:',pg.inner_text('#nd-note'))
    pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'p3_pret.png')
    pg.click('#nd-go');pg.wait_for_timeout(400);print('après prêt:',S(pg),pg.evaluate("JSON.stringify(dettes[0].parts)"))
    # remboursement réparti reçu
    pg.evaluate("openRemb(dettes[0].id)");pg.wait_for_timeout(100)
    pg.click("#rb-pay >> text=+ Recevoir avec plusieurs comptes");pg.wait_for_timeout(100)
    pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'p4_remb.png')
    pg.click('#rb-go');pg.wait_for_timeout(400);print('après remb:',S(pg),pg.evaluate("dettes.map(d=>resteDette(d))"))
    # modification d'une transaction répartie
    tid=pg.evaluate("txs.find(t=>t.parts).id");pg.evaluate(f"openEditTx('{tid}')");pg.wait_for_timeout(200)
    print('edit mode:',pg.evaluate("PAY.edit.mode"),pg.evaluate("JSON.stringify(PAY.edit.parts)"))
    pg.fill('#e-amt','45 000');pg.dispatch_event('#e-amt','input');pg.evaluate("saveEditTx()");pg.wait_for_timeout(200)
    print('edit invalide → modal ouvert:',pg.is_visible('#edit-modal'))
    pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'p5_edit.png')
    pg.evaluate("goP('tx',document.querySelectorAll('.ni')[1])");pg.wait_for_timeout(200)
    print('historique:',pg.locator('.txi').first.inner_text().replace('\n',' / ')[:120])
    print('errors',errs);b.close()
srv.kill()
