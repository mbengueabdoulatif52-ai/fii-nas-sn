// Test de /api/supprimer avec un faux Firebase
import { makeSupprimer } from '../api/_secours.js';
const log=[];let authTime=Date.now()/1000;
const ops={pret:()=>true,async verifierJeton(t){if(t!=='ok')throw new Error('x');return{uid:'u1',auth_time:authTime};},
  async lireProfil(){return{numero:'771234567'};},async retirerNumero(n,u){log.push('num '+n+' '+u);},
  async effacerDonnees(u){log.push('data '+u);},async supprimerUtilisateur(u){log.push('user '+u);}};
const h=makeSupprimer(ops);
const call=async b=>{let st=0,js=null;const res={setHeader(){},status(s){st=s;return this;},json(j){js=j;return this;},end(){return this;}};await h({method:'POST',headers:{},body:b},res);return[st,js];};
const eq=(a,b,m)=>{if(JSON.stringify(a)!==JSON.stringify(b)){console.error('ÉCHEC',m,a,b);process.exit(1);}};
eq((await call({}))[0],401,'sans jeton');
authTime=Date.now()/1000-600;eq((await call({idToken:'ok'}))[0],401,'connexion trop ancienne');eq(log,[],'rien effacé');
authTime=Date.now()/1000;eq((await call({idToken:'ok'}))[0],200,'ok');
eq(log,['num 221771234567 u1','data u1','user u1'],'ordre');
console.log('srv3 ok');
