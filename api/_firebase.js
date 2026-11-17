// Accès administrateur à Firebase (clé de service dans la variable Vercel FIREBASE_SERVICE_ACCOUNT)
import { initializeApp, cert, getApps } from 'firebase-admin/app';
import { getAuth } from 'firebase-admin/auth';
import { getFirestore } from 'firebase-admin/firestore';
import { DOMAINE } from './_secours.js';

function app() {
  if (getApps().length) return getApps()[0];
  return initializeApp({ credential: cert(JSON.parse(process.env.FIREBASE_SERVICE_ACCOUNT)) });
}
export const ops = {
  pret: () => !!process.env.FIREBASE_SERVICE_ACCOUNT,
  async uidDePseudo(pseudo) {
    try { return (await getAuth(app()).getUserByEmail(pseudo + DOMAINE)).uid; }
    catch (e) { if (e.code === 'auth/user-not-found') return null; throw e; }
  },
  async lireSecours(uid) { const d = await getFirestore(app()).doc(`users/${uid}/data/secours`).get(); return d.exists ? d.data() : null; },
  async ecrireSecours(uid, data) { await getFirestore(app()).doc(`users/${uid}/data/secours`).set(data, { merge: true }); },
  async changerMdp(uid, mdp) { await getAuth(app()).updateUser(uid, { password: mdp }); }
};
