# TopKit — Roadmap & TODO

_Mis à jour le 16 avril 2026_

---

## 🔴 Priorité 1 — Joueurs (feature en cours, backend prêt)

1. **Affichage note /100 sur la page joueur** — `compute_note()` + `note_breakdown` committés, intégration React à faire
2. **Career chart joueur visible sur PlayerDetail** — endpoint + SVG area chart committés, vérifier l'intégration finale
3. **Enrichissement batch des joueurs existants** — script ou bouton admin pour `enrich` les joueurs sans `flocking_player_id`

---

## 🟠 Priorité 2 — Page Browser (UX, impact immédiat)

4. **Toggle Club / National** — remplacer master/authentic par un filtre équipe de club vs équipe nationale
5. **Badge count versions sur les cards master kit** — petit carré avec le nombre de versions associées
6. **Filtre gender dans la recherche** — champ supplémentaire dans les filtres du browser

---

## 🟡 Priorité 3 — Page Contribution (refonte UI/UX)

7. **Refonte globale de la page Contribution** — vision communautaire : qui a ajouté quoi (brand/team/sponsor/league/player/kit), garder le système de vote
8. **Section "derniers ajouts à la DB"** — feed toutes refs confondues (brand/team/sponsor/league/player/kit)
9. **Section "meilleurs contributeurs"** — photo de profil + ID user + placeholder score gamification

---

## 🟢 Priorité 4 — Submissions & Modération

10. **Admin panel : suppression physique** sur approval d'un `removal`
11. **Notifications utilisateur** sur approbation / refus de sa submission

---

## ⚪ Priorité 5 — Pages entités & Infra

12. **Page joueur complète** — carrière, stats, maillots portés, section aura
13. **Page league** — modèle enrichi commité mais pas de page dédiée
14. **Backup automatique MongoDB Atlas**
15. **Logs centralisés + monitoring 5xx**
