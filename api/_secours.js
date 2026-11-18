// Récupération d'un compte « nom d'utilisateur » par code de secours.
// Logique séparée des appels Firebase (ops) pour pouvoir la tester sans serveur.
import crypto from 'node:crypto';

export const DOMAINE = '@utilisateurs.fii-nas-sn.vercel.app';
export const DOMAINE_NUM = '@numeros.fii-nas-sn.vercel.app';
// Numéro sénégalais → 2217XXXXXXXX (null si ce n'est pas un numéro)
export function numeroDe(v) {
  const s = String(v || '').trim();
  if (!/^[+\d\s().-]+$/.test(s)) return null;
  let d = s.replace(/\D/g, '');
  if (d.startsWith('00')) d = d.slice(2);
  if (d.length === 9 && d[0] === '7') d = '221' + d;
  return /^2217\d{8}$/.test(d) ? d : null;
}
// Identifiant caché d'un compte « numéro » : empreinte du numéro et du mot de passe
export const emailNumero = (num, mdp) => 't' + sha256('fiinas-sn:' + num + ':' + mdp).slice(0, 40) + DOMAINE_NUM;
const ORIGINES = ['https://fii-nas-sn.vercel.app'];
const ALPHABET = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';
const MAX_ECHECS = 5, BLOCAGE_MS = 60 * 60 * 1000;
const ERR_GENERIQUE = 'Nom d\'utilisateur ou code de secours incorrect.';

export const normPseudo = v => String(v || '').trim().toLowerCase().replace(/^@/, '');
export const pseudoValide = p => /^[a-z0-9][a-z0-9._-]{2,19}$/.test(p);
export const normCode = v => String(v || '').toUpperCase().replace(/[^A-Z0-9]/g, '');
export const sha256 = s => crypto.createHash('sha256').update(s).digest('hex');

export function nouveauCode() {
  let c = '';
  while (c.length < 12) {
    const b = crypto.randomBytes(1)[0];
    if (b < 248) c += ALPHABET[b % 31]; // 248 = 8 × 31 : pas de biais
  }
  return c.slice(0, 4) + '-' + c.slice(4, 8) + '-' + c.slice(8);
}
export function hashCode(code, salt) { return sha256(salt + ':' + normCode(code)); }

function egal(a, b) {
  const x = Buffer.from(String(a)), y = Buffer.from(String(b));
  return x.length === y.length && crypto.timingSafeEqual(x, y);
}
function entetes(req, res) {
  const o = req.headers.origin || '';
  if (ORIGINES.includes(o) || /^http:\/\/localhost(:\d+)?$/.test(o)) res.setHeader('Access-Control-Allow-Origin', o);
  res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Cache-Control', 'no-store');
}
function corps(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  try { return JSON.parse(req.body || '{}'); } catch { return {}; }
}

async function verifierCode(ops, uid, code) {
  const s = (await ops.lireSecours(uid)) || {};
  if (!s.hash || !s.salt) return 'non';
  if ((s.bloqueJusqua || 0) > Date.now()) return 'bloque';
  if (egal(hashCode(code, s.salt), s.hash)) return 'ok';
  const echecs = (s.echecs || 0) + 1;
  await ops.ecrireSecours(uid, echecs >= MAX_ECHECS ? { echecs: 0, bloqueJusqua: Date.now() + BLOCAGE_MS } : { echecs });
  return 'non';
}
async function renouvelerCode(ops, uid) {
  const nc = nouveauCode(), salt = crypto.randomBytes(16).toString('hex');
  await ops.ecrireSecours(uid, { hash: hashCode(nc, salt), salt, date: new Date().toISOString(), echecs: 0, bloqueJusqua: 0 });
  return nc;
}
const MSG_DOUBLON = 'Ce mot de passe est déjà utilisé avec ce numéro. Choisis-en un autre.';

// POST /api/recuperer {identifiant (ou pseudo), code, mdp} → {ok, nouveauCode} | {erreur}
export function makeRecuperer(ops) {
  return async (req, res) => {
    entetes(req, res);
    if (req.method === 'OPTIONS') return res.status(204).end();
    if (req.method !== 'POST') return res.status(405).json({ erreur: 'Méthode non autorisée.' });
    if (!ops.pret()) return res.status(503).json({ erreur: 'La récupération de compte n\'est pas encore configurée.' });
    const b = corps(req);
    const ident = b.identifiant != null ? b.identifiant : b.pseudo;
    const num = numeroDe(ident), pseudo = num ? null : normPseudo(ident);
    const code = normCode(b.code), mdp = String(b.mdp || '');
    if ((!num && !pseudoValide(pseudo)) || code.length !== 12) return res.status(400).json({ erreur: ERR_GENERIQUE });
    if (mdp.length < 8 || mdp.length > 128) return res.status(400).json({ erreur: 'Le nouveau mot de passe doit faire au moins 8 caractères.' });
    try {
      let uid = null, bloque = false;
      if (num) {
        // Plusieurs comptes peuvent partager un numéro : on cherche celui dont le code correspond
        for (const u of (await ops.uidsDeNumero(num)).slice(0, 50)) {
          const r = await verifierCode(ops, u, code);
          if (r === 'ok') { uid = u; break; }
          if (r === 'bloque') bloque = true;
        }
      } else {
        const u = await ops.uidDePseudo(pseudo);
        if (u) { const r = await verifierCode(ops, u, code); if (r === 'ok') uid = u; else if (r === 'bloque') bloque = true; }
      }
      if (!uid) return res.status(bloque ? 429 : 400).json({ erreur: bloque ? 'Trop d\'essais. Réessaie dans une heure.' : ERR_GENERIQUE });
      if (num) {
        try { await ops.majUtilisateur(uid, { email: emailNumero(num, mdp), password: mdp }); }
        catch (e) { if (e.code === 'auth/email-already-exists') return res.status(409).json({ erreur: MSG_DOUBLON }); throw e; }
      } else await ops.changerMdp(uid, mdp);
      // Le code utilisé est remplacé : il ne peut servir qu'une fois
      return res.status(200).json({ ok: true, nouveauCode: await renouvelerCode(ops, uid) });
    } catch (e) {
      console.error('recuperer', e);
      return res.status(500).json({ erreur: 'Erreur du serveur. Réessaie plus tard.' });
    }
  };
}

// GET /api/disponible?u=pseudo → {disponible}
export function makeDisponible(ops) {
  return async (req, res) => {
    entetes(req, res);
    if (req.method === 'OPTIONS') return res.status(204).end();
    const pseudo = normPseudo((req.query && req.query.u) || '');
    if (!pseudoValide(pseudo)) return res.status(400).json({ erreur: 'Nom d\'utilisateur invalide.' });
    if (!ops.pret()) return res.status(503).json({ erreur: 'indisponible' });
    try { return res.status(200).json({ disponible: !(await ops.uidDePseudo(pseudo)) }); }
    catch (e) { console.error('disponible', e); return res.status(500).json({ erreur: 'indisponible' }); }
  };
}

// Jeton de connexion Firebase de l'appelant → uid (et heure de connexion)
async function appelant(ops, b) {
  if (!b.idToken) return null;
  try { return await ops.verifierJeton(String(b.idToken)); } catch { return null; }
}

// POST /api/numero {idToken, numero} → relie le compte à son numéro (pour la récupération)
export function makeNumero(ops) {
  return async (req, res) => {
    entetes(req, res);
    if (req.method === 'OPTIONS') return res.status(204).end();
    if (req.method !== 'POST') return res.status(405).json({ erreur: 'Méthode non autorisée.' });
    if (!ops.pret()) return res.status(503).json({ erreur: 'indisponible' });
    const b = corps(req), num = numeroDe(b.numero), t = await appelant(ops, b);
    if (!t) return res.status(401).json({ erreur: 'Connexion requise.' });
    if (!num) return res.status(400).json({ erreur: 'Numéro invalide.' });
    try {
      const u = await ops.lireUtilisateur(t.uid);
      if (!u || !String(u.email || '').endsWith(DOMAINE_NUM)) return res.status(400).json({ erreur: 'Ce compte n\'utilise pas de numéro.' });
      await ops.ajouterNumero(num, t.uid);
      return res.status(200).json({ ok: true });
    } catch (e) { console.error('numero', e); return res.status(500).json({ erreur: 'Erreur du serveur.' }); }
  };
}

// POST /api/motdepasse {idToken, nouveau} → change le mot de passe d'un compte « numéro »
// (l'identifiant caché dépend du mot de passe). L'appli refait d'abord vérifier l'ancien.
export function makeMotDePasse(ops) {
  return async (req, res) => {
    entetes(req, res);
    if (req.method === 'OPTIONS') return res.status(204).end();
    if (req.method !== 'POST') return res.status(405).json({ erreur: 'Méthode non autorisée.' });
    if (!ops.pret()) return res.status(503).json({ erreur: 'Le changement de mot de passe n\'est pas encore configuré.' });
    const b = corps(req), mdp = String(b.nouveau || ''), t = await appelant(ops, b);
    if (!t) return res.status(401).json({ erreur: 'Reconnecte-toi puis réessaie.' });
    if (Date.now() / 1000 - (t.auth_time || 0) > 300) return res.status(401).json({ erreur: 'Confirme d\'abord ton mot de passe actuel.' });
    if (mdp.length < 8 || mdp.length > 128) return res.status(400).json({ erreur: 'Le nouveau mot de passe doit faire au moins 8 caractères.' });
    try {
      const u = await ops.lireUtilisateur(t.uid);
      if (!u || !String(u.email || '').endsWith(DOMAINE_NUM)) return res.status(400).json({ erreur: 'Ce compte n\'utilise pas de numéro.' });
      const num = numeroDe((await ops.lireProfil(t.uid) || {}).numero);
      if (!num) return res.status(400).json({ erreur: 'Numéro du compte introuvable.' });
      try { await ops.majUtilisateur(t.uid, { email: emailNumero(num, mdp), password: mdp }); }
      catch (e) { if (e.code === 'auth/email-already-exists') return res.status(409).json({ erreur: MSG_DOUBLON }); throw e; }
      await ops.ajouterNumero(num, t.uid);
      return res.status(200).json({ ok: true });
    } catch (e) { console.error('motdepasse', e); return res.status(500).json({ erreur: 'Erreur du serveur.' }); }
  };
}

// POST /api/supprimer {idToken} → efface le compte : données, numéro associé, compte de connexion.
// L'appli refait d'abord confirmer le mot de passe (connexion de moins de 5 minutes).
export function makeSupprimer(ops) {
  return async (req, res) => {
    entetes(req, res);
    if (req.method === 'OPTIONS') return res.status(204).end();
    if (req.method !== 'POST') return res.status(405).json({ erreur: 'Méthode non autorisée.' });
    if (!ops.pret()) return res.status(503).json({ erreur: 'La suppression n\'est pas disponible pour le moment.' });
    const b = corps(req), t = await appelant(ops, b);
    if (!t) return res.status(401).json({ erreur: 'Reconnecte-toi puis réessaie.' });
    if (Date.now() / 1000 - (t.auth_time || 0) > 300) return res.status(401).json({ erreur: 'Confirme d\'abord ton mot de passe.' });
    try {
      const num = numeroDe((await ops.lireProfil(t.uid) || {}).numero);
      if (num) await ops.retirerNumero(num, t.uid);
      await ops.effacerDonnees(t.uid);
      await ops.supprimerUtilisateur(t.uid);
      return res.status(200).json({ ok: true });
    } catch (e) { console.error('supprimer', e); return res.status(500).json({ erreur: 'Erreur du serveur. Réessaie plus tard.' }); }
  };
}
