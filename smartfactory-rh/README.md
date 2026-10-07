# SmartFactory RH — Intranet RH mobile-first

Application monopage (un seul fichier `index.html`) : HTML + Tailwind CSS (CDN) + JavaScript natif. Aucune compilation.

## Tester
Double-cliquez sur `index.html` : il s'ouvre dans votre navigateur. Une connexion Internet est nécessaire pour charger Tailwind et la police Inter.

## Fonctionnalités
| Onglet | Contenu |
|---|---|
| 📰 Actus | Fil d'actualités filtrable (Politiques RH, Vie d'entreprise, Sites de production), cartes cliquables (lecture en modale), « J'aime » |
| ❓ FAQ | Recherche en temps réel (insensible aux accents, mots surlignés), accordéons |
| 💡 Participer | Baromètre eNPS (note 0–10, score calculé), sondage avec barres de résultats animées, boîte à idées (formulaire + votes +1, tri) |
| 👥 Annuaire | Cartes des interlocuteurs RH, filtres par site, expertise et nom, boutons Appeler / E-mail |
| 🧭 Guides | Espace conduite du changement : tutoriels pas à pas, progression et badge |
| 💬 Chatbot | Assistante « Léa » : congés, paie, mutuelle, télétravail (mots-clés et suggestions rapides) |

Navigation : barre d'onglets en bas sur mobile, menu latéral à partir de 768 px. Les liens profonds fonctionnent (`index.html#faq`).

## Données
Toutes les données factices sont regroupées dans la section `2. DONNÉES FACTICES` du script (`NEWS`, `FAQ`, `DIRECTORY`, `POLL`, `GUIDES`, `CHATBOT`…).
Les votes, idées et notes sont enregistrés dans le `localStorage` du navigateur (objet `Store`). Pour brancher un vrai back-end, remplacez `Store.get` / `Store.set` par des appels API.

## Déploiement
Fichier statique : à déposer tel quel sur Netlify, GitHub Pages, SharePoint, un serveur web interne, etc.
