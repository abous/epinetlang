"""
Visiteur AST pour EpiNetLang
"""

from abc import ABC, abstractmethod
from typing import Any
from .nodes import *

class ASTVisitor(ABC):
    """Visiteur abstrait pour le parcours d'AST"""
    
    @abstractmethod
    def visit_program(self, node: Program) -> Any:
        pass
    
    @abstractmethod
    def visit_import_decl(self, node: ImportDecl) -> Any:
        pass
    
    @abstractmethod
    def visit_network_decl(self, node: NetworkDecl) -> Any:
        pass
    
    @abstractmethod
    def visit_model_decl(self, node: ModelDecl) -> Any:
        pass
    
    @abstractmethod
    def visit_analysis_decl(self, node: AnalysisDecl) -> Any:
        pass
    
    @abstractmethod
    def visit_data_decl(self, node: DataDecl) -> Any:
        pass
    
    @abstractmethod
    def visit_parameter(self, node: Parameter) -> Any:
        pass
    
    @abstractmethod
    def visit_type(self, node: Type) -> Any:
        pass
    
    @abstractmethod
    def visit_block(self, node: Block) -> Any:
        pass
    
    @abstractmethod
    def visit_var_decl(self, node: VarDecl) -> Any:
        pass
    
    @abstractmethod
    def visit_assign_stmt(self, node: AssignStmt) -> Any:
        pass
    
    @abstractmethod
    def visit_if_stmt(self, node: IfStmt) -> Any:
        pass
    
    @abstractmethod
    def visit_for_stmt(self, node: ForStmt) -> Any:
        pass
    
    @abstractmethod
    def visit_while_stmt(self, node: WhileStmt) -> Any:
        pass
    
    @abstractmethod
    def visit_expr_stmt(self, node: ExprStmt) -> Any:
        pass
    
    @abstractmethod
    def visit_return_stmt(self, node: ReturnStmt) -> Any:
        pass
    
    @abstractmethod
    def visit_analysis_stmt(self, node: AnalysisStmt) -> Any:
        pass
    
    @abstractmethod
    def visit_binary_op(self, node: BinaryOp) -> Any:
        pass
    
    @abstractmethod
    def visit_unary_op(self, node: UnaryOp) -> Any:
        pass
    
    @abstractmethod
    def visit_call(self, node: Call) -> Any:
        pass
    
    @abstractmethod
    def visit_index(self, node: Index) -> Any:
        pass
    
    @abstractmethod
    def visit_member_access(self, node: MemberAccess) -> Any:
        pass
    
    @abstractmethod
    def visit_conditional(self, node: Conditional) -> Any:
        pass
    
    @abstractmethod
    def visit_literal(self, node: Literal) -> Any:
        pass
    
    @abstractmethod
    def visit_variable(self, node: Variable) -> Any:
        pass
    
    @abstractmethod
    def visit_list_literal(self, node: ListLiteral) -> Any:
        pass
    
    @abstractmethod
    def visit_dict_literal(self, node: DictLiteral) -> Any:
        pass
    
    @abstractmethod
    def visit_pair(self, node: Pair) -> Any:
        pass

class DefaultVisitor(ASTVisitor):
    """Visiteur par défaut qui visite récursivement tous les nœuds"""
    
    def visit_program(self, node: Program) -> Any:
        for decl in node.declarations:
            decl.accept(self)
    
    def visit_import_decl(self, node: ImportDecl) -> Any:
        pass
    
    def visit_network_decl(self, node: NetworkDecl) -> Any:
        for param in node.parameters:
            param.accept(self)
        node.body.accept(self)
    
    def visit_model_decl(self, node: ModelDecl) -> Any:
        for param in node.parameters:
            param.accept(self)
        node.body.accept(self)
    
    def visit_analysis_decl(self, node: AnalysisDecl) -> Any:
        for param in node.parameters:
            param.accept(self)
        node.body.accept(self)
    
    def visit_data_decl(self, node: DataDecl) -> Any:
        for param in node.parameters:
            param.accept(self)
    
    def visit_parameter(self, node: Parameter) -> Any:
        node.type.accept(self)
        if node.default_value:
            node.default_value.accept(self)
    
    def visit_type(self, node: Type) -> Any:
        pass
    
    def visit_block(self, node: Block) -> Any:
        for stmt in node.statements:
            stmt.accept(self)
    
    def visit_var_decl(self, node: VarDecl) -> Any:
        node.type.accept(self)
        if node.initializer:
            node.initializer.accept(self)
    
    def visit_assign_stmt(self, node: AssignStmt) -> Any:
        node.value.accept(self)
    
    def visit_if_stmt(self, node: IfStmt) -> Any:
        node.condition.accept(self)
        node.then_block.accept(self)
        if node.else_block:
            node.else_block.accept(self)
    
    def visit_for_stmt(self, node: ForStmt) -> Any:
        node.iterable.accept(self)
        node.body.accept(self)
    
    def visit_while_stmt(self, node: WhileStmt) -> Any:
        node.condition.accept(self)
        node.body.accept(self)
    
    def visit_expr_stmt(self, node: ExprStmt) -> Any:
        node.expression.accept(self)
    
    def visit_return_stmt(self, node: ReturnStmt) -> Any:
        node.value.accept(self)
    
    def visit_analysis_stmt(self, node: AnalysisStmt) -> Any:
        for arg in node.arguments:
            arg.accept(self)
    
    def visit_binary_op(self, node: BinaryOp) -> Any:
        node.left.accept(self)
        node.right.accept(self)
    
    def visit_unary_op(self, node: UnaryOp) -> Any:
        node.operand.accept(self)
    
    def visit_call(self, node: Call) -> Any:
        node.callee.accept(self)
        for arg in node.arguments:
            arg.accept(self)
    
    def visit_index(self, node: Index) -> Any:
        node.object.accept(self)
        node.index.accept(self)
    
    def visit_member_access(self, node: MemberAccess) -> Any:
        node.object.accept(self)
    
    def visit_conditional(self, node: Conditional) -> Any:
        node.condition.accept(self)
        node.then_expr.accept(self)
        node.else_expr.accept(self)
    
    def visit_literal(self, node: Literal) -> Any:
        pass
    
    def visit_variable(self, node: Variable) -> Any:
        pass
    
    def visit_list_literal(self, node: ListLiteral) -> Any:
        for elem in node.elements:
            elem.accept(self)
    
    def visit_dict_literal(self, node: DictLiteral) -> Any:
        for pair in node.pairs:
            pair.accept(self)
    
    def visit_pair(self, node: Pair) -> Any:
        node.key.accept(self)
        node.value.accept(self)