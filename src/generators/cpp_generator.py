"""
Générateur de code C++ pour EpiNetLang
"""

from typing import Dict, List, Any
from src.ast.visitor import ASTVisitor
from src.ast.nodes import *

class CppGenerator(ASTVisitor):
    """Générateur de code C++ pour EpiNetLang"""
    
    def __init__(self):
        self.code_lines = []
        self.header_lines = []
        self.indent_level = 0
        self.current_class = None
        self.includes = set()
    
    def generate(self, ast) -> str:
        """Générer le code C++ à partir de l'AST"""
        self.code_lines = []
        self.header_lines = []
        self.includes.clear()
        
        # Visiter l'AST
        ast.accept(self)
        
        # Générer le fichier header
        header_code = self._generate_header()
        
        # Générer le fichier source
        source_code = self._generate_source()
        
        return header_code, source_code
    
    def _generate_header(self) -> str:
        """Générer le code du fichier header (.hpp)"""
        header = []
        
        # Ajouter les guards
        header.append("#ifndef EPINETLANG_GENERATED_HPP")
        header.append("#define EPINETLANG_GENERATED_HPP")
        header.append("")
        
        # Ajouter les includes
        if "vector" in self.includes:
            header.append("#include <vector>")
        if "string" in self.includes:
            header.append("#include <string>")
        if "map" in self.includes:
            header.append("#include <map>")
        if "memory" in self.includes:
            header.append("#include <memory>")
        if "cmath" in self.includes:
            header.append("#include <cmath>")
        
        header.append("#include <iostream>")
        header.append("#include <fstream>")
        header.append("#include <sstream>")
        header.append("")
        
        # Ajouter le namespace
        header.append("namespace epinetlang {")
        header.append("")
        
        # Ajouter les lignes du header
        header.extend(self.header_lines)
        
        header.append("")
        header.append("} // namespace epinetlang")
        header.append("")
        header.append("#endif // EPINETLANG_GENERATED_HPP")
        
        return "\n".join(header)
    
    def _generate_source(self) -> str:
        """Générer le code du fichier source (.cpp)"""
        source = []
        
        # Ajouter l'inclusion du header
        source.append('#include "epinetlang_generated.hpp"')
        source.append("")
        
        # Ajouter d'autres includes spécifiques
        if "Eigen" in self.includes:
            source.append("#include <Eigen/Dense>")
            source.append("using Eigen::MatrixXd;")
            source.append("using Eigen::VectorXd;")
            source.append("")
        
        source.append("using namespace epinetlang;")
        source.append("")
        
        # Ajouter les lignes de code
        source.extend(self.code_lines)
        
        return "\n".join(source)
    
    def _indent(self):
        """Augmenter le niveau d'indentation"""
        self.indent_level += 1
    
    def _dedent(self):
        """Diminuer le niveau d'indentation"""
        self.indent_level -= 1
    
    def _add_line(self, line: str = "", to_header: bool = False):
        """Ajouter une ligne de code avec l'indentation appropriée"""
        indent = "    " * self.indent_level
        
        if to_header:
            self.header_lines.append(indent + line)
        else:
            self.code_lines.append(indent + line)
    
    def visit_program(self, node):
        for decl in node.declarations:
            decl.accept(self)
    
    def visit_network_decl(self, node):
        self.includes.add("vector")
        self.includes.add("memory")
        
        # Déclarer la classe dans le header
        self._add_line(f"class Network{node.name} {{", to_header=True)
        self._add_line("public:", to_header=True)
        self._indent()
        
        # Déclarer le constructeur
        params_str = ", ".join([f"{self._type_to_cpp(p.type.name)} {p.name}" 
                               for p in node.parameters])
        
        self._add_line(f"Network{node.name}({params_str});", to_header=True)
        self._add_line("", to_header=True)
        
        # Déclarer les méthodes
        self._add_line("int get_num_nodes() const;", to_header=True)
        self._add_line("int get_num_edges() const;", to_header=True)
        self._add_line("double compute_R0() const;", to_header=True)
        self._add_line("", to_header=True)
        
        self._dedent()
        self._add_line("private:", to_header=True)
        self._indent()
        
        # Déclarer les membres
        for param in node.parameters:
            cpp_type = self._type_to_cpp(param.type.name)
            self._add_line(f"{cpp_type} {param.name}_;", to_header=True)
        
        self._add_line("std::vector<std::vector<int>> adjacency_matrix_;", to_header=True)
        
        self._dedent()
        self._add_line("};", to_header=True)
        self._add_line("", to_header=True)
        
        # Implémenter les méthodes dans le source
        self._add_line(f"Network{node.name}::Network{node.name}({params_str})")
        self._indent()
        
        # Liste d'initialisation
        init_list = []
        for param in node.parameters:
            init_list.append(f"{param.name}_({param.name})")
        
        init_list.append("adjacency_matrix_()")
        
        if init_list:
            self._add_line(f": {', '.join(init_list)}")
        
        self._dedent()
        self._add_line("{")
        self._indent()
        
        # Générer le corps
        node.body.accept(self)
        
        self._dedent()
        self._add_line("}")
        self._add_line("")
        
        # Implémenter les autres méthodes
        self._add_line(f"int Network{node.name}::get_num_nodes() const")
        self._add_line("{")
        self._indent()
        self._add_line("return adjacency_matrix_.size();")
        self._dedent()
        self._add_line("}")
        self._add_line("")
        
        self._add_line(f"double Network{node.name}::compute_R0() const")
        self._add_line("{")
        self._indent()
        self._add_line("// Calcul simplifié de R0")
        self._add_line("double beta = 0.3;  // Paramètre de transmission")
        self._add_line("double gamma = 0.1; // Paramètre de guérison")
        self._add_line("double mean_degree = 5.0; // Degré moyen approximatif")
        self._add_line("return beta * mean_degree / gamma;")
        self._dedent()
        self._add_line("}")
        self._add_line("")
    
    def visit_model_decl(self, node):
        self.includes.add("Eigen")
        self.includes.add("vector")
        
        # Déclarer la classe dans le header
        self._add_line(f"class {node.name}Model {{", to_header=True)
        self._add_line("public:", to_header=True)
        self._indent()
        
        # Déclarer le constructeur
        params_str = ", ".join([f"{self._type_to_cpp(p.type.name)} {p.name}" 
                               for p in node.parameters])
        
        self._add_line(f"{node.name}Model({params_str});", to_header=True)
        self._add_line("", to_header=True)
        
        # Déclarer les méthodes
        self._add_line("VectorXd simulate(int steps) const;", to_header=True)
        self._add_line("MatrixXd get_jacobian() const;", to_header=True)
        self._add_line("double compute_R0() const;", to_header=True)
        self._add_line("", to_header=True)
        
        self._dedent()
        self._add_line("private:", to_header=True)
        self._indent()
        
        # Déclarer les membres
        for param in node.parameters:
            cpp_type = self._type_to_cpp(param.type.name)
            self._add_line(f"{cpp_type} {param.name}_;", to_header=True)
        
        self._add_line("VectorXd initial_conditions_;", to_header=True)
        self._add_line("MatrixXd parameters_;", to_header=True)
        
        self._dedent()
        self._add_line("};", to_header=True)
        self._add_line("", to_header=True)
        
        # Implémenter le constructeur dans le source
        self._add_line(f"{node.name}Model::{node.name}Model({params_str})")
        self._indent()
        
        # Liste d'initialisation
        init_list = []
        for param in node.parameters:
            init_list.append(f"{param.name}_({param.name})")
        
        init_list.append("initial_conditions_(VectorXd::Zero(3))")
        init_list.append("parameters_(MatrixXd::Zero(3, 3))")
        
        if init_list:
            self._add_line(f": {', '.join(init_list)}")
        
        self._dedent()
        self._add_line("{")
        self._indent()
        
        # Générer le corps
        node.body.accept(self)
        
        self._dedent()
        self._add_line("}")
        self._add_line("")
        
        # Implémenter la méthode simulate
        self._add_line(f"VectorXd {node.name}Model::simulate(int steps) const")
        self._add_line("{")
        self._indent()
        self._add_line("VectorXd result(steps);")
        self._add_line("// Implémentation simplifiée de la simulation")
        self._add_line("for (int i = 0; i < steps; ++i) {")
        self._indent()
        self._add_line("result(i) = std::exp(-0.1 * i);  // Décroissance exponentielle")
        self._dedent()
        self._add_line("}")
        self._add_line("return result;")
        self._dedent()
        self._add_line("}")
        self._add_line("")
        
        # Implémenter le calcul de R0
        self._add_line(f"double {node.name}Model::compute_R0() const")
        self._add_line("{")
        self._indent()
        self._add_line("// Calcul du nombre de reproduction de base")
        self._add_line("double beta = 0.3;   // Taux de transmission")
        self._add_line("double gamma = 0.1;  // Taux de guérison")
        self._add_line("double mu = 0.01;    // Taux de mortalité")
        self._add_line("return beta / (gamma + mu);")
        self._dedent()
        self._add_line("}")
        self._add_line("")
    
    def visit_analysis_decl(self, node):
        # Générer une fonction d'analyse
        params_str = ", ".join([f"{self._type_to_cpp(p.type.name)} {p.name}" 
                               for p in node.parameters])
        return_type = "double"  # Par défaut
        
        self._add_line(f"{return_type} analyze_{node.name}({params_str})", to_header=True)
        self._add_line("{")
        self._indent()
        
        # Générer le corps
        node.body.accept(self)
        
        self._dedent()
        self._add_line("}")
        self._add_line("")
    
    def visit_data_decl(self, node):
        if node.source_type == 'CSV':
            self._generate_csv_loader(node)
    
    def _generate_csv_loader(self, node):
        """Générer le code pour charger un fichier CSV"""
        self.includes.add("vector")
        self.includes.add("string")
        self.includes.add("fstream")
        self.includes.add("sstream")
        
        self._add_line(f"std::vector<std::vector<double>> load_{node.name}_data(const std::string& filename)", to_header=True)
        self._add_line("{")
        self._indent()
        self._add_line("std::vector<std::vector<double>> data;")
        self._add_line("std::ifstream file(filename);")
        self._add_line("std::string line;")
        self._add_line("")
        self._add_line("while (std::getline(file, line)) {")
        self._indent()
        self._add_line("std::vector<double> row;")
        self._add_line("std::stringstream ss(line);")
        self._add_line("std::string value;")
        self._add_line("")
        self._add_line("while (std::getline(ss, value, ',')) {")
        self._indent()
        self._add_line("row.push_back(std::stod(value));")
        self._dedent()
        self._add_line("}")
        self._add_line("data.push_back(row);")
        self._dedent()
        self._add_line("}")
        self._add_line("")
        self._add_line("return data;")
        self._dedent()
        self._add_line("}")
        self._add_line("")
    
    def visit_var_decl(self, node):
        cpp_type = self._type_to_cpp(node.type.name)
        var_name = node.name
        
        if node.initializer:
            init_code = self._expression_to_cpp(node.initializer)
            self._add_line(f"{cpp_type} {var_name} = {init_code};")
        else:
            self._add_line(f"{cpp_type} {var_name};")
    
    def visit_assign_stmt(self, node):
        value_code = self._expression_to_cpp(node.value)
        self._add_line(f"{node.target} = {value_code};")
    
    def visit_if_stmt(self, node):
        condition = self._expression_to_cpp(node.condition)
        self._add_line(f"if ({condition}) {{")
        self._indent()
        node.then_block.accept(self)
        self._dedent()
        self._add_line("}")
        
        if node.else_block:
            self._add_line("else {")
            self._indent()
            node.else_block.accept(self)
            self._dedent()
            self._add_line("}")
    
    def visit_for_stmt(self, node):
        iterable = self._expression_to_cpp(node.iterable)
        
        # Pour l'instant, on suppose que c'est une boucle for standard
        if isinstance(node.iterable, Variable) and node.iterable.name == "range":
            # C'est un range, on génère une boucle for standard
            self._add_line(f"for (int {node.variable} = 0; {node.variable} < N; ++{node.variable}) {{")
        else:
            self._add_line(f"for (auto& {node.variable} : {iterable}) {{")
        
        self._indent()
        node.body.accept(self)
        self._dedent()
        self._add_line("}")
    
    def visit_while_stmt(self, node):
        condition = self._expression_to_cpp(node.condition)
        self._add_line(f"while ({condition}) {{")
        self._indent()
        node.body.accept(self)
        self._dedent()
        self._add_line("}")
    
    def visit_expr_stmt(self, node):
        expr = self._expression_to_cpp(node.expression)
        self._add_line(f"{expr};")
    
    def visit_return_stmt(self, node):
        value = self._expression_to_cpp(node.value)
        self._add_line(f"return {value};")
    
    def visit_analysis_stmt(self, node):
        if node.analysis_type == 'R0':
            self._add_line("// Calcul de R0")
            self._add_line("double R0 = compute_R0(beta, gamma, network);")
        elif node.analysis_type == 'sensitivity':
            param = self._expression_to_cpp(node.arguments[0])
            self._add_line(f"// Analyse de sensibilité pour {param}")
            self._add_line(f"MatrixXd sensitivity = compute_sensitivity(model, {param});")
        elif node.analysis_type == 'fit':
            data = self._expression_to_cpp(node.arguments[0])
            self._add_line(f"// Ajustement du modèle aux données {data}")
            self._add_line(f"VectorXd fitted_params = fit_model(model, {data});")
        elif node.analysis_type == 'forecast':
            steps = self._expression_to_cpp(node.arguments[0])
            self._add_line(f"// Prévision sur {steps} pas de temps")
            self._add_line(f"VectorXd forecast = forecast_model(model, {steps});")
    
    def _expression_to_cpp(self, expr) -> str:
        """Convertir une expression AST en code C++"""
        if isinstance(expr, BinaryOp):
            left = self._expression_to_cpp(expr.left)
            right = self._expression_to_cpp(expr.right)
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
            
            cpp_op = op_map.get(op, op)
            return f"({left} {cpp_op} {right})"
        
        elif isinstance(expr, UnaryOp):
            operand = self._expression_to_cpp(expr.operand)
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
            elif expr.type == 'float':
                return f"{expr.value}f"
            else:
                return str(expr.value)
        
        elif isinstance(expr, Call):
            callee = self._expression_to_cpp(expr.callee)
            args = [self._expression_to_cpp(arg) for arg in expr.arguments]
            args_str = ", ".join(args)
            return f"{callee}({args_str})"
        
        elif isinstance(expr, ListLiteral):
            # En C++, on utilise std::vector ou std::array
            elements = [self._expression_to_cpp(elem) for elem in expr.elements]
            elements_str = ", ".join(elements)
            return f"{{{elements_str}}}"
        
        elif isinstance(expr, DictLiteral):
            # En C++, on utilise std::map
            pairs = []
            for pair in expr.pairs:
                key = self._expression_to_cpp(pair.key)
                value = self._expression_to_cpp(pair.value)
                pairs.append(f"{{{key}, {value}}}")
            pairs_str = ", ".join(pairs)
            return f"std::map<{self._type_to_cpp('string')}, {self._type_to_cpp('float')}>{{{pairs_str}}}"
        
        elif isinstance(expr, Conditional):
            cond = self._expression_to_cpp(expr.condition)
            then_expr = self._expression_to_cpp(expr.then_expr)
            else_expr = self._expression_to_cpp(expr.else_expr)
            return f"({cond} ? {then_expr} : {else_expr})"
        
        else:
            return "0"
    
    def _type_to_cpp(self, enl_type: str) -> str:
        """Convertir un type EpiNetLang en type C++"""
        type_map = {
            'int': 'int',
            'float': 'double',
            'bool': 'bool',
            'string': 'std::string',
            'Network': 'std::shared_ptr<Network>',
            'Model': 'std::shared_ptr<Model>',
            'Data': 'std::vector<std::vector<double>>',
            'Matrix': 'MatrixXd',
            'Graph': 'std::shared_ptr<Graph>'
        }
        
        return type_map.get(enl_type, 'auto')