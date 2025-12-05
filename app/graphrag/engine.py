from typing import Tuple, List, Dict, Any, Optional
from app.graphrag.cypher_generator import CypherGenerator
from app.graphrag.query_optimizer import QueryOptimizer, _has_limit
from app.graphrag.response_formatter import ResponseFormatter
from app.services.neo4j_service import neo4j_service
from app.services.cache_service import cache_service
from app.core.logging import get_logger
from app.core.exceptions import InvalidCypherQueryError
import time

logger = get_logger(__name__)


class GraphRAGEngine:
    """Moteur principal GraphRAG"""

    def __init__(self):
        self.cypher_generator = CypherGenerator()
        self.query_optimizer = QueryOptimizer()
        self.response_formatter = ResponseFormatter()
        self.neo4j = neo4j_service
        self.cache = cache_service
        self.logger = logger

    def process_natural_query(
        self,
        question: str,
        context: Optional[str] = None,
        use_cache: bool = True
    ) -> Tuple[str, List[Dict[str, Any]], float, str]:
        """
        Traiter une requête en langage naturel

        Args:
            question: Question en langage naturel
            context: Contexte additionnel
            use_cache: Utiliser le cache

        Returns:
            Tuple (cypher, results, execution_time_ms, natural_answer)
        """
        start_time = time.time()

        # Vérifier le cache
        if use_cache and self.cache.enabled:
            cached = self.cache.get(question, {"context": context})
            if cached:
                self.logger.info("Cache hit pour la requête")
                return (
                    cached["cypher"],
                    cached["results"],
                    cached["execution_time"],
                    cached["answer"]
                )

        # Récupérer le schéma
        schema = self.neo4j.get_schema()

        # Générer le Cypher
        self.logger.info(f"Génération Cypher pour: {question}")
        cypher = self.cypher_generator.generate(question, schema, context)

        # Optimiser le Cypher
        cypher = self.query_optimizer.optimize(cypher)

        # Vérifier que c'est read-only
        is_read_only, error_msg = self.query_optimizer.is_read_only(cypher)
        if not is_read_only:
            raise InvalidCypherQueryError(error_msg)

        # Valider le Cypher
        is_valid, validation_error = self.neo4j.validate_cypher(cypher)
        if not is_valid:
            self.logger.error(f"Cypher invalide généré: {validation_error}")
            raise InvalidCypherQueryError(
                f"Le LLM a généré une requête invalide: {validation_error}"
            )

        # Exécuter la requête
        print(f"Cypher query: {cypher}")
        results, query_time = self.neo4j.execute_cypher(cypher)

        print(f"Test to Cypher result: {results}")

        # Générer la réponse naturelle
        natural_answer = self.response_formatter.format_natural_response(
            question,
            results
        )

        total_time = (time.time() - start_time) * 1000

        # Sauvegarder dans le cache
        if use_cache and self.cache.enabled:
            self.cache.set(
                question,
                {
                    "cypher": cypher,
                    "results": results,
                    "execution_time": total_time,
                    "answer": natural_answer
                },
                {"context": context}
            )

        self.logger.info(
            f"Requête naturelle traitée en {total_time:.2f}ms "
            f"({len(results)} résultats)"
        )

        return cypher, results, total_time, natural_answer

    def process_cypher_query(
            self,
            cypher: str,
            parameters: Optional[Dict[str, Any]] = None,
            timeout: Optional[int] = None
    ) -> Tuple[List[Dict[str, Any]], float]:
        """
        Traiter une requête Cypher directe

        Args:
            cypher: Requête Cypher
            parameters: Paramètres
            timeout: Timeout

        Returns:
            Tuple (results, execution_time_ms)
        """
        # Optimiser
        cypher = self.query_optimizer.optimize(cypher)

        # Vérifier read-only
        is_read_only, error_msg = self.query_optimizer.is_read_only(cypher)
        if not is_read_only:
            raise InvalidCypherQueryError(error_msg)

        # Exécuter
        results, execution_time = self.neo4j.execute_cypher(
            cypher,
            parameters,
            timeout
        )

        return results, execution_time

    def validate_query(
            self,
            cypher: str,
            check_read_only: bool = True
    ) -> Tuple[bool, bool, Optional[str], List[str]]:
        """
        Valider une requête

        Returns:
            Tuple (is_valid, is_read_only, error_message, warnings)
        """
        warnings = []

        # Valider la syntaxe
        is_valid, error_msg = self.neo4j.validate_cypher(cypher)

        if not is_valid:
            return False, False, error_msg, warnings

        # Vérifier read-only
        is_read_only = True
        if check_read_only:
            is_read_only, read_only_error = self.query_optimizer.is_read_only(cypher)
            if not is_read_only:
                error_msg = read_only_error

        # Vérifier LIMIT
        if not _has_limit(cypher):
            warnings.append(
                f"Pas de LIMIT spécifié. Un LIMIT de {self.query_optimizer.default_limit} "
                "sera automatiquement ajouté."
            )

        return is_valid, is_read_only, error_msg, warnings


# Instance globale
graphrag_engine = GraphRAGEngine()