"""
Système de types pour EpiNetLang
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass
import numpy as np

class TypeCategory(Enum):
    """Catégories de types"""
    SCALAR = "scalar"
    COMPOSITE = "composite"
    FUNCTION = "function"
    NETWORK = "network"
    MODEL = "model"
    DATA = "data"

@dataclass
class Type:
    """Type dans le système de types"""
    name: str
    category: TypeCategory
    attributes: Dict[str, 'Type'] = None
    methods: Dict[str, 'FunctionType'] = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}
        if self.methods is None:
            self.methods = {}

    def __str__(self):
        return self.name

@dataclass
class FunctionType:
    """Type de fonction"""
    parameters: List[Type]
    return_type: Type
    
    def __init__(self, parameters: List[Type], return_type: Type):
        self.parameters = parameters
        self.return_type = return_type
        self.category = TypeCategory.FUNCTION
    
    def __str__(self):
        params = ", ".join(str(p) for p in self.parameters)
        return f"({params}) -> {self.return_type}"

class TypeSystem:
    """Système de types pour EpiNetLang"""
    
    def __init__(self):
        self.types: Dict[str, Type] = {}
        self._initialize_builtin_types()
    
    def _initialize_builtin_types(self):
        """Initialiser les types intégrés"""
        
        # Types scalaires
        self.types['int'] = Type('int', TypeCategory.SCALAR)
        self.types['float'] = Type('float', TypeCategory.SCALAR)
        self.types['bool'] = Type('bool', TypeCategory.SCALAR)
        self.types['string'] = Type('string', TypeCategory.SCALAR)
        
        # Type Matrix
        matrix_type = Type('Matrix', TypeCategory.COMPOSITE)
        matrix_type.methods = {
            'transpose': FunctionType([], self.types['Matrix']),
            'inverse': FunctionType([], self.types['Matrix']),
            'determinant': FunctionType([], self.types['float']),
            'eigenvalues': FunctionType([], self.types['Matrix'])
        }
        self.types['Matrix'] = matrix_type
        
        # Type Graph
        graph_type = Type('Graph', TypeCategory.COMPOSITE)
        graph_type.methods = {
            'nodes': FunctionType([], self.types['int']),
            'edges': FunctionType([], self.types['int']),
            'adjacency_matrix': FunctionType([], self.types['Matrix']),
            'degree_distribution': FunctionType([], self.types['Matrix'])
        }
        self.types['Graph'] = graph_type
        
        # Type Network (spécial pour les réseaux épidémiologiques)
        network_type = Type('Network', TypeCategory.NETWORK)
        network_type.attributes = {
            'nodes': self.types['int'],
            'edges': self.types['int'],
            'adjacency_matrix': self.types['Matrix'],
            'degree_distribution': self.types['Matrix']
        }
        network_type.methods = {
            'R0': FunctionType([], self.types['float']),
            'clustering_coefficient': FunctionType([], self.types['float']),
            'average_path_length': FunctionType([], self.types['float'])
        }
        self.types['Network'] = network_type
        
        # Type Model (modèles épidémiologiques)
        model_type = Type('Model', TypeCategory.MODEL)
        model_type.attributes = {
            'parameters': self.types['Matrix'],
            'states': self.types['Matrix'],
            'initial_conditions': self.types['Matrix']
        }
        model_type.methods = {
            'simulate': FunctionType([self.types['int']], self.types['Matrix']),
            'equilibrium': FunctionType([], self.types['Matrix']),
            'jacobian': FunctionType([], self.types['Matrix']),
            'sensitivity': FunctionType([self.types['string']], self.types['Matrix'])
        }
        self.types['Model'] = model_type
        
        # Type Data
        data_type = Type('Data', TypeCategory.DATA)
        data_type.methods = {
            'load': FunctionType([self.types['string']], self.types['Data']),
            'save': FunctionType([self.types['string']], self.types['bool']),
            'filter': FunctionType([self.types['string']], self.types['Data']),
            'aggregate': FunctionType([self.types['string']], self.types['Matrix'])
        }
        self.types['Data'] = data_type
    
    def get_type(self, name: str) -> Optional[Type]:
        """Obtenir un type par son nom"""
        return self.types.get(name)
    
    def is_subtype(self, subtype: Type, supertype: Type) -> bool:
        """Vérifier si un type est sous-type d'un autre"""
        if subtype.name == supertype.name:
            return True
        
        # Pour l'instant, pas d'héritage de types
        return False
    
    def unify(self, type1: Type, type2: Type) -> Optional[Type]:
        """Unifier deux types"""
        if type1.name == type2.name:
            return type1
        
        # Conversion implicite int -> float
        if type1.name == 'int' and type2.name == 'float':
            return type2
        if type1.name == 'float' and type2.name == 'int':
            return type1
        
        return None

class TypeChecker:
    """Vérificateur de types pour EpiNetLang"""
    
    def __init__(self):
        self.type_system = TypeSystem()
        self.errors = []
        self.symbol_table = {}  # Table des symboles pour les types
    
    def check_program(self, ast):
        """Vérifier les types d'un programme"""
        # Stub pour l'instant
        return self.errors