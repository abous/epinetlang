"""
Générateur de code Julia pour EpiNetLang
"""

from typing import Dict, List, Any
from src.ast.visitor import ASTVisitor
from src.ast.nodes import *

class JuliaGenerator(ASTVisitor):
    """Générateur de code Julia pour EpiNetLang"""
    
    def __init__(self):
        self.code_lines = []
        self.indent_level = 0
        self.current_function = None
        self.imports = set()
    
    def generate(self, ast) -> str:
        """Générer le code Julia à partir de l'AST"""
        self.code_lines = []
        self.imports.clear()
        
        # Visiter l'AST
        ast.accept(self)
        
        # Ajouter les imports au début
        imports_code = self._generate_imports()
        full_code = imports_code + "\n\n" + "\n".join(self.code_lines)
        
        return full_code
    
    def _generate_imports(self) -> str:
        """Générer les déclarations d'import"""
        import_lines = []
        
        if "LightGraphs" in self.imports:
            import_lines.append("using LightGraphs")
            import_lines.append("using GraphPlot")
        
        if "DifferentialEquations" in self.imports:
            import_lines.append("using DifferentialEquations")
        
        if "DataFrames" in self.imports:
            import_lines.append("using DataFrames")
            import_lines.append("using CSV")
        
        # Imports de base
        import_lines.append("using Statistics")
        import_lines.append("using LinearAlgebra")
        import_lines.append("using Random")
        
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
        self.imports.add("LightGraphs")
        
        # Générer la fonction de création de réseau
        params_str = ", ".join([f"{p.name}::{self._type_to_julia(p.type.name)}" 
                               for p in node.parameters])
        
        self._add_line(f"function create_network_{node.name}({params_str})")
        self._indent()
        self._add_line(f"# Créer le réseau {node.name}")
        
        # Générer le corps
        node.body.accept(self)
        
        self._dedent()
        self._add_line("end")
        self._add_line()
    
    def visit_model_decl(self, node):
        self.imports.add("DifferentialEquations")
        
        # Générer la structure du modèle
        self._add_line(f"struct {node.name}Model")
        self._indent()
        
        for param in node.parameters:
            julia_type = self._type_to_julia(param.type.name)
            self._add_line(f"{param.name}::{julia_type}")
        
        self._dedent()
        self._add_line("end")
        self._add_line()
        
        # Générer les fonctions du modèle
        self._add_line(f"function simulate(model::{node.name}Model, tspan, u0)")
        self._indent()
        
        # Générer le corps
        node.body.accept(self)
        
        self._dedent()
        self._add_line("end")
        self._add_line()
    
    def visit_analysis_decl(self, node):
        # Générer la fonction d'analyse
        params_str = ", ".join([f"{p.name}::{self._type_to_julia(p.type.name)}" 
                               for p in node.parameters])
        
        self._add_line(f"function analyze_{node.name}({params_str})")
        self._indent()
        self._add_line(f"# Analyse {node.name}")
        
        # Générer le corps
        node.body.accept(self)
        
        self._dedent()
        self._add_line("end")
        self._add_line()
    
    def visit_data_decl(self, node):
        self.imports.add("DataFrames")
        
        # Générer le chargement des données
        if node.source_type == 'CSV':
            self._generate_csv_loader(node)
        elif node.source_type == 'JSON':
            self._generate_json_loader(node)
    
    def _generate_csv_loader(self, node):
        """Générer le code pour charger un fichier CSV"""
        self._add_line(f"function load_{node.name}_data(filepath::String)")
        self._indent()
        self._add_line(f"# Charger les données {node.name} depuis un fichier CSV")
        
        # Ajouter les paramètres
        delimiter = ','
        header = 1
        
        for param in node.parameters:
            if param.name == 'delimiter':
                delimiter = param.default_value.value
            elif param.name == 'header':
                header = param.default_value.value
        
        self._add_line(f"data = CSV.read(filepath, DataFrame; delim='{delimiter}', header={header})")
        self._add_line("return data")
        self._dedent()
        self._add_line("end")
        self._add_line()
    
    def _generate_json_loader(self, node):
        """Générer le code pour charger un fichier JSON"""
        self._add_line(f"function load_{node.name}_data(filepath::String)")
        self._indent()
        self._add_line(f"# Charger les données {node.name} depuis un fichier JSON")
        self._add_line("data = JSON.parsefile(filepath)")
        self._add_line("return data")
        self._dedent()
        self._add_line("end")
        self._add_line()
    
    def visit_var_decl(self, node):
        julia_type = self._type_to_julia(node.type.name)
        var_name = node.name
        
        if node.initializer:
            init_code = self._expression_to_julia(node.initializer)
            self._add_line(f"{var_name}::{julia_type} = {init_code}")
        else:
            self._add_line(f"{var_name}::{julia_type}")
    
    def visit_assign_stmt(self, node):
        value_code = self._expression_to_julia(node.value)
        self._add_line(f"{node.target} = {value_code}")
    
    def visit_if_stmt(self, node):
        condition = self._expression_to_julia(node.condition)
        self._add_line(f"if {condition}")
        self._indent()
        node.then_block.accept(self)
        self._dedent()
        
        if node.else_block:
            self._add_line("else")
            self._indent()
            node.else_block.accept(self)
            self._dedent()
        
        self._add_line("end")
    
    def visit_for_stmt(self, node):
        iterable = self._expression_to_julia(node.iterable)
        self._add_line(f"for {node.variable} in {iterable}")
        self._indent()
        node.body.accept(self)
        self._dedent()
        self._add_line("end")
    
    def visit_while_stmt(self, node):
        condition = self._expression_to_julia(node.condition)
        self._add_line(f"while {condition}")
        self._indent()
        node.body.accept(self)
        self._dedent()
        self._add_line("end")
    
    def visit_expr_stmt(self, node):
        expr = self._expression_to_julia(node.expression)
        self._add_line(expr)
    
    def visit_return_stmt(self, node):
        value = self._expression_to_julia(node.value)
        self._add_line(f"return {value}")
    
    def visit_analysis_stmt(self, node):
        if node.analysis_type == 'R0':
            self._generate_R0_computation()
        elif node.analysis_type == 'sensitivity':
            param = self._expression_to_julia(node.arguments[0])
            self._generate_sensitivity_analysis(param)
        elif node.analysis_type == 'fit':
            data = self._expression_to_julia(node.arguments[0])
            self._generate_model_fitting(data)
        elif node.analysis_type == 'forecast':
            steps = self._expression_to_julia(node.arguments[0])
            self._generate_forecast(steps)
    
    def _generate_R0_computation(self):
        """Générer le calcul de R0 en Julia"""
        self._add_line("# Calcul du nombre de reproduction de base R0")
        self._add_line("function compute_R0(beta::Float64, gamma::Float64, network=nothing)")
        self._indent()
        self._add_line('"""')
        self._add_line("Calculer R0 pour un modèle SIR")
        self._add_line('"""')
        self._add_line("if isnothing(network)")
        self._indent()
        self._add_line("# Modèle bien mélangé")
        self._add_line("R0 = beta / gamma")
        self._dedent()
        self._add_line("else")
        self._indent()
        self._add_line("# Modèle sur réseau")
        self._add_line("degrees = degree(network)")
        self._add_line("mean_degree = mean(degrees)")
        self._add_line("mean_squared_degree = mean(degrees .^ 2)")
        self._add_line("R0 = (beta / gamma) * (mean_squared_degree / mean_degree - 1)")
        self._dedent()
        self._add_line("end")
        self._add_line("return R0")
        self._dedent()
        self._add_line("end")
        self._add_line()
    
    def _generate_sensitivity_analysis(self, parameter):
        """Générer l'analyse de sensibilité en Julia"""
        self._add_line(f"# Analyse de sensibilité pour le paramètre {parameter}")
        self._add_line(f"function sensitivity_analysis_{parameter}(model, param_range)")
        self._indent()
        self._add_line("sensitivities = []")
        self._add_line("for param_value in param_range")
        self._indent()
        self._add_line(f"model.{parameter} = param_value")
        self._add_line("result = simulate(model)")
        self._add_line("sensitivity = gradient(result)")
        self._add_line("push!(sensitivities, sensitivity)")
        self._dedent()
        self._add_line("end")
        self._add_line("return sensitivities")
        self._dedent()
        self._add_line("end")
        self._add_line()
    
    def _generate_model_fitting(self, data_var):
        """Générer l'ajustement de modèle en Julia"""
        self.imports.add("Optim")
        
        self._add_line(f"# Ajustement du modèle aux données {data_var}")
        self._add_line(f"function fit_model_to_{data_var}(model, initial_params)")
        self._indent()
        self._add_line("function error_function(params)")
        self._indent()
        self._add_line("set_parameters!(model, params)")
        self._add_line("simulated = simulate(model)")
        self._add_line(f"error = sum((simulated .- {data_var}).^2)")
        self._add_line("return error")
        self._dedent()
        self._add_line("end")
        self._add_line("result = optimize(error_function, initial_params)")
        self._add_line("return result.minimizer")
        self._dedent()
        self._add_line("end")
        self._add_line()
    
    def _generate_forecast(self, steps):
        """Générer la prévision en Julia"""
        self._add_line(f"# Prévision sur {steps} pas de temps")
        self._add_line(f"function forecast_model(model, initial_conditions, n_steps={steps})")
        self._indent()
        self._add_line("forecast = Vector{typeof(initial_conditions)}()")
        self._add_line("current_state = copy(initial_conditions)")
        self._add_line("for t in 1:n_steps")
        self._indent()
        self._add_line("next_state = step!(model, current_state)")
        self._add_line("push!(forecast, next_state)")
        self._add_line("current_state = next_state")
        self._dedent()
        self._add_line("end")
        self._add_line("return forecast")
        self._dedent()
        self._add_line("end")
        self._add_line()
    
    def _expression_to_julia(self, expr) -> str:
        """Convertir une expression AST en code Julia"""
        if isinstance(expr, BinaryOp):
            left = self._expression_to_julia(expr.left)
            right = self._expression_to_julia(expr.right)
            op = expr.operator
            
            # Mapper les opérateurs
            op_map = {
                '&&': '&&',
                '||': '||',
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
            
            julia_op = op_map.get(op, op)
            return f"({left} {julia_op} {right})"
        
        elif isinstance(expr, UnaryOp):
            operand = self._expression_to_julia(expr.operand)
            op = expr.operator
            
            if op == '!':
                return f"!({operand})"
            else:
                return f"({op}{operand})"
        
        elif isinstance(expr, Variable):
            return expr.name
        
        elif isinstance(expr, Literal):
            if expr.type == 'string':
                return f'"{expr.value}"'
            elif expr.type == 'bool':
                return 'true' if expr.value else 'false'
            else:
                return str(expr.value)
        
        elif isinstance(expr, Call):
            callee = self._expression_to_julia(expr.callee)
            args = [self._expression_to_julia(arg) for arg in expr.arguments]
            args_str = ", ".join(args)
            return f"{callee}({args_str})"
        
        elif isinstance(expr, ListLiteral):
            elements = [self._expression_to_julia(elem) for elem in expr.elements]
            elements_str = ", ".join(elements)
            return f"[{elements_str}]"
        
        elif isinstance(expr, DictLiteral):
            pairs = []
            for pair in expr.pairs:
                key = self._expression_to_julia(pair.key)
                value = self._expression_to_julia(pair.value)
                pairs.append(f"{key} => {value}")
            pairs_str = ", ".join(pairs)
            return f"Dict({pairs_str})"
        
        elif isinstance(expr, Conditional):
            cond = self._expression_to_julia(expr.condition)
            then_expr = self._expression_to_julia(expr.then_expr)
            else_expr = self._expression_to_julia(expr.else_expr)
            return f"({cond} ? {then_expr} : {else_expr})"
        
        else:
            return "nothing"
    
    def _type_to_julia(self, enl_type: str) -> str:
        """Convertir un type EpiNetLang en type Julia"""
        type_map = {
            'int': 'Int64',
            'float': 'Float64',
            'bool': 'Bool',
            'string': 'String',
            'Network': 'SimpleGraph',
            'Model': 'Any',
            'Data': 'DataFrame',
            'Matrix': 'Matrix{Float64}',
            'Graph': 'SimpleGraph'
        }
        
        return type_map.get(enl_type, 'Any')