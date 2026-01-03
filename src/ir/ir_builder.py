"""
Constructeur de représentation intermédiaire pour EpiNetLang
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

class IROpCode(Enum):
    """Codes d'opération de l'IR"""
    # Opérations arithmétiques
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    MOD = "mod"
    NEG = "neg"
    
    # Opérations logiques
    AND = "and"
    OR = "or"
    NOT = "not"
    
    # Opérations de comparaison
    LT = "lt"
    LE = "le"
    GT = "gt"
    GE = "ge"
    EQ = "eq"
    NE = "ne"
    
    # Contrôle de flux
    JMP = "jmp"
    JMP_IF = "jmp_if"
    JMP_IF_NOT = "jmp_if_not"
    CALL = "call"
    RET = "ret"
    
    # Mémoire
    LOAD = "load"
    STORE = "store"
    ALLOC = "alloc"
    FREE = "free"
    
    # Réseaux et modèles
    NETWORK_CREATE = "network_create"
    NETWORK_ADD_NODE = "network_add_node"
    NETWORK_ADD_EDGE = "network_add_edge"
    MODEL_CREATE = "model_create"
    MODEL_SET_PARAM = "model_set_param"
    MODEL_SIMULATE = "model_simulate"
    
    # Analyse
    COMPUTE_R0 = "compute_r0"
    SENSITIVITY_ANALYSIS = "sensitivity_analysis"
    FIT_MODEL = "fit_model"
    FORECAST = "forecast"
    
    # Données
    DATA_LOAD = "data_load"
    DATA_SAVE = "data_save"
    DATA_FILTER = "data_filter"
    DATA_AGGREGATE = "data_aggregate"

@dataclass
class IROperand:
    """Opérande de l'IR"""
    type: str  # 'imm' (immédiat), 'reg' (registre), 'mem' (mémoire), 'label'
    value: Any
    data_type: str = None  # Type de données: 'int', 'float', 'bool', etc.

@dataclass
class IRInstruction:
    """Instruction de l'IR"""
    opcode: IROpCode
    operands: List[IROperand] = field(default_factory=list)
    result: Optional[IROperand] = None
    comment: str = ""
    
    def __str__(self):
        result_str = f"{self.result} = " if self.result else ""
        ops_str = ", ".join(str(op) for op in self.operands)
        comment_str = f" ; {self.comment}" if self.comment else ""
        return f"{result_str}{self.opcode.value}({ops_str}){comment_str}"

@dataclass
class IRBasicBlock:
    """Bloc de base de l'IR"""
    name: str
    instructions: List[IRInstruction] = field(default_factory=list)
    predecessors: List[str] = field(default_factory=list)
    successors: List[str] = field(default_factory=list)
    
    def add_instruction(self, instr: IRInstruction):
        """Ajouter une instruction au bloc"""
        self.instructions.append(instr)
    
    def __str__(self):
        lines = [f"BB_{self.name}:"]
        for instr in self.instructions:
            lines.append(f"  {instr}")
        return "\n".join(lines)

@dataclass
class IRFunction:
    """Fonction de l'IR"""
    name: str
    parameters: List[IROperand]
    return_type: str
    basic_blocks: Dict[str, IRBasicBlock] = field(default_factory=dict)
    entry_block: str = "entry"
    exit_block: str = "exit"
    
    def get_block(self, name: str) -> IRBasicBlock:
        """Obtenir un bloc par son nom"""
        if name not in self.basic_blocks:
            self.basic_blocks[name] = IRBasicBlock(name)
        return self.basic_blocks[name]
    
    def __str__(self):
        lines = [f"func {self.name}({', '.join(str(p) for p in self.parameters)}) -> {self.return_type}:"]
        for block_name, block in self.basic_blocks.items():
            lines.append(str(block))
        return "\n".join(lines)

class IRModule:
    """Module de l'IR"""
    
    def __init__(self, name: str = "main"):
        self.name = name
        self.functions: Dict[str, IRFunction] = {}
        self.globals: Dict[str, IROperand] = {}
        self.constants: Dict[str, Any] = {}
    
    def add_function(self, func: IRFunction):
        """Ajouter une fonction au module"""
        self.functions[func.name] = func
    
    def get_function(self, name: str) -> Optional[IRFunction]:
        """Obtenir une fonction par son nom"""
        return self.functions.get(name)
    
    def add_global(self, name: str, operand: IROperand):
        """Ajouter une variable globale"""
        self.globals[name] = operand
    
    def add_constant(self, name: str, value: Any):
        """Ajouter une constante"""
        self.constants[name] = value
    
    def __str__(self):
        lines = [f"module {self.name}"]
        
        if self.constants:
            lines.append("\n; Constantes:")
            for name, value in self.constants.items():
                lines.append(f"const {name} = {value}")
        
        if self.globals:
            lines.append("\n; Variables globales:")
            for name, operand in self.globals.items():
                lines.append(f"global {name}: {operand.data_type}")
        
        lines.append("\n; Fonctions:")
        for func in self.functions.values():
            lines.append("\n" + str(func))
        
        return "\n".join(lines)

class IRBuilder:
    """Constructeur de représentation intermédiaire"""
    
    def __init__(self):
        self.module = IRModule()
        self.current_function: Optional[IRFunction] = None
        self.current_block: Optional[IRBasicBlock] = None
        self.next_reg_id = 0
        self.next_label_id = 0
        self.symbol_table: Dict[str, IROperand] = {}
    
    def new_register(self, data_type: str = "any") -> IROperand:
        """Créer un nouveau registre temporaire"""
        reg_name = f"%r{self.next_reg_id}"
        self.next_reg_id += 1
        return IROperand("reg", reg_name, data_type)
    
    def new_label(self, prefix: str = "L") -> str:
        """Créer un nouveau label"""
        label = f"{prefix}{self.next_label_id}"
        self.next_label_id += 1
        return label
    
    def build_from_ast(self, ast):
        """Construire l'IR à partir de l'AST"""
        from src.ast.visitor import ASTVisitor
        
        class IRVisitor(ASTVisitor):
            def __init__(self, builder):
                self.builder = builder
                self.value_stack = []
            
            def visit_program(self, node):
                for decl in node.declarations:
                    decl.accept(self)
            
            def visit_network_decl(self, node):
                # Créer une fonction pour le réseau
                func = IRFunction(
                    name=f"network_{node.name}",
                    parameters=[
                        IROperand("reg", f"%p{i}", param.type.name)
                        for i, param in enumerate(node.parameters)
                    ],
                    return_type="Network"
                )
                
                self.builder.current_function = func
                entry_block = func.get_block("entry")
                self.builder.current_block = entry_block
                
                # Construire le corps
                node.body.accept(self)
                
                # Ajouter la fonction au module
                self.builder.module.add_function(func)
                
                # Réinitialiser
                self.builder.current_function = None
                self.builder.current_block = None
            
            def visit_model_decl(self, node):
                # Créer une fonction pour le modèle
                func = IRFunction(
                    name=f"model_{node.name}",
                    parameters=[
                        IROperand("reg", f"%p{i}", param.type.name)
                        for i, param in enumerate(node.parameters)
                    ],
                    return_type="Model"
                )
                
                self.builder.current_function = func
                entry_block = func.get_block("entry")
                self.builder.current_block = entry_block
                
                # Construire le corps
                node.body.accept(self)
                
                # Ajouter la fonction au module
                self.builder.module.add_function(func)
                
                # Réinitialiser
                self.builder.current_function = None
                self.builder.current_block = None
            
            def visit_var_decl(self, node):
                # Allouer de l'espace pour la variable
                if self.builder.current_function:
                    # Variable locale
                    reg = self.builder.new_register(node.type.name)
                    self.builder.symbol_table[node.name] = reg
                    
                    # Initialiser si nécessaire
                    if node.initializer:
                        node.initializer.accept(self)
                        init_value = self.value_stack.pop()
                        
                        # Créer une instruction de stockage
                        instr = IRInstruction(
                            opcode=IROpCode.STORE,
                            operands=[init_value],
                            result=reg,
                            comment=f"store {node.name}"
                        )
                        self.builder.current_block.add_instruction(instr)
                else:
                    # Variable globale
                    operand = IROperand("mem", f"@{node.name}", node.type.name)
                    self.builder.module.add_global(node.name, operand)
            
            def visit_binary_op(self, node):
                # Visiter les sous-expressions
                node.left.accept(self)
                left_val = self.value_stack.pop()
                
                node.right.accept(self)
                right_val = self.value_stack.pop()
                
                # Déterminer l'opcode
                opcode_map = {
                    '+': IROpCode.ADD,
                    '-': IROpCode.SUB,
                    '*': IROpCode.MUL,
                    '/': IROpCode.DIV,
                    '%': IROpCode.MOD,
                    '&&': IROpCode.AND,
                    '||': IROpCode.OR,
                    '<': IOpCode.LT,
                    '<=': IROpCode.LE,
                    '>': IROpCode.GT,
                    '>=': IROpCode.GE,
                    '==': IROpCode.EQ,
                    '!=': IROpCode.NE
                }
                
                if node.operator in opcode_map:
                    opcode = opcode_map[node.operator]
                    result_reg = self.builder.new_register(left_val.data_type)
                    
                    instr = IRInstruction(
                        opcode=opcode,
                        operands=[left_val, right_val],
                        result=result_reg,
                        comment=f"{node.operator}"
                    )
                    
                    if self.builder.current_block:
                        self.builder.current_block.add_instruction(instr)
                    
                    self.value_stack.append(result_reg)
            
            def visit_literal(self, node):
                # Créer un opérande immédiat
                operand = IROperand("imm", node.value, node.type)
                self.value_stack.append(operand)
            
            def visit_variable(self, node):
                # Rechercher la variable dans la table des symboles
                if node.name in self.builder.symbol_table:
                    operand = self.builder.symbol_table[node.name]
                elif node.name in self.builder.module.globals:
                    operand = self.builder.module.globals[node.name]
                else:
                    # Variable non trouvée, créer un nouveau registre
                    operand = self.builder.new_register("unknown")
                
                # Charger la valeur si nécessaire
                if operand.type == "mem":
                    reg = self.builder.new_register(operand.data_type)
                    instr = IRInstruction(
                        opcode=IROpCode.LOAD,
                        operands=[operand],
                        result=reg,
                        comment=f"load {node.name}"
                    )
                    self.builder.current_block.add_instruction(instr)
                    self.value_stack.append(reg)
                else:
                    self.value_stack.append(operand)
            
            # Implémenter les autres méthodes visit...
        
        visitor = IRVisitor(self)
        ast.accept(visitor)
        
        return self.module
    
    def build_network_creation(self, network_type: str, params: Dict[str, Any]) -> IROperand:
        """Construire l'IR pour la création d'un réseau"""
        result_reg = self.new_register("Network")
        
        # Convertir les paramètres en opérandes
        param_operands = []
        for key, value in params.items():
            if isinstance(value, (int, float)):
                param_operands.append(IROperand("imm", value, type(value).__name__))
            elif isinstance(value, str):
                param_operands.append(IROperand("imm", value, "string"))
        
        instr = IRInstruction(
            opcode=IROpCode.NETWORK_CREATE,
            operands=param_operands,
            result=result_reg,
            comment=f"create {network_type} network"
        )
        
        if self.current_block:
            self.current_block.add_instruction(instr)
        
        return result_reg
    
    def build_model_simulation(self, model: IROperand, steps: int) -> IROperand:
        """Construire l'IR pour la simulation d'un modèle"""
        result_reg = self.new_register("Matrix")
        
        steps_operand = IROperand("imm", steps, "int")
        
        instr = IRInstruction(
            opcode=IROpCode.MODEL_SIMULATE,
            operands=[model, steps_operand],
            result=result_reg,
            comment="simulate model"
        )
        
        if self.current_block:
            self.current_block.add_instruction(instr)
        
        return result_reg
    
    def build_R0_computation(self, model: IROperand) -> IROperand:
        """Construire l'IR pour le calcul de R0"""
        result_reg = self.new_register("float")
        
        instr = IRInstruction(
            opcode=IROpCode.COMPUTE_R0,
            operands=[model],
            result=result_reg,
            comment="compute R0"
        )
        
        if self.current_block:
            self.current_block.add_instruction(instr)
        
        return result_reg
    
    def build_sensitivity_analysis(self, model: IROperand, parameter: str) -> IROperand:
        """Construire l'IR pour l'analyse de sensibilité"""
        result_reg = self.new_register("Matrix")
        
        param_operand = IROperand("imm", parameter, "string")
        
        instr = IRInstruction(
            opcode=IROpCode.SENSITIVITY_ANALYSIS,
            operands=[model, param_operand],
            result=result_reg,
            comment=f"sensitivity analysis for {parameter}"
        )
        
        if self.current_block:
            self.current_block.add_instruction(instr)
        
        return result_reg

class IRContext:
    """Contexte d'exécution de l'IR"""
    
    def __init__(self):
        self.registers: Dict[str, Any] = {}
        self.memory: Dict[str, Any] = {}
        self.functions: Dict[str, Any] = {}
        self.current_module: Optional[IRModule] = None
    
    def execute_module(self, module: IRModule):
        """Exécuter un module IR"""
        self.current_module = module
        
        # Initialiser les constantes
        for name, value in module.constants.items():
            self.memory[name] = value
        
        # Exécuter les fonctions principales
        for func_name, func in module.functions.items():
            if func_name.startswith("network_") or func_name.startswith("model_"):
                self._execute_function(func)
    
    def _execute_function(self, func: IRFunction):
        """Exécuter une fonction IR"""
        # Pour l'instant, simplement stocker la fonction
        self.functions[func.name] = func
    
    def evaluate_instruction(self, instr: IRInstruction) -> Any:
        """Évaluer une instruction IR"""
        if instr.opcode == IROpCode.ADD:
            left = self._get_operand_value(instr.operands[0])
            right = self._get_operand_value(instr.operands[1])
            result = left + right
            self._set_result_value(instr.result, result)
            return result
        
        elif instr.opcode == IROpCode.SUB:
            left = self._get_operand_value(instr.operands[0])
            right = self._get_operand_value(instr.operands[1])
            result = left - right
            self._set_result_value(instr.result, result)
            return result
        
        elif instr.opcode == IOpCode.MUL:
            left = self._get_operand_value(instr.operands[0])
            right = self._get_operand_value(instr.operands[1])
            result = left * right
            self._set_result_value(instr.result, result)
            return result
        
        elif instr.opcode == IROpCode.DIV:
            left = self._get_operand_value(instr.operands[0])
            right = self._get_operand_value(instr.operands[1])
            if right == 0:
                raise ZeroDivisionError("Division by zero")
            result = left / right
            self._set_result_value(instr.result, result)
            return result
        
        elif instr.opcode == IROpCode.NETWORK_CREATE:
            # Créer un réseau simple
            network = {
                "type": "generic",
                "nodes": 100,  # Par défaut
                "edges": 0,
                "adjacency_matrix": None
            }
            self._set_result_value(instr.result, network)
            return network
        
        elif instr.opcode == IROpCode.COMPUTE_R0:
            # Calculer R0 simple
            model = self._get_operand_value(instr.operands[0])
            r0 = 2.5  # Valeur par défaut
            self._set_result_value(instr.result, r0)
            return r0
        
        # Implémenter les autres opcodes...
        
        return None
    
    def _get_operand_value(self, operand: IROperand) -> Any:
        """Obtenir la valeur d'un opérande"""
        if operand.type == "imm":
            return operand.value
        elif operand.type == "reg":
            return self.registers.get(operand.value)
        elif operand.type == "mem":
            return self.memory.get(operand.value)
        return None
    
    def _set_result_value(self, result: IROperand, value: Any):
        """Définir la valeur d'un résultat"""
        if result is None:
            return
        
        if result.type == "reg":
            self.registers[result.value] = value
        elif result.type == "mem":
            self.memory[result.value] = value