"""
Sanitizers pour nettoyer et valider les entrées utilisateur
Prévient les injections et les données malformées
"""
import re
import html
from typing import Optional, Dict, Any, List
from app.core.logging import get_logger

logger = get_logger(__name__)


class InputSanitizer:
    """Sanitizer général pour les entrées utilisateur"""

    # Caractères dangereux à enlever ou échapper
    DANGEROUS_CHARS = ['<', '>', '{', '}', '`', '\\x00']

    # Patterns d'injection courants
    INJECTION_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # XSS
        r'javascript:',  # JavaScript URI
        r'on\w+\s*=',  # Event handlers
        r'<iframe[^>]*>',  # iframes
        r'<object[^>]*>',  # objects
        r'<embed[^>]*>',  # embeds
    ]

    @staticmethod
    def sanitize_string(
            text: str,
            max_length: Optional[int] = None,
            strip: bool = True,
            escape_html: bool = True,
            remove_dangerous: bool = True
    ) -> str:
        """
        Nettoyer une chaîne de caractères

        Args:
            text: Texte à nettoyer
            max_length: Longueur maximale
            strip: Enlever les espaces
            escape_html: Échapper le HTML
            remove_dangerous: Enlever les caractères dangereux

        Returns:
            Texte nettoyé
        """
        if not text:
            return ""

        # Strip espaces
        if strip:
            text = text.strip()

        # Échapper HTML
        if escape_html:
            text = html.escape(text)

        # Enlever caractères dangereux
        if remove_dangerous:
            for char in InputSanitizer.DANGEROUS_CHARS:
                text = text.replace(char, '')

        # Enlever patterns d'injection
        for pattern in InputSanitizer.INJECTION_PATTERNS:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        # Normaliser espaces multiples
        text = re.sub(r'\s+', ' ', text)

        # Limiter longueur
        if max_length and len(text) > max_length:
            text = text[:max_length]
            logger.warning(f"Texte tronqué à {max_length} caractères")

        return text

    @staticmethod
    def sanitize_email(email: str) -> str:
        """
        Nettoyer et valider un email

        Args:
            email: Email à nettoyer

        Returns:
            Email nettoyé

        Raises:
            ValueError: Si email invalide
        """
        email = email.strip().lower()

        # Pattern email basique
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(pattern, email):
            raise ValueError("Format d'email invalide")

        return email

    @staticmethod
    def sanitize_url(url: str) -> str:
        """
        Nettoyer et valider une URL

        Args:
            url: URL à nettoyer

        Returns:
            URL nettoyée

        Raises:
            ValueError: Si URL invalide
        """
        url = url.strip()

        # Vérifier le protocole
        if not url.startswith(('http://', 'https://')):
            raise ValueError("URL doit commencer par http:// ou https://")

        # Enlever javascript: et autres protocoles dangereux
        dangerous_protocols = ['javascript:', 'data:', 'vbscript:']
        for protocol in dangerous_protocols:
            if protocol in url.lower():
                raise ValueError(f"Protocole non autorisé: {protocol}")

        return url


class QuerySanitizer:
    """Sanitizer spécifique pour les requêtes"""

    # Mots-clés SQL/Cypher dangereux
    DANGEROUS_KEYWORDS = [
        'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE',
        'INSERT', 'UPDATE', 'EXEC', 'EXECUTE', 'SCRIPT'
    ]

    @staticmethod
    def sanitize_question(
            question: str,
            max_length: int = 1000,
            allow_special_chars: bool = False
    ) -> str:
        """
        Nettoyer une question en langage naturel

        Args:
            question: Question à nettoyer
            max_length: Longueur maximale
            allow_special_chars: Autoriser caractères spéciaux

        Returns:
            Question nettoyée
        """
        # Nettoyer avec InputSanitizer
        question = InputSanitizer.sanitize_string(
            question,
            max_length=max_length,
            escape_html=True,
            remove_dangerous=not allow_special_chars
        )

        # Vérifier les mots-clés dangereux
        question_upper = question.upper()
        for keyword in QuerySanitizer.DANGEROUS_KEYWORDS:
            if f' {keyword} ' in f' {question_upper} ':
                logger.warning(f"Mot-clé suspect détecté: {keyword}")

        return question

    @staticmethod
    def sanitize_cypher(cypher: str) -> str:
        """
        Nettoyer une requête Cypher

        Args:
            cypher: Requête Cypher à nettoyer

        Returns:
            Requête nettoyée
        """
        # Enlever commentaires
        cypher = re.sub(r'//.*?$', '', cypher, flags=re.MULTILINE)
        cypher = re.sub(r'/\*.*?\*/', '', cypher, flags=re.DOTALL)

        # Normaliser espaces
        cypher = ' '.join(cypher.split())

        # Enlever ; multiples
        cypher = re.sub(r';+', ';', cypher)

        return cypher.strip()

    @staticmethod
    def sanitize_cypher_parameters(
            parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Nettoyer les paramètres Cypher

        Args:
            parameters: Paramètres à nettoyer

        Returns:
            Paramètres nettoyés
        """
        if not parameters:
            return {}

        sanitized = {}

        for key, value in parameters.items():
            # Nettoyer la clé
            clean_key = re.sub(r'[^\w_]', '', key)

            # Nettoyer la valeur selon le type
            if isinstance(value, str):
                clean_value = InputSanitizer.sanitize_string(value)
            elif isinstance(value, (list, tuple)):
                clean_value = [
                    InputSanitizer.sanitize_string(v) if isinstance(v, str) else v
                    for v in value
                ]
            else:
                clean_value = value

            sanitized[clean_key] = clean_value

        return sanitized


class PathSanitizer:
    """Sanitizer pour les chemins de fichiers"""

    # Caractères interdits dans les chemins
    FORBIDDEN_CHARS = ['..', '~', '\\', '|', '>', '<', '?', '*']

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Nettoyer un nom de fichier

        Args:
            filename: Nom de fichier à nettoyer

        Returns:
            Nom de fichier nettoyé

        Raises:
            ValueError: Si le nom est invalide
        """
        # Enlever le chemin si présent
        filename = filename.split('/')[-1].split('\\')[-1]

        # Vérifier caractères interdits
        for char in PathSanitizer.FORBIDDEN_CHARS:
            if char in filename:
                raise ValueError(f"Caractère interdit dans le nom: {char}")

        # Enlever caractères non-alphanumériques (garde ., -, _)
        filename = re.sub(r'[^\w.-]', '_', filename)

        # Limiter longueur
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')

        return filename

    @staticmethod
    def sanitize_path(path: str) -> str:
        """
        Nettoyer un chemin de fichier

        Args:
            path: Chemin à nettoyer

        Returns:
            Chemin nettoyé

        Raises:
            ValueError: Si le chemin est invalide
        """
        # Vérifier path traversal
        if '..' in path:
            raise ValueError("Path traversal détecté")

        # Normaliser les séparateurs
        path = path.replace('\\', '/')

        # Enlever / multiples
        path = re.sub(r'/+', '/', path)

        # Enlever / au début et à la fin
        path = path.strip('/')

        return path


class JSONSanitizer:
    """Sanitizer pour les données JSON"""

    @staticmethod
    def sanitize_dict(
            data: Dict[str, Any],
            max_depth: int = 10,
            current_depth: int = 0
    ) -> Dict[str, Any]:
        """
        Nettoyer un dictionnaire récursivement

        Args:
            data: Dictionnaire à nettoyer
            max_depth: Profondeur maximale
            current_depth: Profondeur actuelle

        Returns:
            Dictionnaire nettoyé
        """
        if current_depth >= max_depth:
            logger.warning(f"Profondeur maximale atteinte: {max_depth}")
            return {}

        sanitized = {}

        for key, value in data.items():
            # Nettoyer la clé
            clean_key = InputSanitizer.sanitize_string(
                str(key),
                max_length=100,
                escape_html=False
            )

            # Nettoyer la valeur selon le type
            if isinstance(value, str):
                clean_value = InputSanitizer.sanitize_string(value)
            elif isinstance(value, dict):
                clean_value = JSONSanitizer.sanitize_dict(
                    value,
                    max_depth,
                    current_depth + 1
                )
            elif isinstance(value, list):
                clean_value = JSONSanitizer.sanitize_list(
                    value,
                    max_depth,
                    current_depth + 1
                )
            else:
                clean_value = value

            sanitized[clean_key] = clean_value

        return sanitized

    @staticmethod
    def sanitize_list(
            data: List[Any],
            max_depth: int = 10,
            current_depth: int = 0
    ) -> List[Any]:
        """
        Nettoyer une liste récursivement

        Args:
            data: Liste à nettoyer
            max_depth: Profondeur maximale
            current_depth: Profondeur actuelle

        Returns:
            Liste nettoyée
        """
        if current_depth >= max_depth:
            return []

        sanitized = []

        for item in data[:1000]:  # Limite à 1000 items
            if isinstance(item, str):
                sanitized.append(InputSanitizer.sanitize_string(item))
            elif isinstance(item, dict):
                sanitized.append(
                    JSONSanitizer.sanitize_dict(item, max_depth, current_depth + 1)
                )
            elif isinstance(item, list):
                sanitized.append(
                    JSONSanitizer.sanitize_list(item, max_depth, current_depth + 1)
                )
            else:
                sanitized.append(item)

        return sanitized


class SQLInjectionSanitizer:
    """Sanitizer spécifique pour prévenir les injections SQL/Cypher"""

    # Patterns d'injection SQL courants
    SQL_INJECTION_PATTERNS = [
        r"('\s*(OR|AND)\s*'?\d)",  # ' OR '1'='1
        r"('\s*;\s*DROP)",  # '; DROP TABLE
        r"('\s*--)",  # ' --
        r"('\s*/\*)",  # ' /*
        r"(UNION\s+SELECT)",  # UNION SELECT
        r"(INSERT\s+INTO)",  # INSERT INTO
        r"(UPDATE\s+\w+\s+SET)",  # UPDATE ... SET
    ]

    @staticmethod
    def detect_sql_injection(text: str) -> bool:
        """
        Détecter une tentative d'injection SQL

        Args:
            text: Texte à analyser

        Returns:
            True si injection détectée
        """
        for pattern in SQLInjectionSanitizer.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Injection SQL détectée: {pattern}")
                return True
        return False

    @staticmethod
    def sanitize_for_query(text: str) -> str:
        """
        Nettoyer un texte pour l'utiliser dans une requête

        Args:
            text: Texte à nettoyer

        Returns:
            Texte nettoyé

        Raises:
            ValueError: Si injection détectée
        """
        if SQLInjectionSanitizer.detect_sql_injection(text):
            raise ValueError("Tentative d'injection SQL détectée")

        # Échapper les quotes
        text = text.replace("'", "''")
        text = text.replace('"', '""')

        return text


# Fonctions utilitaires exportées
def sanitize_input(text: str, **kwargs) -> str:
    """Fonction helper pour sanitize_string"""
    return InputSanitizer.sanitize_string(text, **kwargs)


def sanitize_question(question: str, **kwargs) -> str:
    """Fonction helper pour sanitize_question"""
    return QuerySanitizer.sanitize_question(question, **kwargs)


def sanitize_cypher(cypher: str) -> str:
    """Fonction helper pour sanitize_cypher"""
    return QuerySanitizer.sanitize_cypher(cypher)


def sanitize_dict(data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Fonction helper pour sanitize_dict"""
    return JSONSanitizer.sanitize_dict(data, **kwargs)


def detect_injection(text: str) -> bool:
    """Fonction helper pour detect_sql_injection"""
    return SQLInjectionSanitizer.detect_sql_injection(text)