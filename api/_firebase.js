// Accès administrateur à Firebase (clé de service dans la variable Vercel FIREBASE_SERVICE_ACCOUNT)
import { initializeApp, cert, getApps } from 'firebase-admin/app';
import { getAuth } from 'firebase-admin/auth';
import { getFirestore, FieldValue } from 'firebase-admin/firestore';
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
  async changerMdp(uid, mdp) { await getAuth(app()).updateUser(uid, { password: mdp }); },
  async majUtilisateur(uid, data) { await getAuth(app()).updateUser(uid, data); },
  async lireUtilisateur(uid) { try { return await getAuth(app()).getUser(uid); } catch (e) { if (e.code === 'auth/user-not-found') return null; throw e; } },
  async verifierJeton(t) { return await getAuth(app()).verifyIdToken(t); },
  async lireProfil(uid) { const d = await getFirestore(app()).doc(`users/${uid}/data/profil`).get(); return d.exists ? d.data() : null; },
  // Index numéro → comptes, lisible et modifiable par le serveur seulement (règles : tout le reste est fermé)
  async uidsDeNumero(num) { const d = await getFirestore(app()).doc(`numeros/${num}`).get(); return d.exists ? (d.data().uids || []) : []; },
  async ajouterNumero(num, uid) { await getFirestore(app()).doc(`numeros/${num}`).set({ uids: FieldValue.arrayUnion(uid) }, { merge: true }); },
  async retirerNumero(num, uid) {
    const ref = getFirestore(app()).doc(`numeros/${num}`), d = await ref.get();
    if (!d.exists) return;
    const reste = (d.data().uids || []).filter(u => u !== uid);
    if (reste.length) await ref.set({ uids: reste }); else await ref.delete();
  },
  // users/{uid} et tout ce qu'il contient (transactions, mouvements, réglages, code de secours…)
  async effacerDonnees(uid) { const db = getFirestore(app()); await db.recursiveDelete(db.doc(`users/${uid}`)); },
  async supprimerUtilisateur(uid) { try { await getAuth(app()).deleteUser(uid); } catch (e) { if (e.code !== 'auth/user-not-found') throw e; } }
};
