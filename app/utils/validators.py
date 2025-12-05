import re
from typing import Tuple


class CypherValidator:
    """Validateur de requêtes Cypher"""

    WRITE_KEYWORDS = [
        'CREATE', 'DELETE', 'REMOVE', 'SET', 'MERGE',
        'DROP', 'ALTER', 'DETACH'
    ]

    @staticmethod
    def is_read_only(cypher: str) -> Tuple[bool, str]:
        """Vérifier si c'est en lecture seule"""
        cypher_upper = cypher.upper()

        for keyword in CypherValidator.WRITE_KEYWORDS:
            pattern = r'\b' + keyword + r'\b'
            if re.search(pattern, cypher_upper):
                return False, f"Mot-clé non autorisé: {keyword}"

        return True, ""

    @staticmethod
    def has_limit(cypher: str) -> bool:
        """Vérifier si LIMIT existe"""
        return bool(re.search(r'\bLIMIT\s+\d+', cypher, re.IGNORECASE))

    @staticmethod
    def extract_limit(cypher: str) -> int:
        """Extraire la valeur de LIMIT"""
        match = re.search(r'\bLIMIT\s+(\d+)', cypher, re.IGNORECASE)
        return int(match.group(1)) if match else 0

    @staticmethod
    def contains_parameters(cypher: str) -> bool:
        """Vérifier si la requête contient des paramètres"""
        return bool(re.search(r'\$\w+', cypher))


class QuerySanitizer:
    """Sanitizer pour les requêtes"""

    @staticmethod
    def sanitize_question(question: str, max_length: int = 1000) -> str:
        """Nettoyer une question"""
        # Enlever espaces multiples
        question = ' '.join(question.split())

        # Limiter la longueur
        if len(question) > max_length:
            question = question[:max_length]

        # Enlever caractères dangereux
        question = re.sub(r'[<>{}]', '', question)

        return question.strip()

    @staticmethod
    def sanitize_cypher(cypher: str) -> str:
        """Nettoyer une requête Cypher"""
        # Enlever commentaires
        cypher = re.sub(r'//.*?$', '', cypher, flags=re.MULTILINE)
        cypher = re.sub(r'/\*.*?\*/', '', cypher, flags=re.DOTALL)

        # Normaliser espaces
        cypher = ' '.join(cypher.split())

        return cypher.strip()