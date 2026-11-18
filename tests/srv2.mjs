import { makeRecuperer, makeNumero, makeMotDePasse, hashCode, nouveauCode, emailNumero, numeroDe } from '../api/_secours.js';
const sec={},users={},prof={},idx={};
const mk=(uid,email,code)=>{const salt='s'+uid;sec[uid]={hash:hashCode(code,salt),salt};users[uid]={email};};
const N='221771234567';
const cA=nouveauCode(),cB=nouveauCode();
mk('uA',emailNumero(N,'motdepasseA'),cA);prof.uA={numero:N};
mk('uB',emailNumero(N,'motdepasseB'),cB);prof.uB={numero:N};
idx[N]=['uA','uB'];
const E=c=>{const e=new Error(c);e.code=c;return e};
const ops={pret:()=>true,uidDePseudo:async()=>null,lireSecours:async u=>sec[u],ecrireSecours:async(u,d)=>{sec[u]=Object.assign({},sec[u],d)},
 changerMdp:async()=>{},majUtilisateur:async(u,d)=>{if(d.email&&Object.entries(users).some(([k,v])=>k!==u&&v.email===d.email))throw E('auth/email-already-exists');Object.assign(users[u],d)},
 lireUtilisateur:async u=>users[u]||null,verifierJeton:async t=>JSON.parse(t),lireProfil:async u=>prof[u],uidsDeNumero:async n=>idx[n]||[],ajouterNumero:async(n,u)=>{idx[n]=[...new Set([...(idx[n]||[]),u])]}};
const call=async(h,body)=>{let st,js;const res={setHeader(){},status(s){st=s;return this},json(j){js=j;return this},end(){return this}};await h({method:'POST',headers:{},body},res);return [st,js];};
const R=makeRecuperer(ops),M=makeMotDePasse(ops),NU=makeNumero(ops);
console.log('numeroDe', numeroDe('77 123 45 67'), numeroDe('+221771234567'), numeroDe('00221 77 123 45 67'), numeroDe('awa.diop'), numeroDe('123'));
console.log('récup B par numéro', (await call(R,{identifiant:'77 123 45 67',code:cB,mdp:'nouveauB123'}))[0], users.uB.email===emailNumero(N,'nouveauB123'), users.uA.email===emailNumero(N,'motdepasseA'));
console.log('récup avec mot de passe de A (doublon)', await call(R,{identifiant:N,code:cA,mdp:'nouveauB123'}));
console.log('mauvais code', (await call(R,{identifiant:N,code:'AAAA-BBBB-CCCC',mdp:'xxxxxxxx1'}))[0], sec.uA.echecs, sec.uB.echecs);
const now=Math.floor(Date.now()/1000);
console.log('mdp sans reauth', await call(M,{idToken:JSON.stringify({uid:'uA',auth_time:now-900}),nouveau:'abcdefgh9'}));
console.log('mdp ok', (await call(M,{idToken:JSON.stringify({uid:'uA',auth_time:now}),nouveau:'abcdefgh9'}))[0], users.uA.email===emailNumero(N,'abcdefgh9'));
console.log('mdp doublon', (await call(M,{idToken:JSON.stringify({uid:'uA',auth_time:now}),nouveau:'nouveauB123'}))[0]);
users.uC={email:emailNumero('221781112233','zzzzzzzz1')};
console.log('liaison numéro', (await call(NU,{idToken:JSON.stringify({uid:'uC'}),numero:'78 111 22 33'}))[0], idx['221781112233']);
console.log('sans jeton', (await call(NU,{numero:'781112233'}))[0]);
