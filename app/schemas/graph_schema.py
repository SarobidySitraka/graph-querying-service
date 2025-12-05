from typing import Dict, List, Optional, Any, Set
from pydantic import BaseModel, Field, field_validator
from enum import Enum
from datetime import datetime, timezone


class PropertyType(str, Enum):
    """Types de propriétés Neo4j"""
    STRING = "String"
    INTEGER = "Integer"
    FLOAT = "Float"
    BOOLEAN = "Boolean"
    DATE = "Date"
    DATETIME = "DateTime"
    POINT = "Point"
    LIST = "List"
    MAP = "Map"
    ANY = "Any"


class ConstraintType(str, Enum):
    """Types de contraintes Neo4j"""
    UNIQUE = "UNIQUE"
    NODE_KEY = "NODE_KEY"
    NODE_PROPERTY_EXISTENCE = "NODE_PROPERTY_EXISTENCE"
    RELATIONSHIP_PROPERTY_EXISTENCE = "RELATIONSHIP_PROPERTY_EXISTENCE"


class IndexType(str, Enum):
    """Types d'index Neo4j"""
    BTREE = "BTREE"
    FULLTEXT = "FULLTEXT"
    LOOKUP = "LOOKUP"
    TEXT = "TEXT"
    POINT = "POINT"


class CardinalityType(str, Enum):
    """Cardinalité des relations"""
    ONE_TO_ONE = "1:1"
    ONE_TO_MANY = "1:N"
    MANY_TO_ONE = "N:1"
    MANY_TO_MANY = "N:M"


# ============================================
# PROPERTY SCHEMA
# ============================================

class PropertySchema(BaseModel):
    """Schéma d'une propriété"""

    name: str = Field(..., description="Nom de la propriété")
    type: PropertyType = Field(..., description="Type de la propriété")
    required: bool = Field(default=False, description="Propriété obligatoire")
    indexed: bool = Field(default=False, description="Propriété indexée")
    unique: bool = Field(default=False, description="Propriété unique")
    default_value: Optional[Any] = Field(None, description="Valeur par défaut")
    description: Optional[str] = Field(None, description="Description")
    examples: List[Any] = Field(default_factory=list, description="Exemples de valeurs")
    validation_pattern: Optional[str] = Field(None, description="Pattern de validation")
    min_value: Optional[float] = Field(None, description="Valeur minimale")
    max_value: Optional[float] = Field(None, description="Valeur maximale")
    min_length: Optional[int] = Field(None, description="Longueur minimale")
    max_length: Optional[int] = Field(None, description="Longueur maximale")

    def to_cypher_type(self) -> str:
        """Convertir en type Cypher"""
        type_mapping = {
            PropertyType.STRING: "STRING",
            PropertyType.INTEGER: "INTEGER",
            PropertyType.FLOAT: "FLOAT",
            PropertyType.BOOLEAN: "BOOLEAN",
            PropertyType.DATE: "DATE",
            PropertyType.DATETIME: "DATETIME",
            PropertyType.LIST: "LIST",
            PropertyType.MAP: "MAP"
        }
        return type_mapping.get(self.type, "ANY")


# ============================================
# NODE SCHEMA
# ============================================

class NodeSchema(BaseModel):
    """Schéma d'un nœud"""

    label: str = Field(..., description="Label du nœud")
    properties: Dict[str, PropertySchema] = Field(
        default_factory=dict,
        description="Propriétés du nœud"
    )
    description: Optional[str] = Field(None, description="Description du nœud")
    primary_key: Optional[str] = Field(None, description="Clé primaire")
    display_property: Optional[str] = Field(
        default="name",
        description="Propriété à afficher par défaut"
    )
    icon: Optional[str] = Field(None, description="Icône pour visualisation")
    color: Optional[str] = Field(None, description="Couleur pour visualisation")
    count: int = Field(default=0, description="Nombre de nœuds de ce type")

    @field_validator("label")
    @classmethod
    def validate_label(cls, v: str) -> str:
        if not v or not v[0].isupper():
            raise ValueError("Le label doit commencer par une majuscule")
        return v

    def get_required_properties(self) -> List[str]:
        """Obtenir les propriétés obligatoires"""
        return [name for name, prop in self.properties.items() if prop.required]

    def get_indexed_properties(self) -> List[str]:
        """Obtenir les propriétés indexées"""
        return [name for name, prop in self.properties.items() if prop.indexed]

    def get_unique_properties(self) -> List[str]:
        """Obtenir les propriétés uniques"""
        return [name for name, prop in self.properties.items() if prop.unique]

    def to_cypher_pattern(self, variable: str = "n") -> str:
        """Générer un pattern Cypher"""
        return f"({variable}:{self.label})"

    def get_property_names(self) -> List[str]:
        """Obtenir les noms des propriétés"""
        return list(self.properties.keys())


# ============================================
# RELATIONSHIP SCHEMA
# ============================================

class RelationshipSchema(BaseModel):
    """Schéma d'une relation"""

    type: str = Field(..., description="Type de la relation")
    source_label: str = Field(..., description="Label du nœud source")
    target_label: str = Field(..., description="Label du nœud cible")
    properties: Dict[str, PropertySchema] = Field(
        default_factory=dict,
        description="Propriétés de la relation"
    )
    description: Optional[str] = Field(None, description="Description de la relation")
    cardinality: CardinalityType = Field(
        default=CardinalityType.MANY_TO_MANY,
        description="Cardinalité"
    )
    bidirectional: bool = Field(
        default=False,
        description="Relation bidirectionnelle"
    )
    count: int = Field(default=0, description="Nombre de relations de ce type")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if not v or not v.isupper():
            raise ValueError("Le type de relation doit être en majuscules")
        return v

    def to_cypher_pattern(
            self,
            source_var: str = "a",
            rel_var: str = "r",
            target_var: str = "b"
    ) -> str:
        """Générer un pattern Cypher"""
        return (
            f"({source_var}:{self.source_label})"
            f"-[{rel_var}:{self.type}]->"
            f"({target_var}:{self.target_label})"
        )

    def get_reverse_pattern(
            self,
            source_var: str = "a",
            rel_var: str = "r",
            target_var: str = "b"
    ) -> str:
        """Pattern inverse (si bidirectionnel)"""
        if self.bidirectional:
            return (
                f"({target_var}:{self.target_label})"
                f"-[{rel_var}:{self.type}]->"
                f"({source_var}:{self.source_label})"
            )
        return ""


# ============================================
# CONSTRAINT SCHEMA
# ============================================

class ConstraintSchema(BaseModel):
    """Schéma d'une contrainte"""

    name: str = Field(..., description="Nom de la contrainte")
    type: ConstraintType = Field(..., description="Type de contrainte")
    entity_type: str = Field(..., description="Node ou Relationship")
    label: str = Field(..., description="Label/Type concerné")
    properties: List[str] = Field(..., description="Propriétés concernées")
    description: Optional[str] = Field(None, description="Description")

    def to_cypher_create(self) -> str:
        """Générer la commande Cypher pour créer la contrainte"""
        props = ", ".join([f"n.{prop}" for prop in self.properties])

        if self.type == ConstraintType.UNIQUE:
            return (
                f"CREATE CONSTRAINT {self.name} IF NOT EXISTS "
                f"FOR (n:{self.label}) REQUIRE {props} IS UNIQUE"
            )
        elif self.type == ConstraintType.NODE_KEY:
            return (
                f"CREATE CONSTRAINT {self.name} IF NOT EXISTS "
                f"FOR (n:{self.label}) REQUIRE ({props}) IS NODE KEY"
            )
        elif self.type == ConstraintType.NODE_PROPERTY_EXISTENCE:
            return (
                f"CREATE CONSTRAINT {self.name} IF NOT EXISTS "
                f"FOR (n:{self.label}) REQUIRE {props} IS NOT NULL"
            )
        return ""


# ============================================
# INDEX SCHEMA
# ============================================

class IndexSchema(BaseModel):
    """Schéma d'un index"""

    name: str = Field(..., description="Nom de l'index")
    type: IndexType = Field(..., description="Type d'index")
    entity_type: str = Field(..., description="Node ou Relationship")
    label: str = Field(..., description="Label/Type concerné")
    properties: List[str] = Field(..., description="Propriétés indexées")
    description: Optional[str] = Field(None, description="Description")

    def to_cypher_create(self) -> str:
        """Générer la commande Cypher pour créer l'index"""
        props = ", ".join([f"n.{prop}" for prop in self.properties])

        if self.type == IndexType.BTREE:
            return (
                f"CREATE INDEX {self.name} IF NOT EXISTS "
                f"FOR (n:{self.label}) ON ({props})"
            )
        elif self.type == IndexType.FULLTEXT:
            props_list = ", ".join([f'"{prop}"' for prop in self.properties])
            return (
                f"CREATE FULLTEXT INDEX {self.name} IF NOT EXISTS "
                f"FOR (n:{self.label}) ON EACH [{props_list}]"
            )
        return ""


# ============================================
# GRAPH SCHEMA (PRINCIPAL)
# ============================================

class GraphSchema(BaseModel):
    """Schéma complet du graphe"""

    version: str = Field(default="1.0.0", description="Version du schéma")
    name: str = Field(..., description="Nom du schéma")
    description: Optional[str] = Field(None, description="Description")

    nodes: Dict[str, NodeSchema] = Field(
        default_factory=dict,
        description="Schémas des nœuds"
    )
    relationships: Dict[str, RelationshipSchema] = Field(
        default_factory=dict,
        description="Schémas des relations"
    )
    constraints: List[ConstraintSchema] = Field(
        default_factory=list,
        description="Contraintes"
    )
    indexes: List[IndexSchema] = Field(
        default_factory=list,
        description="Index"
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Métadonnées supplémentaires"
    )
    created_at: datetime = Field(
        default_factory= lambda : datetime.now(timezone.utc),
        description="Date de création"
    )
    updated_at: datetime = Field(
        default_factory= lambda : datetime.now(timezone.utc),
        description="Date de mise à jour"
    )

    def get_node_labels(self) -> List[str]:
        """Obtenir tous les labels de nœuds"""
        return list(self.nodes.keys())

    def get_relationship_types(self) -> List[str]:
        """Obtenir tous les types de relations"""
        return list(self.relationships.keys())

    def get_all_properties(self) -> Set[str]:
        """Obtenir toutes les propriétés utilisées"""
        props = set()
        for node in self.nodes.values():
            props.update(node.properties.keys())
        for rel in self.relationships.values():
            props.update(rel.properties.keys())
        return props

    def get_node_by_label(self, label: str) -> Optional[NodeSchema]:
        """Obtenir un nœud par son label"""
        return self.nodes.get(label)

    def get_relationship_by_type(self, rel_type: str) -> Optional[RelationshipSchema]:
        """Obtenir une relation par son type"""
        return self.relationships.get(rel_type)

    def get_relationships_for_node(self, label: str) -> List[RelationshipSchema]:
        """Obtenir toutes les relations d'un nœud"""
        return [
            rel for rel in self.relationships.values()
            if rel.source_label == label or rel.target_label == label
        ]

    def get_outgoing_relationships(self, label: str) -> List[RelationshipSchema]:
        """Obtenir les relations sortantes d'un nœud"""
        return [
            rel for rel in self.relationships.values()
            if rel.source_label == label
        ]

    def get_incoming_relationships(self, label: str) -> List[RelationshipSchema]:
        """Obtenir les relations entrantes d'un nœud"""
        return [
            rel for rel in self.relationships.values()
            if rel.target_label == label
        ]

    def get_connected_nodes(self, label: str) -> Set[str]:
        """Obtenir tous les nœuds connectés à un nœud"""
        connected = set()
        for rel in self.relationships.values():
            if rel.source_label == label:
                connected.add(rel.target_label)
            if rel.target_label == label and rel.bidirectional:
                connected.add(rel.source_label)
        return connected

    def find_path(self, source: str, target: str) -> Optional[List[str]]:
        """Trouver un chemin entre deux types de nœuds"""
        # BFS simple
        from collections import deque

        queue = deque([(source, [source])])
        visited = {source}

        while queue:
            current, path = queue.popleft()

            if current == target:
                return path

            for connected in self.get_connected_nodes(current):
                if connected not in visited:
                    visited.add(connected)
                    queue.append((connected, path + [connected]))

        return None

    def to_context_string(self, max_items: int = 50) -> str:
        """Convertir en string de contexte pour LLM"""
        context_parts = []

        # Nœuds
        node_labels = self.get_node_labels()[:max_items]
        if node_labels:
            context_parts.append(f"Labels de nœuds: {', '.join(node_labels)}")

        # Relations
        rel_types = self.get_relationship_types()[:max_items]
        if rel_types:
            context_parts.append(f"Types de relations: {', '.join(rel_types)}")

        # Propriétés
        props = list(self.get_all_properties())[:max_items]
        if props:
            context_parts.append(f"Propriétés: {', '.join(props)}")

        return "\n".join(context_parts)

    def to_detailed_context(self) -> str:
        """Convertir en contexte détaillé"""
        context = []

        context.append("=== SCHÉMA DU GRAPHE ===\n")

        # Nœuds détaillés
        context.append("NŒUDS:")
        for label, node in self.nodes.items():
            context.append(f"  - {label}:")
            if node.description:
                context.append(f"    Description: {node.description}")
            if node.properties:
                context.append(f"    Propriétés: {', '.join(node.properties.keys())}")
            if node.count > 0:
                context.append(f"    Nombre: {node.count}")

        context.append("\nRELATIONS:")
        for rel_type, rel in self.relationships.items():
            pattern = f"({rel.source_label})-[{rel_type}]->({rel.target_label})"
            context.append(f"  - {pattern}")
            if rel.description:
                context.append(f"    Description: {rel.description}")
            if rel.properties:
                context.append(f"    Propriétés: {', '.join(rel.properties.keys())}")
            if rel.count > 0:
                context.append(f"    Nombre: {rel.count}")

        return "\n".join(context)

    def get_statistics(self) -> Dict[str, Any]:
        """Obtenir les statistiques du schéma"""
        return {
            "node_types": len(self.nodes),
            "relationship_types": len(self.relationships),
            "total_node_properties": sum(
                len(node.properties) for node in self.nodes.values()
            ),
            "total_relationship_properties": sum(
                len(rel.properties) for rel in self.relationships.values()
            ),
            "constraints": len(self.constraints),
            "indexes": len(self.indexes),
            "total_nodes": sum(node.count for node in self.nodes.values()),
            "total_relationships": sum(
                rel.count for rel in self.relationships.values()
            )
        }

    def validate_schema(self) -> tuple[bool, List[str]]:
        """Valider la cohérence du schéma"""
        errors = []

        # Vérifier que les relations référencent des nœuds existants
        for rel_type, rel in self.relationships.items():
            if rel.source_label not in self.nodes:
                errors.append(
                    f"Relation {rel_type}: source '{rel.source_label}' n'existe pas"
                )
            if rel.target_label not in self.nodes:
                errors.append(
                    f"Relation {rel_type}: target '{rel.target_label}' n'existe pas"
                )

        # Vérifier les contraintes
        for constraint in self.constraints:
            if constraint.label not in self.nodes:
                errors.append(
                    f"Contrainte {constraint.name}: label '{constraint.label}' n'existe pas"
                )

        # Vérifier les index
        for index in self.indexes:
            if index.label not in self.nodes:
                errors.append(
                    f"Index {index.name}: label '{index.label}' n'existe pas"
                )

        return len(errors) == 0, errors

    def export_to_dict(self) -> Dict[str, Any]:
        """Exporter en dictionnaire"""
        return self.model_dump()

    def export_to_json(self) -> str:
        """Exporter en JSON"""
        return self.model_dump_json(indent=2)

    @classmethod
    def from_neo4j(cls, schema_data: Dict[str, Any]) -> "GraphSchema":
        """Créer un GraphSchema depuis les données Neo4j"""
        graph_schema = cls(
            name="Neo4j Graph Schema",
            description="Schéma extrait de Neo4j"
        )

        # Ajouter les nœuds
        for label in schema_data.get("node_labels", []):
            graph_schema.nodes[label] = NodeSchema(
                label=label,
                properties={},
                count=0
            )

        # Ajouter les relations (simplifié)
        for rel_type in schema_data.get("relationship_types", []):
            # On ne peut pas deviner la source et la cible sans plus d'info
            # Il faudrait une analyse plus approfondie
            pass

        return graph_schema


# ============================================
# SCHEMA BUILDER
# ============================================

class GraphSchemaBuilder:
    """Constructeur de schéma de graphe"""

    def __init__(self, name: str, description: Optional[str] = None):
        self.schema = GraphSchema(name=name, description=description)

    def add_node(
            self,
            label: str,
            properties: Optional[Dict[str, PropertySchema]] = None,
            **kwargs
    ) -> "GraphSchemaBuilder":
        """Ajouter un nœud"""
        self.schema.nodes[label] = NodeSchema(
            label=label,
            properties=properties or {},
            **kwargs
        )
        return self

    def add_relationship(
            self,
            rel_type: str,
            source_label: str,
            target_label: str,
            properties: Optional[Dict[str, PropertySchema]] = None,
            **kwargs
    ) -> "GraphSchemaBuilder":
        """Ajouter une relation"""
        self.schema.relationships[rel_type] = RelationshipSchema(
            type=rel_type,
            source_label=source_label,
            target_label=target_label,
            properties=properties or {},
            **kwargs
        )
        return self

    def add_constraint(self, constraint: ConstraintSchema) -> "GraphSchemaBuilder":
        """Ajouter une contrainte"""
        self.schema.constraints.append(constraint)
        return self

    def add_index(self, index: IndexSchema) -> "GraphSchemaBuilder":
        """Ajouter un index"""
        self.schema.indexes.append(index)
        return self

    def build(self) -> GraphSchema:
        """Construire le schéma final"""
        is_valid, errors = self.schema.validate_schema()
        if not is_valid:
            raise ValueError(f"Schéma invalide: {errors}")
        return self.schema


# ============================================
# EXEMPLE D'UTILISATION
# ============================================

def create_sample_schema() -> GraphSchema:
    """Créer un schéma d'exemple"""
    builder = GraphSchemaBuilder(
        name="Enterprise Graph",
        description="Schéma pour un graphe d'entreprise"
    )

    # Nœud Person
    builder.add_node(
        "Person",
        properties={
            "name": PropertySchema(
                name="name",
                type=PropertyType.STRING,
                required=True,
                indexed=True
            ),
            "age": PropertySchema(
                name="age",
                type=PropertyType.INTEGER,
                min_value=0,
                max_value=150
            ),
            "email": PropertySchema(
                name="email",
                type=PropertyType.STRING,
                unique=True
            )
        },
        description="Représente une personne",
        primary_key="email",
        display_property="name"
    )

    # Nœud Company
    builder.add_node(
        "Company",
        properties={
            "name": PropertySchema(
                name="name",
                type=PropertyType.STRING,
                required=True,
                unique=True
            ),
            "founded": PropertySchema(
                name="founded",
                type=PropertyType.INTEGER
            )
        },
        description="Représente une entreprise"
    )

    # Relation WORKS_AT
    builder.add_relationship(
        "WORKS_AT",
        source_label="Person",
        target_label="Company",
        properties={
            "since": PropertySchema(
                name="since",
                type=PropertyType.INTEGER
            ),
            "position": PropertySchema(
                name="position",
                type=PropertyType.STRING
            )
        },
        description="Personne travaille dans une entreprise",
        cardinality=CardinalityType.MANY_TO_ONE
    )

    return builder.build()