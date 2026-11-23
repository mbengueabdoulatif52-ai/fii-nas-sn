# Bilans de la semaine et du mois éprouvés sur 12 situations types
import os,sys,subprocess,time,json,datetime as dt
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from stub import page
from playwright.sync_api import sync_playwright
CATS={'Revenu':['Salaire','Commerce'],'Dépenses fixes':['Loyer','Électricité','Mensualité'],'Dépenses variables':['Alimentation','Transport','Loisirs','Dons','Imprévus','Équipement','Cadeaux'],'Epargne':['Epargne projet']}
def mk(budgets,txs):
    st={'users/u1/data/settings':{'cats':CATS,'budget':budgets,'custom':{},'modules':{}}}
    for i,(a,d,c,p) in enumerate(txs): st[f'users/u1/transactions/t{i}']={'amt':a,'date':d,'cat':c,'poste':p,'ts':d+'T10:00:00Z'}
    return json.dumps(st)
F,V,R,E='Dépenses fixes','Dépenses variables','Revenu','Epargne'
BN={'Salaire':500000,'Loyer':150000,'Électricité':20000,'Alimentation':90000,'Transport':30000,'Loisirs':20000,'Dons':15000,'Imprévus':15000,'Epargne projet':80000}
def base(ym,extra=()):
    return [(500000,ym+'-01',R,'Salaire'),(150000,ym+'-02',F,'Loyer'),(18000,ym+'-04',F,'Électricité'),(80000,ym+'-05',E,'Epargne projet')]+list(extra)
def jours(ym,a,b,amt,poste,cat=V,step=1): return [(amt,f'{ym}-{d:02d}',cat,poste) for d in range(a,b+1,step)]
SC=[]
# S1 mois tenu : alimentation 2 500/j, transport 700/j, jusqu'au 22
SC.append(('S1 mois tenu','2026-11-23','2026-11-16',{'2026-11':BN},base('2026-11',jours('2026-11',1,22,2500,'Alimentation')+jours('2026-11',1,22,700,'Transport'))))
# S2 rythme rapide alimentation (5 000/j → 150k projeté pour 90k) mais pas encore dépassé au 15
SC.append(('S2 rythme rapide','2026-11-16','2026-11-09',{'2026-11':BN},base('2026-11',jours('2026-11',1,15,5000,'Alimentation'))))
# S3 un poste dépassé (Transport 45k pour 30k) mais grande marge ailleurs
SC.append(('S3 un poste dépassé, mois OK','2026-11-23','2026-11-16',{'2026-11':BN},base('2026-11',jours('2026-11',1,22,1000,'Alimentation')+jours('2026-11',16,22,6500,'Transport'))))
# S4 mois dans le rouge
SC.append(('S4 mois dans le rouge','2026-11-23','2026-11-16',{'2026-11':BN},base('2026-11',jours('2026-11',1,22,4500,'Alimentation')+[(60000,'2026-11-17',V,'Imprévus'),(40000,'2026-11-18',V,'Dons'),(35000,'2026-11-10',V,'Loisirs')])))
# S5 poste sans budget
SC.append(('S5 poste sans budget','2026-11-23','2026-11-16',{'2026-11':BN},base('2026-11',jours('2026-11',1,22,2000,'Alimentation')+[(25000,'2026-11-19',V,'Cadeaux')])))
# S6 pas de budget
SC.append(('S6 sans budget','2026-11-23','2026-11-16',{},base('2026-11',jours('2026-11',1,22,3000,'Alimentation'))))
# S7 semaine sans dépense (dépenses avant le 15)
SC.append(('S7 semaine sans transaction','2026-11-23','2026-11-16',{'2026-11':BN},base('2026-11',jours('2026-11',1,14,2000,'Alimentation'))))
# S8 semaine à cheval : 30 nov → 6 déc, vue le 7 déc ; novembre clos dans son budget, 30 nov : 20 000 alimentation
B12=dict(BN)
SC.append(('S8 semaine à cheval nov/déc','2026-12-07','2026-11-30',{'2026-11':BN,'2026-12':B12},base('2026-11',jours('2026-11',1,29,2800,'Alimentation')+[(20000,'2026-11-30',V,'Alimentation'),(15000,'2026-11-30',V,'Cadeaux')])+base('2026-12',jours('2026-12',1,6,2500,'Alimentation'))))
# S9 dépense fixe dépassée seulement
SC.append(('S9 fixe dépassée','2026-11-23','2026-11-16',{'2026-11':BN},[(500000,'2026-11-01',R,'Salaire'),(150000,'2026-11-02',F,'Loyer'),(80000,'2026-11-05',E,'Epargne projet'),(32000,'2026-11-17',F,'Électricité')]+jours('2026-11',1,22,2500,'Alimentation')))
# S10 gros achat prévu
BQ=dict(BN);BQ['Équipement']=150000;BQ['Salaire']=700000
SC.append(('S10 gros achat prévu','2026-11-23','2026-11-16',{'2026-11':BQ},[(700000,'2026-11-01',R,'Salaire')]+base('2026-11',[])[1:]+jours('2026-11',1,22,2500,'Alimentation')+[(150000,'2026-11-18',V,'Équipement')]))
# S11 début de mois, semaine à cheval oct/nov vue le 2 nov... (lundi 26 oct)
SC.append(('S11 début de mois (3 nov)','2026-11-09','2026-11-02',{'2026-11':BN,'2026-10':BN},base('2026-10',jours('2026-10',1,31,2900,'Alimentation'))+base('2026-11',jours('2026-11',1,8,2500,'Alimentation'))))
# S12 revenus réels > prévus + mois rouge sur budget mais encaissé un extra
BR=dict(BN)
SC.append(('S12 commerce non prévu','2026-11-23','2026-11-16',{'2026-11':BR},base('2026-11',jours('2026-11',1,22,4500,'Alimentation')+[(150000,'2026-11-15',R,'Commerce')])))

# Ce que chaque situation doit dire (présent) et ne jamais dire (absent)
ATT={
 'S1':(['Semaine dans les clous','Tu peux encore dépenser','tiendront leur budget'],['hors budget cette']),
 'S2':(['Rythme trop rapide sur Alimentation','Pour tenir'],['dépassé']),
 'S3':(['15 500 F hors budget','Un poste a déjà dépassé son budget','compense en réduisant'],['tiendront leur budget']),
 'S4':(['Budget du mois','dépassé de 62 000 F','4 postes ont déjà dépassé','ne suffisent plus','Pas ce mois-ci'],['Tu peux encore dépenser','tiendront leur budget','compense en réduisant']),
 'S5':(['25 000 F hors budget','Cadeaux (25 000 F) n\'était pas prévu'],['tous tes postes variables tiendront']),
 'S6':(['Semaine sans budget de référence','Je ne peux pas répondre'],['hors budget cette']),
 'S7':(['Semaine sans transaction notée'],[]),
 'S8':(['26 200 F hors budget','dont 11 200 F hors budget de novembre','dont 15 000 F hors budget de novembre'],[]),
 'S9':(['12 000 F hors budget','Électricité'],['Tu peux encore dépenser\n0']),
 'S10':(['Semaine dans les clous','budget du mois utilisé en entier'],['Rythme trop rapide','0 F par jour']),
 'S11':(['Semaine dans les clous'],['hors budget cette']),
 'S12':(['221 000 F non affectés'],[]),
}
srv=subprocess.Popen(['python3','-m','http.server','8771'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
fautes=[]
try:
  with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for nom,auj,lun,bud,txs in SC:
        k=nom.split()[0]
        pg,errs=page(b,mk(bud,txs),now=dt.datetime.fromisoformat(auj+'T20:00:00'));pg.wait_for_timeout(500)
        pg.evaluate(f"openBilan('{lun}')");pg.wait_for_timeout(250)
        pg.fill('#pp-lib','Achat');pg.fill('#pp-amt','20000');pg.evaluate('peutPermettre()')
        txt=pg.inner_text('#cpt-sheet').replace('\u202f',' ').replace('\u00a0',' ')
        oui,non=ATT[k]
        for x in oui:
            if x not in txt:fautes.append(f'{k}: manque « {x} »')
        for x in non:
            if x in txt:fautes.append(f'{k}: ne devrait pas dire « {x} »')
        if errs:fautes.append(f'{k}: {errs}')
        pg.context.close()
    # Bilan du mois (vu le 3 décembre)
    for k,att in [('S4','94 000 F au total'),('S6','Fais un budget pour décembre'),('S5','Cadeaux a coûté 25 000 F')]:
        nom,auj,lun,bud,txs=[x for x in SC if x[0].split()[0]==k][0]
        pg,errs=page(b,mk(bud,txs),now=dt.datetime.fromisoformat('2026-12-03T20:00:00'));pg.wait_for_timeout(500)
        pg.evaluate("openBilanMois('2026-11')");pg.wait_for_timeout(250)
        if att not in pg.inner_text('#cpt-sheet').replace('\u202f',' ').replace('\u00a0',' '):fautes.append(f'mois {k}: manque « {att} »')
        pg.context.close()
finally: srv.terminate()
print(len(SC),'situations ;',len(fautes),'incohérence(s)')
for f in fautes:print(' -',f)
print('errors',fautes)
