"""
Nœuds AST pour EpiNetLang
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any, Union, Dict
from dataclasses import dataclass, field

class Node(ABC):
    """Classe de base pour tous les nœuds AST"""
    
    @abstractmethod
    def accept(self, visitor: 'ASTVisitor'):
        pass
    
    @property
    def position(self):
        return getattr(self, '_position', None)
    
    @position.setter
    def position(self, value):
        self._position = value

@dataclass
class Program(Node):
    """Programme complet"""
    declarations: List[Node]
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_program(self)

@dataclass
class ImportDecl(Node):
    """Déclaration d'importation"""
    path: str
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_import_decl(self)

@dataclass
class NetworkDecl(Node):
    """Déclaration de réseau"""
    name: str
    parameters: List['Parameter']
    body: 'Block'
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_network_decl(self)

@dataclass
class ModelDecl(Node):
    """Déclaration de modèle"""
    name: str
    parameters: List['Parameter']
    body: 'Block'
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_model_decl(self)

@dataclass
class AnalysisDecl(Node):
    """Déclaration d'analyse"""
    name: str
    parameters: List['Parameter']
    body: 'Block'
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_analysis_decl(self)

@dataclass
class DataDecl(Node):
    """Déclaration de données"""
    name: str
    source_type: str
    path: str
    parameters: List['Parameter']
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_data_decl(self)

@dataclass
class Parameter(Node):
    """Paramètre de fonction"""
    type: 'Type'
    name: str
    default_value: Optional['Expression'] = None
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_parameter(self)

@dataclass
class Type(Node):
    """Type de données"""
    name: str
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_type(self)

@dataclass
class Block(Node):
    """Bloc de code"""
    statements: List['Statement']
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_block(self)

class Statement(Node, ABC):
    """Instruction"""
    pass

@dataclass
class VarDecl(Statement):
    """Déclaration de variable"""
    type: Type
    name: str
    initializer: Optional['Expression'] = None
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_var_decl(self)

@dataclass
class AssignStmt(Statement):
    """Affectation"""
    target: str
    value: 'Expression'
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_assign_stmt(self)

@dataclass
class IfStmt(Statement):
    """Condition if"""
    condition: 'Expression'
    then_block: Block
    else_block: Optional[Block] = None
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_if_stmt(self)

@dataclass
class ForStmt(Statement):
    """Boucle for"""
    variable: str
    iterable: 'Expression'
    body: Block
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_for_stmt(self)

@dataclass
class WhileStmt(Statement):
    """Boucle while"""
    condition: 'Expression'
    body: Block
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_while_stmt(self)

@dataclass
class ExprStmt(Statement):
    """Instruction expression"""
    expression: 'Expression'
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_expr_stmt(self)

@dataclass
class ReturnStmt(Statement):
    """Instruction return"""
    value: 'Expression'
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_return_stmt(self)

@dataclass
class AnalysisStmt(Statement):
    """Instruction d'analyse"""
    analysis_type: str  # 'R0', 'sensitivity', 'fit', 'forecast'
    arguments: List['Expression']
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_analysis_stmt(self)

class Expression(Node, ABC):
    """Expression"""
    pass

@dataclass
class BinaryOp(Expression):
    """Opération binaire"""
    left: Expression
    operator: str
    right: Expression
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_binary_op(self)

@dataclass
class UnaryOp(Expression):
    """Opération unaire"""
    operator: str
    operand: Expression
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_unary_op(self)

@dataclass
class Call(Expression):
    """Appel de fonction"""
    callee: Expression
    arguments: List[Expression]
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_call(self)

@dataclass
class Index(Expression):
    """Indexation"""
    object: Expression
    index: Expression
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_index(self)

@dataclass
class MemberAccess(Expression):
    """Accès membre"""
    object: Expression
    member: str
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_member_access(self)

@dataclass
class Conditional(Expression):
    """Expression conditionnelle"""
    condition: Expression
    then_expr: Expression
    else_expr: Expression
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_conditional(self)

class Primary(Expression, ABC):
    """Expression primaire"""
    pass

@dataclass
class Literal(Primary):
    """Littéral"""
    value: Any
    type: str  # 'int', 'float', 'string', 'bool'
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_literal(self)

@dataclass
class Variable(Primary):
    """Variable"""
    name: str
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_variable(self)

@dataclass
class ListLiteral(Primary):
    """Liste littérale"""
    elements: List[Expression]
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_list_literal(self)

@dataclass
class DictLiteral(Primary):
    """Dictionnaire littéral"""
    pairs: List['Pair']
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_dict_literal(self)

@dataclass
class Pair(Node):
    """Paire clé-valeur"""
    key: Expression
    value: Expression
    
    def accept(self, visitor: 'ASTVisitor'):
        return visitor.visit_pair(self)