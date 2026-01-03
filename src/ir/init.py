"""
Représentation Intermédiaire (IR) pour EpiNetLang
"""

from .ir_builder import IRBuilder, IRContext
from .passes import IRPass, OptimizationPass

__all__ = [
    'IRBuilder', 'IRContext',
    'IRPass', 'OptimizationPass'
]