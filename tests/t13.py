import os
import sys,subprocess,time,json;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from stub import APP
from playwright.sync_api import sync_playwright
AUTH="""const K='__au';const st=JSON.parse(localStorage.getItem(K)||'{"users":{},"cur":null,"n":0}');const sv=()=>localStorage.setItem(K,JSON.stringify(st));
let cb=null;const mk=e=>e?{uid:st.users[e].uid,email:e,displayName:st.users[e].dn||null,getIdToken:async()=>'t'}:null;const A={get currentUser(){return mk(st.cur)}};
export const getAuth=()=>A;export class GoogleAuthProvider{};export const signInWithPopup=async()=>{};
export const signOut=async()=>{st.cur=null;sv();cb&&cb(null)};
export const onAuthStateChanged=(a,f)=>{cb=f;setTimeout(()=>f(mk(st.cur)),30);return()=>{}};
const E=c=>{const e=new Error(c);e.code=c;return e};
export const signInWithEmailAndPassword=async(a,e,pw)=>{const u=st.users[e];if(!u||u.pw!==pw)throw E('auth/invalid-credential');st.cur=e;sv();setTimeout(()=>cb(mk(e)),10);return{user:mk(e)}};
export const createUserWithEmailAndPassword=async(a,e,pw)=>{if(st.users[e])throw E('auth/email-already-in-use');st.users[e]={pw,uid:'u'+(++st.n)};st.cur=e;sv();setTimeout(()=>cb(mk(e)),10);return{user:mk(e)}};
export const updateProfile=async(u,p)=>{st.users[u.email].dn=p.displayName;sv()};
export const EmailAuthProvider={};export const reauthenticateWithPopup=async()=>{};export const reauthenticateWithCredential=async()=>{};export const updatePassword=async()=>{};"""
FSP="""const K='__fs';const store=JSON.parse(localStorage.getItem(K)||'{}');const sv=()=>localStorage.setItem(K,JSON.stringify(store));const subs={};window.__store=store;let n=0;
export const initializeFirestore=()=>({});export const getFirestore=()=>({});export const persistentLocalCache=()=>0;export const persistentMultipleTabManager=()=>0;
export const doc=(d,...a)=>a.length?a.join('/'):(d+'/id'+Date.now()+(++n));export const collection=(d,...a)=>a.join('/');export const query=c=>c;export const orderBy=()=>0;export const where=()=>0;
const isCol=p=>p.split('/').length%2===1;
function colSnap(p){const docs=Object.keys(store).filter(k=>k.startsWith(p+'/')&&k.split('/').length===p.split('/').length+1).map(k=>({id:k.split('/').pop(),data:()=>store[k]}));return{docs,size:docs.length}}
function docSnap(p,fc){return{exists:()=>p in store,data:()=>store[p],metadata:{fromCache:fc,hasPendingWrites:false}}}
function fire(){Object.keys(subs).forEach(p=>subs[p].forEach(cb=>cb(isCol(p)?colSnap(p):docSnap(p,false))))}
export const onSnapshot=(q,o,cb)=>{if(typeof o==='function')cb=o;(subs[q]=subs[q]||[]).push(cb);setTimeout(()=>cb(isCol(q)?colSnap(q):docSnap(q,false)),20);return()=>{}};
export const setDoc=async(p,d,o)=>{store[p]=o?Object.assign({},store[p]||{},d):Object.assign({},d);sv();setTimeout(fire,5)};
export const getDoc=async p=>docSnap(p,false);export const getDocs=async p=>colSnap(p);export const deleteDoc=async p=>{delete store[p];sv();setTimeout(fire,5)};"""
srv=subprocess.Popen(['python3','-m','http.server','8771'],cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
apis=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':844},service_workers='block');pg=ctx.new_page()
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('dialog',lambda d:d.accept())
    pg.route('**/firebase-app.js',lambda r:r.fulfill(body=APP,content_type='text/javascript'))
    pg.route('**/firebase-auth.js',lambda r:r.fulfill(body=AUTH,content_type='text/javascript'))
    pg.route('**/firebase-firestore.js',lambda r:r.fulfill(body=FSP,content_type='text/javascript'))
    pg.route('https://fonts.**',lambda r:r.abort())
    pg.route('**/api/**',lambda r:(apis.append(r.request.url.split('/api/')[1]),r.fulfill(body=json.dumps({'ok':True,'nouveauCode':'AB2C-DE3F-GH4J'}),content_type='application/json')))
    pg.goto('http://localhost:8771/');pg.wait_for_selector('#auth-box button')
    def creer(prenom,num,pw):
        pg.click('text=Créer un compte');pg.fill('#au-prenom',prenom);pg.fill('#au-pseudo',num);pg.fill('#au-mdp',pw);pg.fill('#au-mdp2',pw);pg.click('#au-go');pg.wait_for_timeout(1200)
    def sortir():
        for sel in ['#secours-ov','#empreinte-ov',"#deja-ov",'#onb']:
            if pg.locator(sel).count():
                pg.click({'#secours-ov':"text=Je l'ai noté",'#empreinte-ov':'text=Plus tard','#deja-ov':"text=Ouvrir mon compte",'#onb':'#onb-go'}[sel]);pg.wait_for_timeout(400)
        pg.evaluate("doSignOut()");pg.wait_for_timeout(500);pg.wait_for_selector('#auth-box button')
    creer('Awa','77 123 45 67','Baobab2026');print('1) Awa :',pg.evaluate("window._fb.auth.currentUser.uid"),'| code:',pg.locator('#secours-ov').count());sortir()
    creer('Moussa','+221771234567','Thiebou2026');print('2) même numéro, autre mot de passe :',pg.evaluate("window._fb.auth.currentUser.uid"),'| nouveau compte (code affiché):',pg.locator('#secours-ov').count());sortir()
    creer('Awa bis','771234567','Baobab2026');print('3) même numéro + même mot de passe :',pg.evaluate("window._fb.auth.currentUser.uid"),'| écran déjà un compte:',pg.locator('#deja-ov').count(),'| nom:',pg.inner_text('#uname'))
    pg.screenshot(path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out','')+'n3.png');sortir()
    pg.fill('#au-pseudo','77 123 45 67');pg.fill('#au-mdp','Thiebou2026');pg.click('#au-go');pg.wait_for_timeout(1200);print('4) connexion Moussa :',pg.evaluate("window._fb.auth.currentUser.uid"),pg.inner_text('#uname'))
    sortir();pg.fill('#au-pseudo','77 123 45 67');pg.fill('#au-mdp','Mauvais2026');pg.click('#au-go');pg.wait_for_timeout(500);print('5) mauvais mot de passe :',pg.inner_text('#au-err'))
    print('appels /api :',apis.count('numero'),'liaisons (attendu : 2, une par compte créé)')
    print('errors',errs);b.close()
srv.kill()
