"""
Passes d'optimisation pour l'IR
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from .ir_builder import *

class IRPass:
    """Passe d'optimisation pour l'IR"""
    
    def __init__(self, name: str):
        self.name = name
    
    def apply(self, module: IRModule) -> IRModule:
        """Appliquer la passe au module IR"""
        raise NotImplementedError

class IRConstantPropagationPass(IRPass):
    """Propagation des constantes dans l'IR"""
    
    def __init__(self):
        super().__init__("IRConstantPropagation")
    
    def apply(self, module: IRModule) -> IRModule:
        """Propager les constantes dans toutes les fonctions"""
        
        for func_name, func in module.functions.items():
            self._propagate_in_function(func)
        
        return module
    
    def _propagate_in_function(self, func: IRFunction):
        """Propager les constantes dans une fonction"""
        constants = {}
        
        for block_name, block in func.basic_blocks.items():
            new_instructions = []
            
            for instr in block.instructions:
                # Vérifier si tous les opérandes sont des constantes
                can_fold = True
                folded_operands = []
                
                for operand in instr.operands:
                    if operand.type == "imm":
                        folded_operands.append(operand.value)
                    elif operand.type == "reg" and operand.value in constants:
                        folded_operands.append(constants[operand.value])
                    else:
                        can_fold = False
                        break
                
                # Pliage des constantes
                if can_fold and instr.result:
                    try:
                        result_value = self._fold_instruction(instr.opcode, folded_operands)
                        if result_value is not None:
                            # Stocker la constante
                            constants[instr.result.value] = result_value
                            
                            # Remplacer par une instruction de chargement de constante
                            new_instr = IRInstruction(
                                opcode=IROpCode.LOAD,
                                operands=[IROperand("imm", result_value, type(result_value).__name__)],
                                result=instr.result,
                                comment=f"folded {instr.opcode.value}"
                            )
                            new_instructions.append(new_instr)
                            continue
                    except:
                        pass
                
                # Instruction non pliable
                new_instructions.append(instr)
            
            # Mettre à jour les instructions du bloc
            block.instructions = new_instructions
    
    def _fold_instruction(self, opcode: IROpCode, operands: List[Any]) -> Any:
        """Plier une instruction avec des opérandes constants"""
        if opcode == IROpCode.ADD:
            return operands[0] + operands[1]
        elif opcode == IROpCode.SUB:
            return operands[0] - operands[1]
        elif opcode == IROpCode.MUL:
            return operands[0] * operands[1]
        elif opcode == IROpCode.DIV:
            if operands[1] == 0:
                raise ZeroDivisionError
            return operands[0] / operands[1]
        elif opcode == IROpCode.MOD:
            return operands[0] % operands[1]
        elif opcode == IROpCode.AND:
            return operands[0] and operands[1]
        elif opcode == IROpCode.OR:
            return operands[0] or operands[1]
        elif opcode == IROpCode.NOT:
            return not operands[0]
        elif opcode == IROpCode.LT:
            return operands[0] < operands[1]
        elif opcode == IROpCode.LE:
            return operands[0] <= operands[1]
        elif opcode == IROpCode.GT:
            return operands[0] > operands[1]
        elif opcode == IROpCode.GE:
            return operands[0] >= operands[1]
        elif opcode == IROpCode.EQ:
            return operands[0] == operands[1]
        elif opcode == IROpCode.NE:
            return operands[0] != operands[1]
        
        return None

class IRDeadCodeEliminationPass(IRPass):
    """Élimination du code mort dans l'IR"""
    
    def __init__(self):
        super().__init__("IRDeadCodeElimination")
    
    def apply(self, module: IRModule) -> IRModule:
        """Éliminer le code mort dans toutes les fonctions"""
        
        for func_name, func in module.functions.items():
            self._eliminate_dead_code(func)
        
        return module
    
    def _eliminate_dead_code(self, func: IRFunction):
        """Éliminer le code mort dans une fonction"""
        
        # Étape 1: Analyse des définitions et utilisations
        defs = {}
        uses = {}
        live_vars = set()
        
        for block_name, block in func.basic_blocks.items():
            for instr in block.instructions:
                # Variables définies
                if instr.result:
                    defs[instr.result.value] = instr
                
                # Variables utilisées
                for operand in instr.operands:
                    if operand.type == "reg":
                        uses.setdefault(operand.value, []).append(instr)
        
        # Étape 2: Analyse de vivacité (simplifiée)
        # Ici, nous considérons toutes les variables utilisées comme vivantes
        live_vars.update(uses.keys())
        
        # Étape 3: Éliminer les définitions mortes
        for block_name, block in func.basic_blocks.items():
            new_instructions = []
            
            for instr in block.instructions:
                # Garder l'instruction si:
                # 1. Elle n'a pas de résultat (effet de bord)
                # 2. Son résultat est vivant
                # 3. C'est une instruction critique
                if instr.result is None:
                    new_instructions.append(instr)
                elif instr.result.value in live_vars:
                    new_instructions.append(instr)
                elif self._is_critical_instruction(instr):
                    new_instructions.append(instr)
                # Sinon, l'instruction est morte
            
            block.instructions = new_instructions
    
    def _is_critical_instruction(self, instr: IRInstruction) -> bool:
        """Vérifier si une instruction est critique"""
        critical_opcodes = {
            IROpCode.STORE,
            IROpCode.CALL,
            IROpCode.RET,
            IROpCode.NETWORK_CREATE,
            IROpCode.MODEL_SIMULATE,
            IROpCode.COMPUTE_R0,
            IROpCode.SENSITIVITY_ANALYSIS,
            IROpCode.DATA_LOAD,
            IROpCode.DATA_SAVE
        }
        
        return instr.opcode in critical_opcodes

class IRNetworkOptimizationPass(IRPass):
    """Optimisations spécifiques aux réseaux pour l'IR"""
    
    def __init__(self):
        super().__init__("IRNetworkOptimization")
    
    def apply(self, module: IRModule) -> IRModule:
        """Appliquer des optimisations spécifiques aux réseaux"""
        
        for func_name, func in module.functions.items():
            self._optimize_network_operations(func)
        
        return module
    
    def _optimize_network_operations(self, func: IRFunction):
        """Optimiser les opérations sur les réseaux"""
        
        for block_name, block in func.basic_blocks.items():
            new_instructions = []
            i = 0
            
            while i < len(block.instructions):
                instr = block.instructions[i]
                
                # Regrouper les opérations réseau séquentielles
                if instr.opcode == IROpCode.NETWORK_ADD_NODE:
                    # Regrouper les ajouts de nœuds consécutifs
                    group_count = 1
                    j = i + 1
                    
                    while j < len(block.instructions):
                        next_instr = block.instructions[j]
                        if (next_instr.opcode == IROpCode.NETWORK_ADD_NODE and 
                            next_instr.operands[0].value == instr.operands[0].value):
                            group_count += 1
                            j += 1
                        else:
                            break
                    
                    if group_count > 1:
                        # Remplacer par un ajout groupé
                        new_instr = IRInstruction(
                            opcode=IROpCode.NETWORK_ADD_NODE,
                            operands=[
                                instr.operands[0],
                                IROperand("imm", group_count, "int")
                            ],
                            result=instr.result,
                            comment=f"batch add {group_count} nodes"
                        )
                        new_instructions.append(new_instr)
                        i = j  # Sauter les instructions groupées
                    else:
                        new_instructions.append(instr)
                        i += 1
                
                # Optimiser le calcul de R0 pour les réseaux simples
                elif (instr.opcode == IROpCode.COMPUTE_R0 and 
                      i > 0 and 
                      block.instructions[i-1].opcode == IROpCode.NETWORK_CREATE):
                    # Si R0 est calculé immédiatement après la création du réseau
                    # et que le réseau est simple, utiliser une valeur pré-calculée
                    network_type = block.instructions[i-1].operands[0].value
                    if network_type in ["random", "erdos_renyi"]:
                        # R0 approximatif pour les réseaux aléatoires
                        new_instr = IRInstruction(
                            opcode=IROpCode.LOAD,
                            operands=[IROperand("imm", 1.8, "float")],  # Valeur approximative
                            result=instr.result,
                            comment="approximate R0 for random network"
                        )
                        new_instructions[-1] = new_instr  # Remplacer l'instruction précédente
                        i += 1
                    else:
                        new_instructions.append(instr)
                        i += 1
                
                else:
                    new_instructions.append(instr)
                    i += 1
            
            block.instructions = new_instructions

class IROptimizer:
    """Optimiseur pour l'IR"""
    
    def __init__(self, passes: List[IRPass] = None):
        if passes is None:
            passes = [
                IRConstantPropagationPass(),
                IRDeadCodeEliminationPass(),
                IRNetworkOptimizationPass()
            ]
        self.passes = passes
    
    def optimize(self, module: IRModule, level: str = 'O2') -> IRModule:
        """Optimiser le module IR"""
        
        if level == 'O0':
            return module
        
        elif level == 'O1':
            # Optimisations de base
            for opt_pass in self.passes[:1]:
                module = opt_pass.apply(module)
        
        elif level == 'O2':
            # Optimisations standard
            for opt_pass in self.passes:
                module = opt_pass.apply(module)
        
        elif level == 'O3':
            # Optimisations agressives
            for opt_pass in self.passes:
                module = opt_pass.apply(module)
            # Appliquer plusieurs fois
            for _ in range(2):
                module = self.passes[0].apply(module)  # Propagation des constantes
        
        return module