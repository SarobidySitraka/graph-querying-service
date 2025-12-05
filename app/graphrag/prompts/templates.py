from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class PromptType(str, Enum):
    """Types de prompts"""
    CYPHER_GENERATION = "cypher_generation"
    RESPONSE_FORMATTING = "response_formatting"
    QUERY_REFINEMENT = "query_refinement"
    ERROR_EXPLANATION = "error_explanation"
    SCHEMA_ANALYSIS = "schema_analysis"


@dataclass
class PromptTemplate:
    """Template de prompt avec variables"""

    template: str
    variables: List[str]
    description: str
    examples: Optional[List[Dict[str, str]]] = None

    def format(self, **kwargs) -> str:
        """Formater le template avec les variables"""
        missing_vars = set(self.variables) - set(kwargs.keys())
        if missing_vars:
            raise ValueError(f"Variables manquantes: {missing_vars}")

        return self.template.format(**kwargs)

    def validate_variables(self, **kwargs) -> bool:
        """Valider que toutes les variables sont présentes"""
        return set(self.variables).issubset(set(kwargs.keys()))


class CypherGenerationTemplates:
    """Templates pour la génération de Cypher"""

    BASIC_GENERATION = PromptTemplate(
        template="""Tu es un expert en Neo4j et Cypher. Convertis la question suivante en requête Cypher valide.

Question: {question}

Schéma disponible:
{schema}

Règles:
- Génère UNIQUEMENT la requête Cypher, sans explication
- Utilise SEULEMENT les éléments du schéma fourni
- Ajoute toujours un LIMIT approprié (max 100)
- Pas d'opérations d'écriture (CREATE, DELETE, etc.)

Requête Cypher:""",
        variables=["question", "schema"],
        description="Template de base pour génération Cypher"
    )

    WITH_CONTEXT = PromptTemplate(
        template="""Tu es un expert en Neo4j et Cypher. Convertis la question en requête Cypher en tenant compte du contexte.

Question: {question}

Contexte additionnel: {context}

Schéma disponible:
{schema}

Historique des requêtes similaires:
{history}

Règles:
- Génère UNIQUEMENT la requête Cypher
- Tiens compte du contexte pour mieux comprendre l'intention
- Utilise les patterns des requêtes historiques similaires
- Limite à {limit} résultats

Requête Cypher:""",
        variables=["question", "context", "schema", "history", "limit"],
        description="Template avec contexte étendu"
    )

    WITH_EXAMPLES = PromptTemplate(
        template="""Tu es un expert en Neo4j et Cypher. Génère une requête Cypher basée sur ces exemples.

Question: {question}

Schéma:
{schema}

Exemples de requêtes similaires:
{examples}

Instructions spécifiques:
{instructions}

Génère la requête Cypher:""",
        variables=["question", "schema", "examples", "instructions"],
        description="Template avec exemples de requêtes"
    )

    COMPLEX_QUERY = PromptTemplate(
        template="""Expert Neo4j: Génère une requête Cypher complexe pour cette analyse.

Analyse demandée: {question}

Schéma complet:
Nœuds: {node_labels}
Relations: {relationship_types}
Propriétés: {properties}

Contraintes: {constraints}

Exigences:
{requirements}

Optimisations suggérées:
- Utilise des index si disponibles
- Évite les cartesian products
- Utilise WITH pour les étapes intermédiaires
- Profile la requête si nécessaire

Génère la requête optimisée:""",
        variables=["question", "node_labels", "relationship_types", "properties",
                   "constraints", "requirements"],
        description="Template pour requêtes complexes"
    )

    AGGREGATION_QUERY = PromptTemplate(
        template="""Génère une requête Cypher pour cette agrégation/analyse.

Question: {question}

Métriques demandées: {metrics}

Groupement par: {group_by}

Schéma:
{schema}

Règles d'agrégation:
- Utilise count(), sum(), avg(), min(), max() selon le besoin
- Groupe correctement avec GROUP BY implicite
- Ordonne les résultats de manière pertinente
- Limite à {limit} résultats

Requête Cypher:""",
        variables=["question", "metrics", "group_by", "schema", "limit"],
        description="Template pour requêtes d'agrégation"
    )


class ResponseFormattingTemplates:
    """Templates pour le formatage des réponses"""

    NATURAL_RESPONSE = PromptTemplate(
        template="""Génère une réponse en langage naturel à partir de ces résultats.

Question originale: {question}

Résultats de la base de données:
{results}

Contexte: {context}

Instructions:
- Réponds de manière claire et concise en français
- Base-toi UNIQUEMENT sur les résultats fournis
- Structure ta réponse de manière logique
- Si les résultats sont vides, indique qu'aucune information n'a été trouvée
- Utilise des nombres et des statistiques quand pertinent
- Ne mentionne PAS les aspects techniques (nœuds, relations, etc.)

Réponse:""",
        variables=["question", "results", "context"],
        description="Template pour réponses naturelles"
    )

    DETAILED_ANALYSIS = PromptTemplate(
        template="""Analyse en détail ces résultats et fournis une réponse structurée.

Question: {question}

Données:
{results}

Nombre total de résultats: {count}

Fournis une analyse comprenant:
1. Résumé exécutif (2-3 phrases)
2. Points clés (bullet points)
3. Insights intéressants
4. Recommandations si pertinent

Format de réponse:""",
        variables=["question", "results", "count"],
        description="Template pour analyses détaillées"
    )

    COMPARISON_RESPONSE = PromptTemplate(
        template="""Compare et analyse ces différents ensembles de résultats.

Question: {question}

Ensemble A ({label_a}):
{results_a}

Ensemble B ({label_b}):
{results_b}

Métriques de comparaison: {metrics}

Fournis une analyse comparative incluant:
- Différences principales
- Similitudes
- Tendances observées
- Conclusions

Analyse:""",
        variables=["question", "label_a", "results_a", "label_b", "results_b", "metrics"],
        description="Template pour comparaisons"
    )

    SUMMARY_RESPONSE = PromptTemplate(
        template="""Résume ces résultats de manière concise.

Question: {question}

Résultats ({count} éléments):
{results}

Crée un résumé concis (max {max_words} mots) qui:
- Capture l'essentiel
- Utilise des statistiques clés
- Reste factuel

Résumé:""",
        variables=["question", "results", "count", "max_words"],
        description="Template pour résumés concis"
    )


class QueryRefinementTemplates:
    """Templates pour l'affinement de requêtes"""

    OPTIMIZE_QUERY = PromptTemplate(
        template="""Optimise cette requête Cypher pour de meilleures performances.

Requête originale:
{original_query}

Schéma:
{schema}

Index disponibles: {indexes}

Problèmes identifiés:
{issues}

Optimisations à appliquer:
- Réordonne les patterns pour filtrer tôt
- Utilise les index
- Évite les scans complets
- Réduis les cartesian products

Requête optimisée:""",
        variables=["original_query", "schema", "indexes", "issues"],
        description="Template pour optimisation"
    )

    FIX_SYNTAX_ERROR = PromptTemplate(
        template="""Corrige les erreurs de syntaxe dans cette requête Cypher.

Requête avec erreurs:
{faulty_query}

Erreur détectée:
{error_message}

Schéma de référence:
{schema}

Corrige la requête en:
- Fixant la syntaxe
- Respectant le schéma
- Gardant l'intention originale

Requête corrigée:""",
        variables=["faulty_query", "error_message", "schema"],
        description="Template pour correction d'erreurs"
    )

    SIMPLIFY_QUERY = PromptTemplate(
        template="""Simplifie cette requête Cypher tout en gardant la même fonctionnalité.

Requête complexe:
{complex_query}

Objectif: {goal}

Simplifie en:
- Réduisant la complexité
- Gardant la logique
- Améliorant la lisibilité

Requête simplifiée:""",
        variables=["complex_query", "goal"],
        description="Template pour simplification"
    )


class ErrorExplanationTemplates:
    """Templates pour expliquer les erreurs"""

    EXPLAIN_ERROR = PromptTemplate(
        template="""Explique cette erreur à l'utilisateur de manière claire.

Requête qui a échoué:
{failed_query}

Message d'erreur technique:
{error_message}

Contexte:
{context}

Fournis:
1. Explication simple de l'erreur
2. Cause probable
3. Suggestions pour corriger
4. Exemple de requête correcte si possible

Explication:""",
        variables=["failed_query", "error_message", "context"],
        description="Template pour expliquer les erreurs"
    )

    SUGGEST_ALTERNATIVES = PromptTemplate(
        template="""Suggère des alternatives à cette requête qui a échoué.

Question originale: {question}

Requête échouée: {failed_query}

Raison de l'échec: {reason}

Schéma disponible:
{schema}

Suggère 2-3 approches alternatives qui pourraient fonctionner.

Alternatives:""",
        variables=["question", "failed_query", "reason", "schema"],
        description="Template pour suggestions alternatives"
    )


class SchemaAnalysisTemplates:
    """Templates pour l'analyse de schéma"""

    ANALYZE_SCHEMA = PromptTemplate(
        template="""Analyse ce schéma Neo4j et identifie les patterns utiles pour la question.

Question: {question}

Schéma:
Nœuds: {nodes}
Relations: {relationships}
Propriétés: {properties}

Identifie:
- Nœuds pertinents pour la question
- Relations à utiliser
- Propriétés importantes
- Patterns de traversée suggérés

Analyse:""",
        variables=["question", "nodes", "relationships", "properties"],
        description="Template pour analyse de schéma"
    )

    SUGGEST_SCHEMA_PATH = PromptTemplate(
        template="""Suggère le meilleur chemin dans le graphe pour répondre à cette question.

Question: {question}

Nœud de départ: {start_node}
Nœud d'arrivée: {end_node}

Relations possibles: {relationships}

Suggère le pattern de traversée optimal:""",
        variables=["question", "start_node", "end_node", "relationships"],
        description="Template pour suggestion de chemin"
    )


class PromptTemplateManager:
    """Gestionnaire de templates de prompts"""

    def __init__(self):
        self.templates: Dict[str, Dict[str, PromptTemplate]] = {
            "cypher_generation": {
                "basic": CypherGenerationTemplates.BASIC_GENERATION,
                "with_context": CypherGenerationTemplates.WITH_CONTEXT,
                "with_examples": CypherGenerationTemplates.WITH_EXAMPLES,
                "complex": CypherGenerationTemplates.COMPLEX_QUERY,
                "aggregation": CypherGenerationTemplates.AGGREGATION_QUERY,
            },
            "response_formatting": {
                "natural": ResponseFormattingTemplates.NATURAL_RESPONSE,
                "detailed": ResponseFormattingTemplates.DETAILED_ANALYSIS,
                "comparison": ResponseFormattingTemplates.COMPARISON_RESPONSE,
                "summary": ResponseFormattingTemplates.SUMMARY_RESPONSE,
            },
            "query_refinement": {
                "optimize": QueryRefinementTemplates.OPTIMIZE_QUERY,
                "fix_syntax": QueryRefinementTemplates.FIX_SYNTAX_ERROR,
                "simplify": QueryRefinementTemplates.SIMPLIFY_QUERY,
            },
            "error_explanation": {
                "explain": ErrorExplanationTemplates.EXPLAIN_ERROR,
                "alternatives": ErrorExplanationTemplates.SUGGEST_ALTERNATIVES,
            },
            "schema_analysis": {
                "analyze": SchemaAnalysisTemplates.ANALYZE_SCHEMA,
                "path": SchemaAnalysisTemplates.SUGGEST_SCHEMA_PATH,
            }
        }

    def get_template(self, category: str, name: str) -> PromptTemplate:
        """Récupérer un template"""
        if category not in self.templates:
            raise ValueError(f"Catégorie invalide: {category}")

        if name not in self.templates[category]:
            raise ValueError(f"Template invalide: {name} dans {category}")

        return self.templates[category][name]

    def list_templates(self, category: Optional[str] = None) -> Dict[str, List[str]]:
        """Lister les templates disponibles"""
        if category:
            return {category: list(self.templates.get(category, {}).keys())}
        return {cat: list(temps.keys()) for cat, temps in self.templates.items()}

    def register_template(
            self,
            category: str,
            name: str,
            template: PromptTemplate
    ) -> None:
        """Enregistrer un nouveau template"""
        if category not in self.templates:
            self.templates[category] = {}

        self.templates[category][name] = template


# Instance globale
template_manager = PromptTemplateManager()