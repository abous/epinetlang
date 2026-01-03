"""
Table des symboles pour EpiNetLang
"""

from typing import Dict, Optional, List, Any
from enum import Enum
from dataclasses import dataclass

class SymbolKind(Enum):
    """Types de symboles"""
    VARIABLE = "variable"
    FUNCTION = "function"
    NETWORK = "network"
    MODEL = "model"
    ANALYSIS = "analysis"
    DATA = "data"
    TYPE = "type"
    PARAMETER = "parameter"

@dataclass
class Symbol:
    """Symbole dans la table des symboles"""
    name: str
    kind: SymbolKind
    type: str  # Type du symbole
    scope_level: int
    value: Any = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class Scope:
    """Portée (scope) dans la table des symboles"""
    
    def __init__(self, level: int, parent: Optional['Scope'] = None):
        self.level = level
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}
    
    def define(self, symbol: Symbol) -> bool:
        """Définir un symbole dans la portée"""
        if symbol.name in self.symbols:
            return False
        self.symbols[symbol.name] = symbol
        return True
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Rechercher un symbole dans la portée"""
        return self.symbols.get(name)
    
    def lookup_all(self, name: str) -> Optional[Symbol]:
        """Rechercher un symbole dans la portée et les portées parentes"""
        symbol = self.lookup(name)
        if symbol is not None:
            return symbol
        if self.parent is not None:
            return self.parent.lookup_all(name)
        return None

class SymbolTable:
    """Table des symboles hiérarchique"""
    
    def __init__(self):
        self.current_scope = Scope(0)
        self.scope_stack = [self.current_scope]
    
    def enter_scope(self):
        """Entrer dans une nouvelle portée"""
        new_scope = Scope(self.current_scope.level + 1, self.current_scope)
        self.scope_stack.append(new_scope)
        self.current_scope = new_scope
    
    def exit_scope(self):
        """Sortir de la portée courante"""
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
            self.current_scope = self.scope_stack[-1]
    
    def define(self, name: str, kind: SymbolKind, type: str, **kwargs) -> bool:
        """Définir un nouveau symbole"""
        symbol = Symbol(
            name=name,
            kind=kind,
            type=type,
            scope_level=self.current_scope.level,
            **kwargs
        )
        return self.current_scope.define(symbol)
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Rechercher un symbole dans la portée courante"""
        return self.current_scope.lookup(name)
    
    def lookup_global(self, name: str) -> Optional[Symbol]:
        """Rechercher un symbole globalement"""
        return self.current_scope.lookup_all(name)
    
    def get_current_scope_level(self) -> int:
        """Obtenir le niveau de portée courant"""
        return self.current_scope.level
    
    def get_all_symbols(self) -> List[Symbol]:
        """Obtenir tous les symboles de toutes les portées"""
        symbols = []
        for scope in self.scope_stack:
            symbols.extend(scope.symbols.values())
        return symbols
    
    def clear(self):
        """Effacer toute la table des symboles"""
        self.current_scope = Scope(0)
        self.scope_stack = [self.current_scope]

class SemanticAnalyzer:
    """Analyseur sémantique utilisant la table des symboles"""
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.warnings = []
    
    def analyze(self, ast):
        """Analyser sémantiquement l'AST"""
        from src.ast.visitor import ASTVisitor
        
        class SemanticVisitor(ASTVisitor):
            def __init__(self, analyzer):
                self.analyzer = analyzer
            
            def visit_program(self, node):
                # Définir les types de base
                self.analyzer.symbol_table.define("int", SymbolKind.TYPE, "type")
                self.analyzer.symbol_table.define("float", SymbolKind.TYPE, "type")
                self.analyzer.symbol_table.define("bool", SymbolKind.TYPE, "type")
                self.analyzer.symbol_table.define("string", SymbolKind.TYPE, "type")
                self.analyzer.symbol_table.define("Network", SymbolKind.TYPE, "type")
                self.analyzer.symbol_table.define("Model", SymbolKind.TYPE, "type")
                self.analyzer.symbol_table.define("Data", SymbolKind.TYPE, "type")
                self.analyzer.symbol_table.define("Matrix", SymbolKind.TYPE, "type")
                self.analyzer.symbol_table.define("Graph", SymbolKind.TYPE, "type")
                
                for decl in node.declarations:
                    decl.accept(self)
            
            def visit_network_decl(self, node):
                # Définir le réseau
                self.analyzer.symbol_table.define(
                    node.name,
                    SymbolKind.NETWORK,
                    "Network",
                    metadata={"parameters": node.parameters}
                )
                
                # Entrer dans la portée du réseau
                self.analyzer.symbol_table.enter_scope()
                
                # Définir les paramètres
                for param in node.parameters:
                    self.analyzer.symbol_table.define(
                        param.name,
                        SymbolKind.PARAMETER,
                        param.type.name
                    )
                
                # Analyser le corps
                node.body.accept(self)
                
                # Sortir de la portée
                self.analyzer.symbol_table.exit_scope()
            
            def visit_model_decl(self, node):
                # Définir le modèle
                self.analyzer.symbol_table.define(
                    node.name,
                    SymbolKind.MODEL,
                    "Model",
                    metadata={"parameters": node.parameters}
                )
                
                # Entrer dans la portée du modèle
                self.analyzer.symbol_table.enter_scope()
                
                # Définir les paramètres
                for param in node.parameters:
                    self.analyzer.symbol_table.define(
                        param.name,
                        SymbolKind.PARAMETER,
                        param.type.name
                    )
                
                # Analyser le corps
                node.body.accept(self)
                
                # Sortir de la portée
                self.analyzer.symbol_table.exit_scope()
            
            def visit_var_decl(self, node):
                # Vérifier si le type existe
                type_symbol = self.analyzer.symbol_table.lookup_global(node.type.name)
                if type_symbol is None:
                    self.analyzer.errors.append(f"Type inconnu: {node.type.name}")
                
                # Définir la variable
                success = self.analyzer.symbol_table.define(
                    node.name,
                    SymbolKind.VARIABLE,
                    node.type.name
                )
                
                if not success:
                    self.analyzer.errors.append(f"Variable déjà définie: {node.name}")
                
                # Analyser l'initialisateur
                if node.initializer:
                    node.initializer.accept(self)
            
            def visit_variable(self, node):
                # Vérifier si la variable existe
                symbol = self.analyzer.symbol_table.lookup_global(node.name)
                if symbol is None:
                    self.analyzer.errors.append(f"Variable non définie: {node.name}")
            
            # Implémenter les autres méthodes visit...
            
        visitor = SemanticVisitor(self)
        ast.accept(visitor)
        
        return self.errors, self.warnings