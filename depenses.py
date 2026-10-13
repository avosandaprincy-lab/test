# Calculateur de dépenses de la semaine.
# Lance-le avec :  python3 depenses.py

totaux = {}

print("=== Mes dépenses de la semaine ===")
print("Tape 'fin' comme catégorie quand tu as terminé.")
print()

while True:
    categorie = input("Catégorie (ex : courses, transport) : ").strip().lower()

    if categorie == "fin":
        break

    if categorie == "":
        print("La catégorie ne peut pas être vide.")
        continue

    montant_texte = input("Montant en euros : ").replace(",", ".")

    try:
        montant = float(montant_texte)
    except ValueError:
        print("Ce n'est pas un nombre valide, recommence.")
        continue

    if montant < 0:
        print("Le montant doit être positif.")
        continue

    totaux[categorie] = totaux.get(categorie, 0) + montant
    print(f"OK : {montant:.2f} € ajoutés à « {categorie} ».")
    print()

print()
print("=== Total par catégorie ===")

if not totaux:
    print("Aucune dépense saisie.")
else:
    for categorie, total in sorted(totaux.items()):
        print(f"{categorie:<15} {total:>10.2f} €")

    total_general = sum(totaux.values())
    print("-" * 28)
    print(f"{'TOTAL':<15} {total_general:>10.2f} €")
