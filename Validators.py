from Person import Person
import Constants

def validate_wishes_age_feasibility(persons: list[Person]):
    name_to_person = {f"{p.first_name} {p.last_name}": p for p in persons}

    print("Invalid wishes: ")

    for person in persons:
        wishes = [person.wish_1, person.wish_2]
        for wish_name in wishes:
            if not wish_name:
                continue

            wished_person = name_to_person.get(wish_name)
            if not wished_person:
                print(f"Warning: {person.first_name} {person.last_name} (Klasse {person.klasse_nach_ferien}) "
                      f"has a wish for unknown person '{wish_name}'")
                continue

            age_diff = abs(person.age - wished_person.age)
            if age_diff > Constants.max_age_difference:
                print(f"Invalid wish: {person.first_name} {person.last_name} (Klasse {person.klasse_nach_ferien}, age {person.age}) "
                      f"wishes {wish_name} (age {wished_person.age}) with age difference {age_diff} (too large)")

    print("")

