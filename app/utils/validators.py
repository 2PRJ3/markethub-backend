import re

PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$")


def validate_password(value: str) -> str:
    if not PASSWORD_REGEX.match(value):
        raise ValueError(
            "Le mot de passe doit contenir au moins 8 caractères, "
            "une majuscule, une minuscule, un chiffre et un caractère spécial (@$!%*?&)"
        )
    return value
