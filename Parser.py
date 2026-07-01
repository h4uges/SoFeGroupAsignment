import csv
from datetime import datetime
from Person import Person, Gender

def parse_persons(filepath):
    personen = []
    with open(filepath, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')

        # Feldnamen bereinigen
        reader.fieldnames = [h.strip() for h in reader.fieldnames]

        for row in reader:
            row = {k.strip(): v.strip() for k, v in row.items()}

            # Basiswerte extrahieren
            id_ = int(row["ID"])
            first_name = row["Vorname"]
            last_name = row["Nachname"]
            birth_date = datetime.strptime(row["Geburtsdatum"], "%d.%m.%Y").date()

            # Geschlecht umwandeln
            gender_str = row.get("Geschlecht", "").lower()
            if gender_str in ["m", "M"]:
                gender = Gender.MALE
            elif gender_str in ["w", "W"]:
                gender = Gender.FEMALE

            klasse = int(row["Klasse"])

            # Wünsche extrahieren
            wish_1 = row.get("Gruppenwunsch 1", "") or None
            wish_2 = row.get("Gruppenwunsch 2", "") or None

            # Bag mit restlichen Werten füllen
            bekannte_keys = ["ID", "Vorname", "Nachname", "Geburtsdatum", "Geschlecht", "Klasse nach den Ferien", "Wunsch 1", "Wunsch 2"]
            bag = {k: v for k, v in row.items() if k not in bekannte_keys}

            person = Person(
                id=id_,
                first_name=first_name,
                last_name=last_name,
                birth_date=birth_date,
                gender=gender,
                klasse_nach_ferien=klasse,
                wish_1=wish_1,
                wish_2=wish_2,
                bag=bag
            )
            personen.append(person)

    return personen