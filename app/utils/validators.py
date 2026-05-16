import re

PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$")


def validate_password(value: str) -> str:
    if not PASSWORD_REGEX.match(value):
        raise ValueError(
            "Le mot de passe doit contenir au moins 8 caractères, "
            "une majuscule, une minuscule, un chiffre et un caractère spécial (@$!%*?&)"
        )
    return value


def validate_unique_service_ids(items: list) -> list:
    ids = [it.service_id for it in items]
    if len(ids) != len(set(ids)):
        raise ValueError("Un même service ne peut pas apparaître deux fois dans la commande.")
    return items


def validate_card_number(value: str) -> str:
    cleaned_value = value.replace(" ", "")
    if not (cleaned_value.isdigit() and len(cleaned_value) == 16):
        raise ValueError("Carte invalide")
    return cleaned_value
