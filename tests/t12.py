import os
import sys,subprocess,time,json;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from stub import FS,APP
from playwright.sync_api import sync_playwright
AUTH="""const users={};let n=0;let cb=null,cur=null;const A={get currentUser(){return cur}};window.__users=users;
export const getAuth=()=>A;export class GoogleAuthProvider{};export const signInWithPopup=async()=>{};
export const signOut=async()=>{cur=null;cb&&cb(null)};
export const onAuthStateChanged=(a,f)=>{cb=f;setTimeout(()=>f(cur),30);return()=>{}};
const E=c=>{const e=new Error(c);e.code=c;return e};
const mkU=(email,u)=>({uid:u.uid,email,displayName:u.dn||null,getIdToken:async()=>'tok-'+u.uid});
export const signInWithEmailAndPassword=async(a,email,pw)=>{const u=users[email];if(!u||u.pw!==pw)throw E('auth/invalid-credential');cur=mkU(email,u);setTimeout(()=>cb(cur),10);return{user:cur}};
export const createUserWithEmailAndPassword=async(a,email,pw)=>{if(users[email])throw E('auth/email-already-in-use');users[email]={pw,uid:'u'+(++n)};cur=mkU(email,users[email]);setTimeout(()=>cb(cur),10);return{user:cur}};
export const updateProfile=async(u,p)=>{u.displayName=p.displayName;users[u.email].dn=p.displayName};
export const EmailAuthProvider={credential:(e,p)=>({e,p})};
export const reauthenticateWithPopup=async()=>{};export const reauthenticateWithCredential=async(u,c)=>{if(users[c.e].pw!==c.p)throw E('auth/invalid-credential')};
export const updatePassword=async(u,p)=>{users[u.email].pw=p};"""
srv=subprocess.Popen(['python3','-m','http.server','8771'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
calls=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':844},service_workers='block');pg=ctx.new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('dialog',lambda d:d.accept())
    pg.route('**/firebase-app.js',lambda r:r.fulfill(body=APP,content_type='text/javascript'))
    pg.route('**/firebase-auth.js',lambda r:r.fulfill(body=AUTH,content_type='text/javascript'))
    pg.route('**/firebase-firestore.js',lambda r:r.fulfill(body=FS('{}'),content_type='text/javascript'))
    pg.route('https://fonts.**',lambda r:r.abort())
    def api(r):
        calls.append((r.request.url.split('/api/')[1],r.request.post_data))
        if 'motdepasse' in r.request.url:
            # simule le serveur : déplace le compte vers le nouvel identifiant
            pg.evaluate("""async()=>{const u=window._fb.auth.currentUser;const old=window.__users[u.email];}""")
        r.fulfill(body=json.dumps({'ok':True,'nouveauCode':'AB2C-DE3F-GH4J'}),content_type='application/json')
    pg.route('**/api/**',api)
    pg.goto('http://localhost:8771/');pg.wait_for_timeout(900)
    pg.fill('#au-pseudo','77 123 45 67');pg.dispatch_event('#au-pseudo','input');print('indice connexion:',pg.inner_text('#au-hint'))
    pg.click('text=Créer un compte');pg.fill('#au-prenom','Awa');pg.fill('#au-pseudo','771234567');pg.dispatch_event('#au-pseudo','input')
    print('création:',pg.inner_text('#au-dispo').replace('\n',' / '))
    for pw in ['12345678','azerty12','23081996','77123456700','motdepasse']:
        pg.fill('#au-mdp',pw);pg.dispatch_event('#au-mdp','input');print(' ',pw,'→',pg.inner_text('#au-force') or 'accepté')
    pg.fill('#au-mdp','Baobab2026');pg.dispatch_event('#au-mdp','input');pg.fill('#au-mdp2','Baobab2026');pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'n1.png')
    pg.click('#au-go');pg.wait_for_timeout(1000)
    print('code:',pg.inner_text('#secours-code'),'| libellé:',pg.locator('#secours-ov').inner_text().split('Compte ')[1].split('\n')[0])
    print('profil écrit:',pg.evaluate("JSON.stringify(window.__store['users/u1/data/profil'])"),'| api:',[c[0] for c in calls])
    pg.click("text=Je l'ai noté");pg.wait_for_timeout(300);pg.click('text=Plus tard');pg.wait_for_timeout(200);pg.click('#onb-go');pg.wait_for_timeout(400)
    pg.evaluate("goP('pro',document.querySelectorAll('.ni')[4])");pg.wait_for_timeout(300)
    print('profil:',pg.inner_text('#pname'),'|',pg.inner_text('#pemail'),'| lignes:',pg.locator('#security-ui >> text=Mot de passe').count(),pg.locator('#security-ui >> text=Code de secours').count())
    pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'n2.png',full_page=True)
    # changement de mot de passe (compte numéro → serveur)
    pg.evaluate("openChangerMdp()");pg.fill('#cm-old','faux');pg.fill('#cm-new','Mangue2027x');pg.fill('#cm-new2','Mangue2027x');pg.click('#cm-go');pg.wait_for_timeout(300);print('ancien faux:',pg.inner_text('#cm-err'))
    pg.evaluate("""async()=>{const em=await emailNumero('221771234567','Mangue2027x');const u=window._fb.auth.currentUser;window.__users[em]={pw:'Mangue2027x',uid:u.uid,dn:'Awa'};}""") # le serveur aurait déplacé le compte
    pg.fill('#cm-old','Baobab2026');pg.click('#cm-go');pg.wait_for_timeout(600);print('changement:',pg.locator('#cpt-sheet').count()==0,[c[0] for c in calls][-1])
    # même numéro, autre mot de passe → 2e compte ; même numéro + même mot de passe → compte existant
    ctx2=b.new_context(viewport={'width':390,'height':844},service_workers='block')
    pg.evaluate("doSignOut()");pg.wait_for_timeout(1500)
    print('après déconnexion, comptes existants:',pg.evaluate("Object.keys(window.__users||{}).length") if pg.evaluate("!!window.__users") else 'page rechargée (stub remis à zéro)')
    print('errors',errs);b.close()
srv.kill()
