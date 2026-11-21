# Import Excel : formats de date et de montant, postes inconnus créés, lignes illisibles ignorées
import os,sys,subprocess,time;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from stub import page
from playwright.sync_api import sync_playwright
srv=subprocess.Popen(['python3','-m','http.server','8771'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
try:
  with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg,errs=page(b,"{'users/u1/data/settings':{cats:{'Revenu':['Salaire'],'Dépenses variables':['Transport']},budget:{},custom:{},modules:{}}}")
    pg.evaluate("goP('imp',null)");pg.wait_for_timeout(300)
    print('aide affichée:','5 colonnes' in pg.inner_text('#page-imp'))
    rows=["05/11/2026\tDépenses variables\tTransport\t2 500\tYango","6/11/26\tdepenses variables\tScolarité\t15.000\tÉcole","2026-11-07\tRevenu\tSalaire\t450,000\t","31/02/2026\tRevenu\tSalaire\t1000\t","nov 5\tRevenu\tSalaire\t1000\t"]
    pg.fill('#imp-txt',"\n".join(rows));pg.click('#imp-btn');pg.wait_for_timeout(1500)
    print('importées:',pg.evaluate("JSON.stringify(txs.map(t=>[t.date,t.poste,t.amt]).sort())"))
    print('poste créé:',pg.evaluate("CATS['Dépenses variables'].includes('Scolarité')"))
    pg.fill('#imp-txt',rows[0]);pg.click('#imp-btn');pg.wait_for_timeout(800);print('doublon:',pg.inner_text('#imp-pt'))
    print('errors',errs)
finally: srv.terminate()
