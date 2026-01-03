"""
Générateur de code Python pour EpiNetLang
"""

from typing import Dict, List, Any, Optional
import numpy as np
import networkx as nx
from scipy import integrate, optimize, stats
from src.ast.visitor import ASTVisitor
from src.ast.nodes import *

class PythonGenerator(ASTVisitor):
    """Générateur de code Python pour EpiNetLang"""
    
    def __init__(self):
        self.code_lines = []
        self.indent_level = 0
        self.current_function = None
        self.imports = set()
        self.include_networkx = False
        self.include_numpy = False
        self.include_scipy = False
    
    def generate(self, ast) -> str:
        """Générer le code Python à partir de l'AST"""
        self.code_lines = []
        self.imports.clear()
        self.include_networkx = False
        self.include_numpy = False
        self.include_scipy = False
        
        # Visiter l'AST
        ast.accept(self)
        
        # Ajouter les imports au début
        imports_code = self._generate_imports()
        full_code = imports_code + "\n\n" + "\n".join(self.code_lines)
        
        return full_code
    
    def _generate_imports(self) -> str:
        """Générer les déclarations d'import"""
        import_lines = []
        
        if self.include_numpy:
            import_lines.append("import numpy as np")
        
        if self.include_networkx:
            import_lines.append("import networkx as nx")
        
        if self.include_scipy:
            import_lines.append("from scipy import integrate, optimize, stats")
        
        # Imports de base
        import_lines.append("import math")
        import_lines.append("import json")
        import_lines.append("import csv")
        import_lines.append("from typing import Dict, List, Tuple, Any, Optional")
        
        return "\n".join(import_lines)
    
    def _indent(self):
        """Augmenter le niveau d'indentation"""
        self.indent_level += 1
    
    def _dedent(self):
        """Diminuer le niveau d'indentation"""
        self.indent_level -= 1
    
    def _add_line(self, line: str = ""):
        """Ajouter une ligne de code avec l'indentation appropriée"""
        indent = "    " * self.indent_level
        self.code_lines.append(indent + line)
    
    def visit_program(self, node):
        for decl in node.declarations:
            decl.accept(self)
    
    def visit_network_decl(self, node):
        self.include_networkx = True
        self.include_numpy = True
        
        # Générer la fonction de création de réseau
        params_str = ", ".join([f"{p.name}: {self._type_to_python(p.type.name)}" 
                               for p in node.parameters])
        
        self._add_line(f"def create_network_{node.name}({params_str}):")
        self._indent()
        self._add_line('"""')
        self._add_line(f"Créer le réseau {node.name}")
        self._add_line('"""')
        
        # Générer le corps
        node.body.accept(self)
        
        self._dedent()
        self._add_line()
    
    def visit_model_decl(self, node):
        self.include_numpy = True
        self.include_scipy = True
        
        # Générer la classe du modèle
        self._add_line(f"class {node.name}Model:")
        self._indent()
        self._add_line('"""')
        self._add_line(f"Modèle épidémiologique {node.name}")
        self._add_line('"""')
        self._add_line()
        
        # Générer le constructeur
        params_str = ", ".join([f"{p.name}: {self._type_to_python(p.type.name)} = None" 
                               for p in node.parameters])
        
        self._add_line(f"def __init__(self, {params_str}):")
        self._indent()
        
        for param in node.parameters:
            self._add_line(f"self.{param.name} = {param.name}")
        
        # Générer le corps
        node.body.accept(self)
        
        self._dedent()
        self._add_line()
        self._dedent()
        self._add_line()
    
    def visit_analysis_decl(self, node):
        # Générer la fonction d'analyse
        params_str = ", ".join([f"{p.name}: {self._type_to_python(p.type.name)}" 
                               for p in node.parameters])
        
        self._add_line(f"def analyze_{node.name}({params_str}):")
        self._indent()
        self._add_line('"""')
        self._add_line(f"Analyse {node.name}")
        self._add_line('"""')
        
        # Générer le corps
        node.body.accept(self)
        
        self._dedent()
        self._add_line()
    
    def visit_data_decl(self, node):
        # Générer le chargement des données
        if node.source_type == 'CSV':
            self._generate_csv_loader(node)
        elif node.source_type == 'JSON':
            self._generate_json_loader(node)
        elif node.source_type == 'SQL':
            self._generate_sql_loader(node)
    
    def _generate_csv_loader(self, node):
        """Générer le code pour charger un fichier CSV"""
        self._add_line(f"def load_{node.name}_data(filepath: str):")
        self._indent()
        self._add_line('"""')
        self._add_line(f"Charger les données {node.name} depuis un fichier CSV")
        self._add_line('"""')
        self._add_line("import pandas as pd")
        self._add_line(f"data = pd.read_csv(filepath)")
        
        # Ajouter les paramètres
        for param in node.parameters:
            if param.name == 'delimiter':
                self._add_line(f"data = pd.read_csv(filepath, delimiter='{param.default_value.value}')")
            elif param.name == 'header':
                self._add_line(f"data = pd.read_csv(filepath, header={param.default_value.value})")
        
        self._add_line("return data")
        self._dedent()
        self._add_line()
    
    def _generate_json_loader(self, node):
        """Générer le code pour charger un fichier JSON"""
        self._add_line(f"def load_{node.name}_data(filepath: str):")
        self._indent()
        self._add_line('"""')
        self._add_line(f"Charger les données {node.name} depuis un fichier JSON")
        self._add_line('"""')
        self._add_line("with open(filepath, 'r') as f:")
        self._indent()
        self._add_line("data = json.load(f)")
        self._dedent()
        self._add_line("return data")
        self._dedent()
        self._add_line()
    
    def _generate_sql_loader(self, node):
        """Générer le code pour charger depuis une base SQL"""
        self._add_line(f"def load_{node.name}_data(connection_string: str):")
        self._indent()
        self._add_line('"""')
        self._add_line(f"Charger les données {node.name} depuis une base de données SQL")
        self._add_line('"""')
        self._add_line("import sqlite3")
        self._add_line("conn = sqlite3.connect(connection_string)")
        
        for param in node.parameters:
            if param.name == 'query':
                query = param.default_value.value
                self._add_line(f"query = \"\"\"{query}\"\"\"")
                self._add_line("data = pd.read_sql_query(query, conn)")
        
        self._add_line("conn.close()")
        self._add_line("return data")
        self._dedent()
        self._add_line()
    
    def visit_var_decl(self, node):
        python_type = self._type_to_python(node.type.name)
        var_name = node.name
        
        if node.initializer:
            init_code = self._expression_to_python(node.initializer)
            self._add_line(f"{var_name}: {python_type} = {init_code}")
        else:
            self._add_line(f"{var_name}: {python_type} = None")
    
    def visit_assign_stmt(self, node):
        value_code = self._expression_to_python(node.value)
        self._add_line(f"{node.target} = {value_code}")
    
    def visit_if_stmt(self, node):
        condition = self._expression_to_python(node.condition)
        self._add_line(f"if {condition}:")
        self._indent()
        node.then_block.accept(self)
        self._dedent()
        
        if node.else_block:
            self._add_line("else:")
            self._indent()
            node.else_block.accept(self)
            self._dedent()
    
    def visit_for_stmt(self, node):
        iterable = self._expression_to_python(node.iterable)
        self._add_line(f"for {node.variable} in {iterable}:")
        self._indent()
        node.body.accept(self)
        self._dedent()
    
    def visit_while_stmt(self, node):
        condition = self._expression_to_python(node.condition)
        self._add_line(f"while {condition}:")
        self._indent()
        node.body.accept(self)
        self._dedent()
    
    def visit_expr_stmt(self, node):
        expr = self._expression_to_python(node.expression)
        self._add_line(expr)
    
    def visit_return_stmt(self, node):
        value = self._expression_to_python(node.value)
        self._add_line(f"return {value}")
    
    def visit_analysis_stmt(self, node):
        if node.analysis_type == 'R0':
            self._generate_R0_computation()
        elif node.analysis_type == 'sensitivity':
            param = self._expression_to_python(node.arguments[0])
            self._generate_sensitivity_analysis(param)
        elif node.analysis_type == 'fit':
            data = self._expression_to_python(node.arguments[0])
            self._generate_model_fitting(data)
        elif node.analysis_type == 'forecast':
            steps = self._expression_to_python(node.arguments[0])
            self._generate_forecast(steps)
    
    def _generate_R0_computation(self):
        """Générer le calcul de R0"""
        self.include_numpy = True
        self._add_line("# Calcul du nombre de reproduction de base R0")
        self._add_line("def compute_R0(beta, gamma, network):")
        self._indent()
        self._add_line('"""')
        self._add_line("Calculer R0 pour un modèle SIR sur un réseau")
        self._add_line('"""')
        self._add_line("if network is None:")
        self._indent()
        self._add_line("# Modèle bien mélangé")
        self._add_line("R0 = beta / gamma")
        self._dedent()
        self._add_line("else:")
        self._indent()
        self._add_line("# Modèle sur réseau")
        self._add_line("degrees = [d for _, d in network.degree()]")
        self._add_line("mean_degree = np.mean(degrees)")
        self._add_line("mean_squared_degree = np.mean([d**2 for d in degrees])")
        self._add_line("R0 = (beta / gamma) * (mean_squared_degree / mean_degree - 1)")
        self._dedent()
        self._add_line("return R0")
        self._dedent()
    
    def _generate_sensitivity_analysis(self, parameter):
        """Générer l'analyse de sensibilité"""
        self.include_numpy = True
        self._add_line(f"# Analyse de sensibilité pour le paramètre {parameter}")
        self._add_line(f"def sensitivity_analysis_{parameter}(model, param_range):")
        self._indent()
        self._add_line('"""')
        self._add_line(f"Analyser la sensibilité du modèle au paramètre {parameter}")
        self._add_line('"""')
        self._add_line("sensitivities = []")
        self._add_line("for param_value in param_range:")
        self._indent()
        self._add_line(f"model.{parameter} = param_value")
        self._add_line("result = model.simulate()")
        self._add_line("sensitivity = np.gradient(result)")
        self._add_line("sensitivities.append(sensitivity)")
        self._dedent()
        self._add_line("return np.array(sensitivities)")
        self._dedent()
    
    def _generate_model_fitting(self, data_var):
        """Générer l'ajustement de modèle"""
        self.include_scipy = True
        self._add_line(f"# Ajustement du modèle aux données {data_var}")
        self._add_line(f"def fit_model_to_{data_var}(model, initial_params):")
        self._indent()
        self._add_line('"""')
        self._add_line(f"Ajuster les paramètres du modèle aux données {data_var}")
        self._add_line('"""')
        self._add_line("def error_function(params):")
        self._indent()
        self._add_line("model.set_parameters(params)")
        self._add_line("simulated = model.simulate()")
        self._add_line(f"error = np.sum((simulated - {data_var})**2)")
        self._add_line("return error")
        self._dedent()
        self._add_line("result = optimize.minimize(error_function, initial_params)")
        self._add_line("return result.x")
        self._dedent()
    
    def _generate_forecast(self, steps):
        """Générer la prévision"""
        self.include_numpy = True
        self._add_line(f"# Prévision sur {steps} pas de temps")
        self._add_line(f"def forecast_model(model, initial_conditions, n_steps={steps}):")
        self._indent()
        self._add_line('"""')
        self._add_line(f"Prévoir l'évolution du modèle sur {steps} pas de temps")
        self._add_line('"""')
        self._add_line("forecast = []")
        self._add_line("current_state = initial_conditions.copy()")
        self._add_line("for t in range(n_steps):")
        self._indent()
        self._add_line("next_state = model.step(current_state)")
        self._add_line("forecast.append(next_state)")
        self._add_line("current_state = next_state")
        self._dedent()
        self._add_line("return np.array(forecast)")
        self._dedent()
    
    def _expression_to_python(self, expr) -> str:
        """Convertir une expression AST en code Python"""
        if isinstance(expr, BinaryOp):
            left = self._expression_to_python(expr.left)
            right = self._expression_to_python(expr.right)
            op = expr.operator
            
            # Mapper les opérateurs
            op_map = {
                '&&': 'and',
                '||': 'or',
                '!=': '!=',
                '==': '==',
                '<': '<',
                '<=': '<=',
                '>': '>',
                '>=': '>=',
                '+': '+',
                '-': '-',
                '*': '*',
                '/': '/',
                '%': '%'
            }
            
            python_op = op_map.get(op, op)
            return f"({left} {python_op} {right})"
        
        elif isinstance(expr, UnaryOp):
            operand = self._expression_to_python(expr.operand)
            op = expr.operator
            
            if op == '!':
                return f"(not {operand})"
            else:
                return f"({op}{operand})"
        
        elif isinstance(expr, Variable):
            return expr.name
        
        elif isinstance(expr, Literal):
            if expr.type == 'string':
                return f'"{expr.value}"'
            elif expr.type == 'bool':
                return 'True' if expr.value else 'False'
            else:
                return str(expr.value)
        
        elif isinstance(expr, Call):
            callee = self._expression_to_python(expr.callee)
            args = [self._expression_to_python(arg) for arg in expr.arguments]
            args_str = ", ".join(args)
            return f"{callee}({args_str})"
        
        elif isinstance(expr, ListLiteral):
            elements = [self._expression_to_python(elem) for elem in expr.elements]
            elements_str = ", ".join(elements)
            return f"[{elements_str}]"
        
        elif isinstance(expr, DictLiteral):
            pairs = []
            for pair in expr.pairs:
                key = self._expression_to_python(pair.key)
                value = self._expression_to_python(pair.value)
                pairs.append(f"{key}: {value}")
            pairs_str = ", ".join(pairs)
            return f"{{{pairs_str}}}"
        
        elif isinstance(expr, Conditional):
            cond = self._expression_to_python(expr.condition)
            then_expr = self._expression_to_python(expr.then_expr)
            else_expr = self._expression_to_python(expr.else_expr)
            return f"({then_expr} if {cond} else {else_expr})"
        
        else:
            return "None"
    
    def _type_to_python(self, enl_type: str) -> str:
        """Convertir un type EpiNetLang en type Python"""
        type_map = {
            'int': 'int',
            'float': 'float',
            'bool': 'bool',
            'string': 'str',
            'Network': 'nx.Graph',
            'Model': 'Any',
            'Data': 'pd.DataFrame',
            'Matrix': 'np.ndarray',
            'Graph': 'nx.Graph'
        }
        
        return type_map.get(enl_type, 'Any')