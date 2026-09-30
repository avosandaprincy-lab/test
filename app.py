"""
Mes Cours — une petite application web locale pour organiser ses cours de fac.

Ce fichier contient TOUT le « cerveau » de l'application :
  1. la configuration (où ranger les données) ;
  2. la base de données (création des tables) ;
  3. les « routes » : chaque adresse web (ex. /matieres) est reliée
     à une fonction Python qui décide quoi afficher ou enregistrer.

Pour lancer l'application :  python app.py
Puis ouvrir dans le navigateur :  http://127.0.0.1:5000
"""

import os
import sqlite3
import uuid
from datetime import date, datetime

from flask import (
    Flask,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from werkzeug.utils import secure_filename

# ---------------------------------------------------------------------------
# 1. CONFIGURATION
# ---------------------------------------------------------------------------

# Dossier où se trouve ce fichier app.py
DOSSIER_APP = os.path.dirname(os.path.abspath(__file__))

# Toutes tes données sont rangées dans le dossier « donnees » à côté de app.py :
#   donnees/cours.db      -> la base de données (matières, notes, échéances)
#   donnees/fichiers/     -> les PDF, diapos, etc. que tu joins
DOSSIER_DONNEES = os.path.join(DOSSIER_APP, "donnees")
DOSSIER_FICHIERS = os.path.join(DOSSIER_DONNEES, "fichiers")
CHEMIN_BASE = os.path.join(DOSSIER_DONNEES, "cours.db")

# Types de fichiers acceptés en pièce jointe
EXTENSIONS_AUTORISEES = {
    "pdf", "ppt", "pptx", "odp", "doc", "docx", "odt",
    "xls", "xlsx", "ods", "txt", "md", "png", "jpg", "jpeg", "gif", "zip",
}

# Types d'échéances proposés dans la liste déroulante
TYPES_ECHEANCE = ["Rendu", "Examen", "Partiel", "Oral", "TP", "Autre"]

app = Flask(__name__)
# Clé nécessaire pour afficher les petits messages de confirmation (« flash »).
# L'application ne tourne que sur ton ordinateur, une valeur fixe suffit.
app.config["SECRET_KEY"] = "mes-cours-cle-locale"
# Taille maximale d'un fichier envoyé : 50 Mo
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024


# ---------------------------------------------------------------------------
# 2. BASE DE DONNÉES (SQLite : un simple fichier, rien à installer)
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS matieres (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nom         TEXT NOT NULL,
    enseignant  TEXT,
    couleur     TEXT NOT NULL DEFAULT '#4f7cff'
);

CREATE TABLE IF NOT EXISTS notes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    matiere_id  INTEGER NOT NULL REFERENCES matieres(id) ON DELETE CASCADE,
    date        TEXT NOT NULL,          -- format AAAA-MM-JJ
    titre       TEXT NOT NULL,
    contenu     TEXT
);

CREATE TABLE IF NOT EXISTS fichiers (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    matiere_id   INTEGER NOT NULL REFERENCES matieres(id) ON DELETE CASCADE,
    nom_original TEXT NOT NULL,         -- le nom que tu vois
    nom_stocke   TEXT NOT NULL,         -- le nom unique sur le disque
    date_ajout   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS echeances (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    matiere_id  INTEGER REFERENCES matieres(id) ON DELETE CASCADE,
    titre       TEXT NOT NULL,
    type        TEXT NOT NULL,
    date        TEXT NOT NULL,          -- format AAAA-MM-JJ
    faite       INTEGER NOT NULL DEFAULT 0
);
"""


def get_db():
    """Ouvre (une seule fois par requête) la connexion à la base de données."""
    if "db" not in g:
        g.db = sqlite3.connect(CHEMIN_BASE)
        g.db.row_factory = sqlite3.Row  # permet d'écrire ligne["nom"]
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def fermer_db(exception):
    """Referme la connexion à la fin de chaque requête."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def initialiser():
    """Crée les dossiers et les tables s'ils n'existent pas encore."""
    os.makedirs(DOSSIER_FICHIERS, exist_ok=True)
    with sqlite3.connect(CHEMIN_BASE) as db:
        db.executescript(SCHEMA)


# ---------------------------------------------------------------------------
# Petites fonctions utiles pour l'affichage des dates en français
# ---------------------------------------------------------------------------

MOIS = ["janv.", "févr.", "mars", "avr.", "mai", "juin",
        "juil.", "août", "sept.", "oct.", "nov.", "déc."]
JOURS = ["lun.", "mar.", "mer.", "jeu.", "ven.", "sam.", "dim."]


@app.template_filter("date_fr")
def date_fr(texte):
    """'2026-10-05' -> 'lun. 5 oct. 2026'"""
    try:
        d = date.fromisoformat(texte)
    except (TypeError, ValueError):
        return texte
    return f"{JOURS[d.weekday()]} {d.day} {MOIS[d.month - 1]} {d.year}"


@app.template_filter("dans")
def dans(texte):
    """Transforme une date en texte relatif : « aujourd'hui », « dans 3 jours »…"""
    try:
        ecart = (date.fromisoformat(texte) - date.today()).days
    except (TypeError, ValueError):
        return ""
    if ecart == 0:
        return "aujourd'hui"
    if ecart == 1:
        return "demain"
    if ecart > 1:
        return f"dans {ecart} jours"
    if ecart == -1:
        return "hier"
    return f"il y a {-ecart} jours"


@app.template_filter("urgence")
def urgence(texte):
    """Renvoie une classe CSS selon la proximité de la date (pour la couleur)."""
    try:
        ecart = (date.fromisoformat(texte) - date.today()).days
    except (TypeError, ValueError):
        return ""
    if ecart < 0:
        return "passee"
    if ecart <= 3:
        return "urgente"
    if ecart <= 7:
        return "proche"
    return ""


def page_retour(defaut):
    """Adresse où revenir après un formulaire (uniquement une page de l'appli)."""
    retour = request.form.get("retour", "")
    if retour.startswith("/") and not retour.startswith("//"):
        return retour
    return defaut


def trouver_matiere(matiere_id):
    """Récupère une matière ou affiche une page « introuvable » (erreur 404)."""
    matiere = get_db().execute(
        "SELECT * FROM matieres WHERE id = ?", (matiere_id,)
    ).fetchone()
    if matiere is None:
        abort(404)
    return matiere


# ---------------------------------------------------------------------------
# 3. LES PAGES (routes)
# ---------------------------------------------------------------------------

# ----- Accueil ------------------------------------------------------------

@app.route("/")
def accueil():
    db = get_db()
    aujourd_hui = date.today().isoformat()
    # Les 5 prochaines échéances non terminées, de la plus proche à la plus lointaine
    prochaines = db.execute(
        """SELECT e.*, m.nom AS matiere_nom, m.couleur AS matiere_couleur
           FROM echeances e LEFT JOIN matieres m ON m.id = e.matiere_id
           WHERE e.faite = 0 AND e.date >= ?
           ORDER BY e.date LIMIT 5""",
        (aujourd_hui,),
    ).fetchall()
    # Échéances dépassées mais pas encore cochées « faite »
    en_retard = db.execute(
        "SELECT COUNT(*) FROM echeances WHERE faite = 0 AND date < ?",
        (aujourd_hui,),
    ).fetchone()[0]
    matieres = db.execute(
        """SELECT m.*,
                  (SELECT COUNT(*) FROM notes n WHERE n.matiere_id = m.id) AS nb_notes,
                  (SELECT COUNT(*) FROM fichiers f WHERE f.matiere_id = m.id) AS nb_fichiers
           FROM matieres m ORDER BY m.nom COLLATE NOCASE"""
    ).fetchall()
    return render_template(
        "accueil.html", prochaines=prochaines, en_retard=en_retard, matieres=matieres
    )


# ----- Matières -----------------------------------------------------------

@app.route("/matieres", methods=["GET", "POST"])
def matieres():
    db = get_db()
    if request.method == "POST":
        # Le formulaire « Nouvelle matière » a été envoyé
        nom = request.form.get("nom", "").strip()
        if not nom:
            flash("Le nom de la matière est obligatoire.", "erreur")
        else:
            db.execute(
                "INSERT INTO matieres (nom, enseignant, couleur) VALUES (?, ?, ?)",
                (nom, request.form.get("enseignant", "").strip(),
                 request.form.get("couleur", "#4f7cff")),
            )
            db.commit()
            flash(f"Matière « {nom} » créée.", "succes")
        return redirect(url_for("matieres"))

    liste = db.execute(
        """SELECT m.*,
                  (SELECT COUNT(*) FROM notes n WHERE n.matiere_id = m.id) AS nb_notes,
                  (SELECT COUNT(*) FROM fichiers f WHERE f.matiere_id = m.id) AS nb_fichiers
           FROM matieres m ORDER BY m.nom COLLATE NOCASE"""
    ).fetchall()
    return render_template("matieres.html", matieres=liste)


@app.route("/matieres/<int:matiere_id>")
def matiere(matiere_id):
    db = get_db()
    m = trouver_matiere(matiere_id)
    notes = db.execute(
        "SELECT * FROM notes WHERE matiere_id = ? ORDER BY date DESC, id DESC",
        (matiere_id,),
    ).fetchall()
    fichiers = db.execute(
        "SELECT * FROM fichiers WHERE matiere_id = ? ORDER BY date_ajout DESC",
        (matiere_id,),
    ).fetchall()
    echeances = db.execute(
        "SELECT * FROM echeances WHERE matiere_id = ? ORDER BY faite, date",
        (matiere_id,),
    ).fetchall()
    return render_template(
        "matiere.html",
        matiere=m,
        notes=notes,
        fichiers=fichiers,
        echeances=echeances,
        types=TYPES_ECHEANCE,
        aujourd_hui=date.today().isoformat(),
    )


@app.route("/matieres/<int:matiere_id>/modifier", methods=["POST"])
def modifier_matiere(matiere_id):
    trouver_matiere(matiere_id)
    nom = request.form.get("nom", "").strip()
    if not nom:
        flash("Le nom de la matière est obligatoire.", "erreur")
    else:
        db = get_db()
        db.execute(
            "UPDATE matieres SET nom = ?, enseignant = ?, couleur = ? WHERE id = ?",
            (nom, request.form.get("enseignant", "").strip(),
             request.form.get("couleur", "#4f7cff"), matiere_id),
        )
        db.commit()
        flash("Matière mise à jour.", "succes")
    return redirect(url_for("matiere", matiere_id=matiere_id))


@app.route("/matieres/<int:matiere_id>/supprimer", methods=["POST"])
def supprimer_matiere(matiere_id):
    m = trouver_matiere(matiere_id)
    db = get_db()
    # On supprime d'abord les fichiers joints du disque…
    for f in db.execute(
        "SELECT nom_stocke FROM fichiers WHERE matiere_id = ?", (matiere_id,)
    ):
        chemin = os.path.join(DOSSIER_FICHIERS, f["nom_stocke"])
        if os.path.exists(chemin):
            os.remove(chemin)
    # …puis la matière (ses notes, fichiers et échéances partent avec : « CASCADE »)
    db.execute("DELETE FROM matieres WHERE id = ?", (matiere_id,))
    db.commit()
    flash(f"Matière « {m['nom']} » supprimée.", "succes")
    return redirect(url_for("matieres"))


# ----- Notes de cours -----------------------------------------------------

@app.route("/matieres/<int:matiere_id>/notes", methods=["POST"])
def ajouter_note(matiere_id):
    trouver_matiere(matiere_id)
    titre = request.form.get("titre", "").strip()
    date_note = request.form.get("date") or date.today().isoformat()
    if not titre:
        flash("Donne un titre à ta note.", "erreur")
    else:
        db = get_db()
        db.execute(
            "INSERT INTO notes (matiere_id, date, titre, contenu) VALUES (?, ?, ?, ?)",
            (matiere_id, date_note, titre, request.form.get("contenu", "")),
        )
        db.commit()
        flash("Note ajoutée.", "succes")
    return redirect(url_for("matiere", matiere_id=matiere_id) + "#notes")


@app.route("/notes/<int:note_id>/modifier", methods=["GET", "POST"])
def modifier_note(note_id):
    db = get_db()
    note = db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    if note is None:
        abort(404)
    if request.method == "POST":
        titre = request.form.get("titre", "").strip()
        if not titre:
            flash("Donne un titre à ta note.", "erreur")
            return redirect(url_for("modifier_note", note_id=note_id))
        db.execute(
            "UPDATE notes SET date = ?, titre = ?, contenu = ? WHERE id = ?",
            (request.form.get("date") or note["date"], titre,
             request.form.get("contenu", ""), note_id),
        )
        db.commit()
        flash("Note enregistrée.", "succes")
        return redirect(url_for("matiere", matiere_id=note["matiere_id"]) + "#notes")
    return render_template(
        "note.html", note=note, matiere=trouver_matiere(note["matiere_id"])
    )


@app.route("/notes/<int:note_id>/supprimer", methods=["POST"])
def supprimer_note(note_id):
    db = get_db()
    note = db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    if note is None:
        abort(404)
    db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    db.commit()
    flash("Note supprimée.", "succes")
    return redirect(url_for("matiere", matiere_id=note["matiere_id"]) + "#notes")


# ----- Fichiers joints ----------------------------------------------------

def extension_autorisee(nom):
    return "." in nom and nom.rsplit(".", 1)[1].lower() in EXTENSIONS_AUTORISEES


@app.route("/matieres/<int:matiere_id>/fichiers", methods=["POST"])
def ajouter_fichier(matiere_id):
    trouver_matiere(matiere_id)
    envoyes = [f for f in request.files.getlist("fichiers") if f and f.filename]
    if not envoyes:
        flash("Choisis au moins un fichier.", "erreur")
    db = get_db()
    ajoutes = 0
    for fichier in envoyes:
        if not extension_autorisee(fichier.filename):
            flash(f"Type de fichier non accepté : {fichier.filename}", "erreur")
            continue
        # On donne au fichier un nom unique sur le disque pour éviter
        # qu'un fichier du même nom en écrase un autre.
        extension = fichier.filename.rsplit(".", 1)[1].lower()
        nom_stocke = f"{uuid.uuid4().hex}.{extension}"
        fichier.save(os.path.join(DOSSIER_FICHIERS, nom_stocke))
        db.execute(
            """INSERT INTO fichiers (matiere_id, nom_original, nom_stocke, date_ajout)
               VALUES (?, ?, ?, ?)""",
            (matiere_id, fichier.filename, nom_stocke,
             datetime.now().isoformat(timespec="minutes")),
        )
        ajoutes += 1
    db.commit()
    if ajoutes:
        flash(f"{ajoutes} fichier(s) ajouté(s).", "succes")
    return redirect(url_for("matiere", matiere_id=matiere_id) + "#fichiers")


@app.route("/fichiers/<int:fichier_id>")
def ouvrir_fichier(fichier_id):
    f = get_db().execute(
        "SELECT * FROM fichiers WHERE id = ?", (fichier_id,)
    ).fetchone()
    if f is None:
        abort(404)
    # Ouvre le fichier dans le navigateur (les PDF s'affichent directement)
    return send_from_directory(
        DOSSIER_FICHIERS,
        f["nom_stocke"],
        download_name=secure_filename(f["nom_original"]) or f["nom_stocke"],
    )


@app.route("/fichiers/<int:fichier_id>/supprimer", methods=["POST"])
def supprimer_fichier(fichier_id):
    db = get_db()
    f = db.execute("SELECT * FROM fichiers WHERE id = ?", (fichier_id,)).fetchone()
    if f is None:
        abort(404)
    chemin = os.path.join(DOSSIER_FICHIERS, f["nom_stocke"])
    if os.path.exists(chemin):
        os.remove(chemin)
    db.execute("DELETE FROM fichiers WHERE id = ?", (fichier_id,))
    db.commit()
    flash(f"Fichier « {f['nom_original']} » supprimé.", "succes")
    return redirect(url_for("matiere", matiere_id=f["matiere_id"]) + "#fichiers")


# ----- Échéances ----------------------------------------------------------

@app.route("/echeances", methods=["GET", "POST"])
def echeances():
    db = get_db()
    if request.method == "POST":
        titre = request.form.get("titre", "").strip()
        date_ech = request.form.get("date", "")
        matiere_id = request.form.get("matiere_id") or None
        if not titre or not date_ech:
            flash("Le titre et la date sont obligatoires.", "erreur")
        else:
            db.execute(
                """INSERT INTO echeances (matiere_id, titre, type, date)
                   VALUES (?, ?, ?, ?)""",
                (matiere_id, titre, request.form.get("type", "Autre"), date_ech),
            )
            db.commit()
            flash("Échéance ajoutée.", "succes")
        # Revenir sur la page d'où vient le formulaire (liste ou matière)
        return redirect(page_retour(url_for("echeances")))

    aujourd_hui = date.today().isoformat()
    requete = """SELECT e.*, m.nom AS matiere_nom, m.couleur AS matiere_couleur
                 FROM echeances e LEFT JOIN matieres m ON m.id = e.matiere_id"""
    a_venir = db.execute(
        requete + " WHERE e.faite = 0 AND e.date >= ? ORDER BY e.date", (aujourd_hui,)
    ).fetchall()
    en_retard = db.execute(
        requete + " WHERE e.faite = 0 AND e.date < ? ORDER BY e.date", (aujourd_hui,)
    ).fetchall()
    faites = db.execute(
        requete + " WHERE e.faite = 1 ORDER BY e.date DESC"
    ).fetchall()
    liste_matieres = db.execute(
        "SELECT id, nom FROM matieres ORDER BY nom COLLATE NOCASE"
    ).fetchall()
    return render_template(
        "echeances.html",
        a_venir=a_venir,
        en_retard=en_retard,
        faites=faites,
        matieres=liste_matieres,
        types=TYPES_ECHEANCE,
        aujourd_hui=aujourd_hui,
    )


@app.route("/echeances/<int:echeance_id>/basculer", methods=["POST"])
def basculer_echeance(echeance_id):
    """Coche / décoche une échéance comme « faite »."""
    db = get_db()
    db.execute(
        "UPDATE echeances SET faite = 1 - faite WHERE id = ?", (echeance_id,)
    )
    db.commit()
    return redirect(page_retour(url_for("echeances")))


@app.route("/echeances/<int:echeance_id>/supprimer", methods=["POST"])
def supprimer_echeance(echeance_id):
    db = get_db()
    db.execute("DELETE FROM echeances WHERE id = ?", (echeance_id,))
    db.commit()
    flash("Échéance supprimée.", "succes")
    return redirect(page_retour(url_for("echeances")))


# ----- Erreurs ------------------------------------------------------------

@app.errorhandler(404)
def introuvable(e):
    return render_template("erreur.html", message="Page introuvable."), 404


@app.errorhandler(413)
def trop_gros(e):
    flash("Fichier trop volumineux (50 Mo maximum).", "erreur")
    return redirect(request.referrer or url_for("accueil"))


# ---------------------------------------------------------------------------
# DÉMARRAGE
# ---------------------------------------------------------------------------

initialiser()

if __name__ == "__main__":
    print("\n  ✅ Mes Cours est lancé !")
    print("  👉 Ouvre ton navigateur à l'adresse : http://127.0.0.1:5000")
    print("  (Pour arrêter l'application : Ctrl + C dans ce terminal)\n")
    # host="127.0.0.1" : l'application n'est visible que depuis ton ordinateur
    app.run(host="127.0.0.1", port=5000, debug=False)
