# KinéCotation — OCR pour ordonnances NOMINATIVES : ce qui est confirmé

> 2026-07-18. But : envoyer des ordonnances **sans anonymiser** (données de santé identifiées)
> de façon licite. Recherche en **sources primaires** (DPA, docs fournisseurs, périmètres HDS
> publics ANS), sans devis. Critère = réglementaire (HDS + non-rétention + DPA, FR/UE), pas qualité OCR.

---

## La clé qui reframe tout : HDS certifie l'HÉBERGEMENT, pas le « traitement IA »

La certification HDS (ANS) couvre **6 activités d'hébergement** : datacenters, matériel, plateforme
d'hébergement applicatif, infra virtuelle, administration, sauvegarde. **Il n'existe pas d'activité
« inférence IA / OCR ».** Donc « OCR certifié HDS » est mal posé. La bonne question :
1. la donnée est-elle **hébergée** (même transitoirement pendant l'inférence) sur une infra **HDS** ?
2. le service **retient-il / entraîne-t-il** dessus ?
[esante.gouv.fr — certification HDS](https://esante.gouv.fr/offres-services/hds/liste-des-hebergeurs-certifies)

---

## Faits confirmés en source primaire

**Mistral « La Plateforme » (notre intégration actuelle) — INAPTE au nominatif.** Le DPA officiel :
rétention **30 jours** ; Mistral **se réserve l'entraînement** sur les données « sauf option
désactivée ou produit exclu par défaut » ; le ZDR n'est cité qu'en passant (exception au
monitoring d'abus, sans préciser l'offre) ; **aucune mention HDS** ; Exhibit 1 : « catégories
particulières de données : **Aucune** » (le DPA tel quel ne couvre donc pas la santé).
→ OK pour le test **anonymisé**, exclu pour le nominatif sans contrat Enterprise + ZDR dédié.
[legal.mistral.ai — DPA](https://legal.mistral.ai/terms/data-processing-addendum)

**Scaleway Generative APIs — ZDR par défaut, mais PAS dans le périmètre HDS.** La doc confirme :
**Zero Data Retention par défaut**, données **non utilisées pour l'entraînement**, Scaleway « ne
collecte, ne lit, ne réutilise ni n'analyse » les entrées/sorties. MAIS la FAQ dit noir sur blanc
que le périmètre HDS = « **CPU/GPU Instances, Object/Block Storage, Bare Metal, VPC** » (+ contrat
HDS + plan support Business/Enterprise) — **les Generative APIs (managées) n'y sont pas**.
→ Managé = test anonymisé seulement. Mais ça ouvre la voie B ci-dessous (héberger soi-même sur GPU HDS).
[scaleway — data privacy](https://www.scaleway.com/en/docs/generative-apis/reference-content/data-privacy/) ·
[scaleway — santé](https://www.scaleway.com/en/healthcare-and-life-sciences-solutions/)

**Outscale (Dassault) + Mistral souverain — infra HDS + ZDR par contrat.** Outscale héberge « La
Plateforme » de Mistral sur cloud souverain **SecNumCloud 3.2 + HDS**, offre santé (PariSanté
Campus), dispo depuis sept. 2025. Précédent réel : **PulseLife** tourne sous **contrat ZDR** (Mistral
ne retient ni n'entraîne). → Voie managée conforme, mais via **contrat** (le ZDR n'est pas par défaut).
[usine-digitale](https://www.usine-digitale.fr/article/outscale-structure-son-cloud-souverain-autour-de-l-ia-avec-mistral-du-quantique-et-de-la-sante.N2233332) ·
[LLMaaS by Outscale](https://en.outscale.com/llmaas-by-outscale/) ·
[PulseLife](https://pulselife.com/fr-fr/blog/post/ia-medicale-entierement-souveraine)

**Docaposte — HDS oui, mais pas une API OCR santé.** Certifié HDS (via l'archivage Arkhineo,
« 1er opérateur de données de santé en France »), mais son OCR/LAD est orienté **facture** et
intégration entreprise, pas une API d'extraction d'ordonnances self-service. Non-rétention non
confirmée. → Déprioritisé.
[docaposte — certifications](https://www.docaposte.com/en/our-certifications)

---

## Les DEUX voies réellement conformes (les deux ont un pré-requis incontournable)

### Voie A — Managée : Outscale + Mistral souverain + contrat ZDR
On **garde l'OCR Mistral déjà intégré** (`llm.py` bascule par endpoint). HDS = hébergement Outscale ;
non-rétention = clause ZDR du contrat. **Pré-requis : contrat souverain Outscale/Mistral avec ZDR**
(procurement). Le moins d'ops, la meilleure qualité OCR, souveraineté SecNumCloud.

### Voie B — Auto-hébergée : modèle OCR open sur GPU HDS (Scaleway ou Outscale)
Faire tourner un modèle OCR/vision open (Mistral open-weights, ou un OCR dédié) sur des **GPU
Instances dans le périmètre HDS** (Scaleway : contrat HDS + support Business ; ou Outscale). **La
donnée ne quitte jamais notre infra HDS** : pas de sous-traitant tiers qui la voit, rétention qu'on
contrôle, pas besoin de faire confiance au ZDR d'un tiers. **Pré-requis : contrat HDS + on opère
l'inférence** (plus d'ops). Souveraineté maximale. On n'a pas à être soi-même certifié HDS : héberger
sur une infra certifiée sous contrat HDS suffit.

---

## Verdict honnête

**Il n'existe aucune API OCR managée, self-service, HDS + ZDR confirmée** : ni Mistral (ni HDS ni ZDR
par défaut), ni Scaleway Generative APIs (ZDR oui, HDS non). Donc le nominatif reste **un pré-requis
contractuel** (voie A) **ou opérationnel** (voie B) — pas un interrupteur. Mais c'est désormais **cadré
et sourcé**, pas flou :

- Test de Malcom **maintenant** : ordonnances **anonymisées** (Mistral standard ou Scaleway managé, les
  deux OK anonymisé ; Scaleway a l'avantage du ZDR par défaut).
- Nominatif : **voie A** (procurement Outscale/Mistral ZDR) si on veut le moins d'ops et garder Mistral ;
  **voie B** (auto-hébergé GPU HDS) si on veut la souveraineté maximale sans dépendre d'un tiers.
- Le travail technique est fait : l'abstraction `llm.py` rend les deux voies quasi triviales à câbler.

## INCERTITUDES restantes
- Voie A : périmètre exact du contrat ZDR Outscale/Mistral + prix — non public, mais le **précédent
  PulseLife prouve que ça existe**.
- Voie B : quel modèle OCR open atteint la qualité voulue sur manuscrit FR (à benchmarker) + coût GPU.
- Scaleway : bascule éventuelle des Generative APIs dans le périmètre HDS — à resurveiller (évolutif).
