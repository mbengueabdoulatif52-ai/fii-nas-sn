// Récupération d'un compte « nom d'utilisateur » par code de secours.
// Logique séparée des appels Firebase (ops) pour pouvoir la tester sans serveur.
import crypto from 'node:crypto';

export const DOMAINE = '@utilisateurs.fii-nas-sn.vercel.app';
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

// POST /api/recuperer {pseudo, code, mdp} → {ok, nouveauCode} | {erreur}
export function makeRecuperer(ops) {
  return async (req, res) => {
    entetes(req, res);
    if (req.method === 'OPTIONS') return res.status(204).end();
    if (req.method !== 'POST') return res.status(405).json({ erreur: 'Méthode non autorisée.' });
    if (!ops.pret()) return res.status(503).json({ erreur: 'La récupération de compte n\'est pas encore configurée.' });
    const b = corps(req);
    const pseudo = normPseudo(b.pseudo), code = normCode(b.code), mdp = String(b.mdp || '');
    if (!pseudoValide(pseudo) || code.length !== 12) return res.status(400).json({ erreur: ERR_GENERIQUE });
    if (mdp.length < 8 || mdp.length > 128) return res.status(400).json({ erreur: 'Le nouveau mot de passe doit faire au moins 8 caractères.' });
    try {
      const uid = await ops.uidDePseudo(pseudo);
      if (!uid) return res.status(400).json({ erreur: ERR_GENERIQUE });
      const s = (await ops.lireSecours(uid)) || {};
      if (!s.hash || !s.salt) return res.status(400).json({ erreur: ERR_GENERIQUE });
      if ((s.bloqueJusqua || 0) > Date.now()) return res.status(429).json({ erreur: 'Trop d\'essais. Réessaie dans une heure.' });
      if (!egal(hashCode(code, s.salt), s.hash)) {
        const echecs = (s.echecs || 0) + 1;
        await ops.ecrireSecours(uid, echecs >= MAX_ECHECS ? { echecs: 0, bloqueJusqua: Date.now() + BLOCAGE_MS } : { echecs });
        return res.status(400).json({ erreur: ERR_GENERIQUE });
      }
      await ops.changerMdp(uid, mdp);
      // Le code utilisé est remplacé : il ne peut servir qu'une fois
      const nc = nouveauCode(), salt = crypto.randomBytes(16).toString('hex');
      await ops.ecrireSecours(uid, { hash: hashCode(nc, salt), salt, date: new Date().toISOString(), echecs: 0, bloqueJusqua: 0 });
      return res.status(200).json({ ok: true, nouveauCode: nc });
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
