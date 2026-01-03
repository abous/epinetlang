"""
Module core pour EpiNetLang - Fonctionnalités principales
"""

from .symbol_table import SymbolTable, Symbol
from .type_system import TypeSystem, TypeChecker, Type
from .optimizer import Optimizer, OptimizationPass

__all__ = [
    'SymbolTable', 'Symbol',
    'TypeSystem', 'TypeChecker', 'Type',
    'Optimizer', 'OptimizationPass'
]