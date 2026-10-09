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

## Connexion (démonstration)
Le bouton **Se connecter**, en haut à droite, ouvre la fenêtre de connexion. On s'identifie avec son e-mail ou son matricule.

| Compte | Identifiant | Matricule | Mot de passe |
|---|---|---|---|
| Camille Martin, technicienne (Lyon) | `camille.martin@smartfactory.fr` | `SF10234` | `Usine2026!` |
| Sophie Lambert, DRH (Siège) | `sophie.lambert@smartfactory.fr` | `SF00001` | `DRH2026!` |

- Sans connexion, on peut lire les actualités, la FAQ, l'annuaire et les guides.
- Aimer un article, voter, proposer une idée ou répondre au sondage et au baromètre demande d'être connecté. L'action reprend automatiquement après la connexion.
- « Se souvenir de moi » garde la session sur l'appareil. Sinon, elle s'arrête à la fermeture de l'onglet.
- Pour ajouter un compte, ajoutez-le à la liste `USERS` dans `index.html`.

⚠️ **C'est une simulation**, pas une vraie sécurité : les mots de passe sont lisibles dans le code de la page. Avant une utilisation réelle, branchez une vraie authentification côté serveur, par exemple le SSO de l'entreprise (Microsoft Entra ID / Azure AD), ou l'authentification Netlify (Identity) pour un pilote.

Navigation : barre d'onglets en bas sur mobile, menu latéral à partir de 768 px. Les liens profonds fonctionnent (`index.html#faq`).

## Données
Toutes les données factices sont regroupées dans la section `2. DONNÉES FACTICES` du script (`NEWS`, `FAQ`, `DIRECTORY`, `POLL`, `GUIDES`, `CHATBOT`…).
Les votes, idées et notes sont enregistrés dans le `localStorage` du navigateur (objet `Store`). Pour brancher un vrai back-end, remplacez `Store.get` / `Store.set` par des appels API.

## Contenu du dossier
```
smartfactory-rh/
├── index.html               ← l'application
├── manifest.webmanifest     ← installation sur l'écran d'accueil du téléphone
├── netlify.toml             ← configuration Netlify de ce site
└── images/
    ├── logo.svg / favicon.svg          ← logo (en-tête + onglet du navigateur)
    ├── icon-192.png / icon-512.png     ← icônes Android / Chrome
    ├── icon-maskable-512.png           ← icône Android adaptative
    ├── apple-touch-icon.png            ← icône iPhone / iPad
    ├── og-image.png                    ← aperçu quand le lien est partagé (Teams, WhatsApp…)
    ├── hero-usine.svg                  ← décor du bandeau d'accueil
    └── news/*.svg                      ← illustrations des 8 actualités
```
**Uploadez le dossier entier** : `index.html` cherche les images dans `images/`, à côté de lui.

## Remplacer les images
- **Photo d'actualité** : déposez la photo dans `images/news/` (JPG ou WebP, environ 800×400 px, moins de 200 Ko), puis changez le champ `img` de l'article dans `NEWS` : `img: 'images/news/ma-photo.jpg'`. Si une image manque, l'emoji de l'article s'affiche à la place.
- **Nouvel article sans image** : supprimez simplement le champ `img`.
- **Logo** : remplacez `images/logo.svg` et `images/favicon.svg` en gardant les mêmes noms (format carré). Remplacez aussi les PNG (192, 512 et 180 px) pour les téléphones.

## Héberger la page
### Option 1 : GitHub Pages (gratuit)
1. Fusionnez la branche dans `main`.
2. Sur GitHub : **Settings → Pages → Source : Deploy from a branch → `main` / `/ (root)` → Save**.
3. Après 1 à 2 minutes, la page est en ligne : `https://<compte>.github.io/<depot>/smartfactory-rh/`.

GitHub Pages gratuit nécessite un dépôt **public**. Pour un intranet, préférez un dépôt privé avec un hébergement protégé (option 2 ou 3).

### Option 2 : Netlify
1. Netlify → **Add new site → Import an existing project** → choisissez ce dépôt.
2. **Base directory** : `smartfactory-rh` (Netlify lit alors `smartfactory-rh/netlify.toml`). Laissez la commande de build vide.
3. **Deploy**. Pour restreindre l'accès aux salariés, activez la protection par mot de passe ou l'authentification dans les réglages du site.

Le `netlify.toml` à la racine du dépôt publie le site Miguel Automatismes. Ne le modifiez pas : créez un **second site** Netlify pour SmartFactory RH.

### Option 3 : serveur interne / SharePoint
Copiez le dossier `smartfactory-rh/` tel quel sur n'importe quel serveur web. Aucune configuration n'est nécessaire.

### Après la mise en ligne
Pour que l'aperçu fonctionne quand on partage le lien, remplacez dans `index.html` `content="images/og-image.png"` par l'adresse complète, par exemple `content="https://votre-site.netlify.app/images/og-image.png"`. Teams, WhatsApp et LinkedIn exigent une adresse complète.
