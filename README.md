# 📚 Mes Cours

Une petite application web **locale** pour organiser tes cours de fac :

- **Matières** : nom, enseignant·e, couleur
- **Notes de cours** par matière et par date (tu peux les modifier)
- **Fichiers joints** (PDF, diapos, Word…) par matière
- **Échéances** (rendus, examens, partiels…) avec une date et une case « fait ». Les prochaines s'affichent sur la page d'accueil, en rouge à 3 jours ou moins, en orange à 7 jours ou moins.

Tout est enregistré **sur ton ordinateur**, dans le dossier `donnees/`. Rien n'est envoyé sur Internet.

---

## 🚀 Lancer l'application

### Étape 1 : installer Python (une seule fois)

- **Windows** : télécharge Python sur <https://www.python.org/downloads/>.
  ⚠️ Pendant l'installation, **coche la case « Add Python to PATH »**.
- **Mac** : télécharge Python sur le même site et installe-le.

Pour vérifier, ouvre un terminal et tape `python --version` (Windows) ou `python3 --version` (Mac).
Tu dois voir quelque chose comme `Python 3.12.x`.

> **Ouvrir un terminal** : sous Windows, appuie sur la touche Windows, tape « PowerShell » puis Entrée.
> Sur Mac, fais Cmd + Espace, tape « Terminal » puis Entrée.

### Étape 2 : aller dans le dossier du projet

Dans le terminal, tape `cd ` (avec un espace), puis **fais glisser le dossier du projet** dans la
fenêtre du terminal : son chemin s'écrit tout seul. Appuie sur Entrée.

### Étape 3 : installer Flask (une seule fois)

Flask est la « boîte à outils » qui transforme notre code Python en site web.

```bash
# Windows
python -m pip install -r requirements.txt

# Mac
python3 -m pip install -r requirements.txt
```

### Étape 4 : démarrer

```bash
# Windows
python app.py

# Mac
python3 app.py
```

Le terminal affiche :

```
  ✅ Mes Cours est lancé !
  👉 Ouvre ton navigateur à l'adresse : http://127.0.0.1:5000
```

Ouvre cette adresse dans ton navigateur (Chrome, Firefox, Safari…). C'est parti ! 🎉

**Laisse le terminal ouvert** tant que tu utilises l'application.
Pour l'arrêter, clique dans le terminal et fais **Ctrl + C**.
Les fois suivantes, seules les étapes 2 et 4 sont nécessaires.

---

## 🗂️ Comment le projet est organisé

```
mes-cours/
├── app.py              ← le « cerveau » : toute la logique en Python
├── requirements.txt    ← la liste des outils à installer (juste Flask)
├── templates/          ← les pages HTML (ce que tu vois)
│   ├── base.html           le squelette commun (menu en haut, messages)
│   ├── _macros.html        petits morceaux réutilisés (ligne d'échéance, carte de matière)
│   ├── accueil.html        la page d'accueil
│   ├── matieres.html       la liste des matières et leur création
│   ├── matiere.html        la page d'une matière (notes, fichiers, échéances)
│   ├── note.html           la modification d'une note
│   ├── echeances.html      toutes les échéances
│   └── erreur.html         la page « introuvable »
├── static/
│   └── style.css       ← le design (couleurs, tailles, mise en page)
└── donnees/            ← créé automatiquement au premier lancement
    ├── cours.db            ta base de données
    └── fichiers/           tes PDF et tes diapos
```

---

## 🧠 Comment ça marche ? (explication pas à pas)

### 1. Le navigateur et le serveur
Quand tu lances `python app.py`, ton ordinateur devient un petit **serveur web**.
Le navigateur lui demande des pages (par exemple `http://127.0.0.1:5000/matieres`) et le serveur
les lui renvoie. `127.0.0.1` veut dire « cet ordinateur-ci » : personne d'autre n'y a accès.

### 2. Les routes (dans `app.py`)
Chaque adresse est reliée à une fonction Python grâce à `@app.route(...)` :

```python
@app.route("/echeances")
def echeances():
    ...  # va chercher les échéances dans la base, puis affiche echeances.html
```

- **GET** veut dire « montre-moi une page » (quand tu cliques sur un lien).
- **POST** veut dire « enregistre ces informations » (quand tu valides un formulaire).

### 3. La base de données (SQLite)
Les données sont rangées dans des **tables**, comme des feuilles Excel :

| Table       | Colonnes principales                         |
|-------------|----------------------------------------------|
| `matieres`  | nom, enseignant, couleur                     |
| `notes`     | matiere_id, date, titre, contenu             |
| `fichiers`  | matiere_id, nom_original, nom_stocke         |
| `echeances` | matiere_id, titre, type, date, faite         |

La colonne `matiere_id` relie une note (ou un fichier, ou une échéance) à sa matière.
On parle à la base en langage **SQL**, par exemple :

```sql
SELECT * FROM notes WHERE matiere_id = 3 ORDER BY date DESC
```

Cette phrase veut dire : « donne-moi toutes les notes de la matière n°3, les plus récentes d'abord ».

### 4. Les fichiers joints
Quand tu joins un PDF, il est copié dans `donnees/fichiers/` sous un nom unique,
pour que deux fichiers qui s'appellent tous les deux « cours.pdf » ne s'écrasent pas.
La base garde le vrai nom du fichier pour te l'afficher.

### 5. Les templates (dans `templates/`)
Ce sont des pages HTML avec des « trous » que Python remplit, grâce au moteur **Jinja** :

```html
{% for m in matieres %}
  <p>{{ m.nom }}</p>
{% endfor %}
```

Ce code veut dire : « pour chaque matière, affiche son nom ».
`base.html` contient le menu, et les autres pages le réutilisent avec `{% extends "base.html" %}`.

### 6. Le design (`static/style.css`)
Les couleurs principales sont regroupées en haut du fichier (`--accent`, `--fond`…).
Remplace `--accent: #4f7cff;` par une autre couleur pour personnaliser l'application !
Le thème sombre s'active tout seul si ton ordinateur est en mode sombre.

---

## 💾 Sauvegarder tes données

Tout est dans le dossier **`donnees/`**. Pour faire une sauvegarde, copie simplement
ce dossier sur une clé USB ou dans ton cloud. Pour restaurer, remets-le à côté de `app.py`.

> Git ignore ce dossier (grâce au fichier `.gitignore`) : tes cours ne partent pas sur GitHub.

---

## ❓ Problèmes fréquents

| Problème | Solution |
|---|---|
| `python` n'est pas reconnu | Réinstalle Python en cochant « Add Python to PATH », ou essaie `py app.py` (Windows) ou `python3 app.py` (Mac). |
| `No module named flask` | L'étape 3 n'a pas été faite : lance la commande d'installation de Flask. |
| `Address already in use` | L'application tourne déjà dans un autre terminal. Ferme-le, ou utilise l'onglet déjà ouvert. |
| La page ne s'affiche pas | Vérifie que le terminal est toujours ouvert et que l'adresse est bien `http://127.0.0.1:5000`. |
