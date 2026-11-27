APP="export const initializeApp=()=>({});"
AUTH="""try{if(!localStorage.getItem('fiinas-guide-test'))localStorage.setItem('fiinas-guide','1')}catch(e){}
try{if(!localStorage.getItem('fiinas-annonce-test'))localStorage.setItem('fiinas-sans-annonce','1')}catch(e){}
export const getAuth=()=>({});export class GoogleAuthProvider{};export const signInWithPopup=async()=>{};export const signOut=async()=>{};export const signInWithEmailAndPassword=async()=>{};export const createUserWithEmailAndPassword=async()=>{};export const updateProfile=async()=>{};export const EmailAuthProvider={credential:(e,p)=>({e,p})};export const reauthenticateWithCredential=async()=>{};export const reauthenticateWithPopup=async()=>{};export const updatePassword=async()=>{};
export const onAuthStateChanged=(a,cb)=>{setTimeout(()=>cb({uid:'u1',displayName:'Awa Diop',email:'awa@test.sn'}),30);return()=>{}};"""
def FS(init='{}'):
    return """const store=%s;const subs={};window.__store=store;let n=0;
export const initializeFirestore=()=>({});export const getFirestore=()=>({});export const persistentLocalCache=()=>0;export const persistentMultipleTabManager=()=>0;
export const doc=(d,...a)=>a.length?a.join('/'):(d+'/id'+(++n));export const collection=(d,...a)=>a.join('/');export const query=c=>c;export const orderBy=()=>0;export const where=()=>0;
const isCol=p=>p.split('/').length%%2===1;
function colSnap(p){const docs=Object.keys(store).filter(k=>k.startsWith(p+'/')&&k.split('/').length===p.split('/').length+1).map(k=>({id:k.split('/').pop(),data:()=>store[k]}));return{docs,size:docs.length}}
function docSnap(p,fromCache){return {exists:()=>p in store,data:()=>store[p],metadata:{fromCache,hasPendingWrites:false}}}
function fire(){Object.keys(subs).forEach(p=>subs[p].forEach(cb=>cb(isCol(p)?colSnap(p):docSnap(p,false))))}
export const onSnapshot=(q,o,cb)=>{let meta=false;if(typeof o==='function'){cb=o}else meta=!!(o&&o.includeMetadataChanges);(subs[q]=subs[q]||[]).push(cb);if(isCol(q))setTimeout(()=>cb(colSnap(q)),15);else{setTimeout(()=>cb(docSnap(q,true)),10);if(meta||(q in store))setTimeout(()=>cb(docSnap(q,false)),900);}return()=>{}};
export const setDoc=async(p,d,o)=>{store[p]=o?Object.assign({},store[p]||{},d):Object.assign({},d);setTimeout(fire,5)};
export const getDoc=async p=>docSnap(p,false);export const getDocs=async p=>colSnap(p);export const deleteDoc=async p=>{delete store[p];setTimeout(fire,5)};""" % init
def page(b,init='{}',protect=False,now=None,annonce=False):
    pg=b.new_context(viewport={'width':390,'height':844},service_workers='block').new_page()
    if now: pg.clock.set_fixed_time(now)
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.route('**/firebase-app.js',lambda r:r.fulfill(body=APP,content_type='text/javascript'))
    pg.route('**/firebase-auth.js',lambda r:r.fulfill(body=AUTH,content_type='text/javascript'))
    pg.route('**/firebase-firestore.js',lambda r:r.fulfill(body=FS(init),content_type='text/javascript'))
    pg.route('https://fonts.**',lambda r:r.abort())
    pg.on('dialog',lambda d:d.accept())
    if not protect: pg.add_init_script("localStorage.setItem('fiinas-protect-vu','1')")
    if annonce: pg.add_init_script("localStorage.setItem('fiinas-annonce-test','1')")
    pg.goto('http://localhost:8771/');pg.wait_for_timeout(1000)
    return pg,errs
