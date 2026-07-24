/*
 * Service worker KineCotation — PRUDENT et AUTH-AWARE.
 *
 * Regle d'or : on ne cache QUE le shell statique public et immuable
 * (assets sous /static/ : coeur OCR tesseract, icones PWA). TOUT le reste —
 * la page « / » gardee par login, /login, /logout, /api/* (dont l'OCR :
 * donnees de sante + auth) — passe DIRECTEMENT au reseau (network-only).
 * Le SW n'appelle respondWith QUE pour /static/ ; pour le reste il ne fait
 * rien => le navigateur va au reseau normalement.
 *
 * Requis pour l'installabilite Android (un fetch handler doit exister).
 */
'use strict';

const CACHE = 'kinecotation-static-v1';

// pre-cache leger : uniquement des assets publics et surs (jamais de HTML gardee)
const PRECACHE = [
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  '/static/icons/icon-512-maskable.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE)
      .then((c) => c.addAll(PRECACHE))
      .catch(() => {})           // pre-cache best-effort : n'empeche jamais l'install
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.map((k) => (k === CACHE ? null : caches.delete(k)))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;                  // POST /api/ocr -> reseau

  let url;
  try { url = new URL(req.url); } catch (e) { return; }

  // seul l'origine courante + le prefixe public /static/ sont interceptes
  if (url.origin !== self.location.origin) return;   // tiers -> reseau
  if (!url.pathname.startsWith('/static/')) return;  // /, /login, /api/* -> reseau

  // cache-first sur les assets publics immuables
  event.respondWith(
    caches.match(req).then((hit) => {
      if (hit) return hit;
      return fetch(req).then((res) => {
        if (res && res.ok && res.type === 'basic') {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
        }
        return res;
      });
    })
  );
});
