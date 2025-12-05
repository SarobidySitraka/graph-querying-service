from typing import Any, Dict, List
import json

class ResponseFormatter:
    """Formateur de réponses"""

    @staticmethod
    def format_results(
            results: List[Dict[str, Any]],
            limit: int = None
    ) -> List[Dict[str, Any]]:
        """Formater les résultats"""
        if limit and len(results) > limit:
            results = results[:limit]

        # Convertir les types Neo4j en types Python standards
        formatted = []
        for result in results:
            formatted_result = {}
            for key, value in result.items():
                formatted_result[key] = ResponseFormatter._convert_value(value)
            formatted.append(formatted_result)

        return formatted

    @staticmethod
    def _convert_value(value: Any) -> Any:
        """Convertir une valeur Neo4j"""
        if isinstance(value, (list, tuple)):
            return [ResponseFormatter._convert_value(v) for v in value]
        elif isinstance(value, dict):
            return {k: ResponseFormatter._convert_value(v) for k, v in value.items()}
        elif hasattr(value, '__dict__'):
            # Nœud ou relation Neo4j
            return dict(value)
        else:
            return value

    @staticmethod
    def to_json(data: Any, indent: int = None) -> str:
        """Convertir en JSON"""
        return json.dumps(
            data,
            ensure_ascii=False,
            default=str,
            indent=indent
        )