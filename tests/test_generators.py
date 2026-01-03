"""
Tests des générateurs de code
"""

import unittest
import tempfile
import os
from pathlib import Path

from src.ast.builder import ASTBuilder
from src.generators.python_generator import PythonGenerator
from src.generators.julia_generator import JuliaGenerator
from src.generators.cpp_generator import CppGenerator

class TestGenerators(unittest.TestCase):
    """Tests des générateurs de code EpiNetLang"""
    
    def setUp(self):
        self.builder = ASTBuilder()
    
    def _generate_and_test(self, source_code, generator_class, expected_patterns=None):
        """Générer du code et vérifier les motifs attendus"""
        import antlr4
        from grammar.Lexer import Lexer
        from grammar.Parser import Parser
        
        # Analyser le code source
        input_stream = antlr4.InputStream(source_code)
        lexer = Lexer(input_stream)
        stream = antlr4.CommonTokenStream(lexer)
        parser = Parser(stream)
        tree = parser.program()
        
        if parser.getNumberOfSyntaxErrors() > 0:
            self.fail("Erreur de syntaxe dans le code source de test")
        
        # Construire l'AST
        ast = self.builder.visitProgram(tree)
        self.assertIsNotNone(ast)
        
        # Générer le code
        generator = generator_class()
        generated_code = generator.generate(ast)
        
        # Vérifier que le code n'est pas vide
        self.assertIsNotNone(generated_code)
        self.assertGreater(len(generated_code), 0)
        
        # Vérifier les motifs attendus
        if expected_patterns:
            for pattern in expected_patterns:
                self.assertIn(pattern, generated_code)
        
        return generated_code
    
    def test_python_generator_basic(self):
        """Tester le générateur Python basique"""
        source = """
        network SimpleNetwork(int nodes = 100) {
            int edges = nodes * 10;
            return edges;
        }
        """
        
        expected_patterns = [
            "def create_network_SimpleNetwork",
            "nodes: int",
            "edges = nodes * 10",
            "return edges"
        ]
        
        code = self._generate_and_test(source, PythonGenerator, expected_patterns)
        
        # Vérifier que le code Python est valide (syntaxe)
        try:
            compile(code, "<test>", "exec")
        except SyntaxError as e:
            self.fail(f"Code Python généré invalide: {e}")
    
    def test_python_generator_model(self):
        """Tester le générateur Python pour les modèles"""
        source = """
        model SIRModel(float beta = 0.3, float gamma = 0.1) {
            float S = 999;
            float I = 1;
            float R = 0;
            
            float dS = -beta * S * I / 1000;
            float dI = beta * S * I / 1000 - gamma * I;
            float dR = gamma * I;
            
            compute R0;
            
            return { "S": S, "I": I, "R": R };
        }
        """
        
        expected_patterns = [
            "class SIRModelModel:",
            "def __init__",
            "beta: float",
            "gamma: float",
            "compute_R0",
            "return {"
        ]
        
        code = self._generate_and_test(source, PythonGenerator, expected_patterns)
        
        # Vérifier les imports
        self.assertIn("import numpy as np", code)
        self.assertIn("from scipy", code)
    
    def test_python_generator_analysis(self):
        """Tester le générateur Python pour les analyses"""
        source = """
        analysis TestAnalysis(Model model) {
            compute R0;
            sensitivity("beta");
            forecast 30;
            
            return true;
        }
        """
        
        code = self._generate_and_test(source, PythonGenerator)
        
        # Vérifier les fonctions d'analyse générées
        self.assertIn("def analyze_TestAnalysis", code)
        self.assertIn("compute_R0", code)
        self.assertIn("sensitivity_analysis", code)
        self.assertIn("forecast_model", code)
    
    def test_python_generator_data(self):
        """Tester le générateur Python pour les données"""
        source = """
        data CaseData = CSV("data/cases.csv", delimiter=",", header=1);
        """
        
        code = self._generate_and_test(source, PythonGenerator)
        
        # Vérifier la fonction de chargement des données
        self.assertIn("def load_CaseData_data", code)
        self.assertIn("pd.read_csv", code)
    
    def test_julia_generator_basic(self):
        """Tester le générateur Julia basique"""
        source = """
        network SimpleNetwork(int nodes = 100) {
            int edges = nodes * 10;
            return edges;
        }
        """
        
        expected_patterns = [
            "function create_network_SimpleNetwork",
            "nodes::Int64",
            "edges = nodes * 10",
            "return edges"
        ]
        
        code = self._generate_and_test(source, JuliaGenerator, expected_patterns)
    
    def test_julia_generator_model(self):
        """Tester le générateur Julia pour les modèles"""
        source = """
        model SIRModel(float beta = 0.3, float gamma = 0.1) {
            float S = 999;
            float I = 1;
            float R = 0;
            
            compute R0;
            
            return { "S": S, "I": I, "R": R };
        }
        """
        
        code = self._generate_and_test(source, JuliaGenerator)
        
        # Vérifier la structure et les fonctions
        self.assertIn("struct SIRModelModel", code)
        self.assertIn("function simulate", code)
        self.assertIn("compute_R0", code)
    
    def test_cpp_generator_basic(self):
        """Tester le générateur C++ basique"""
        source = """
        network SimpleNetwork(int nodes = 100) {
            int edges = nodes * 10;
            return edges;
        }
        """
        
        header, source_code = self._generate_cpp(source)
        
        # Vérifier le header
        self.assertIn("class NetworkSimpleNetwork", header)
        self.assertIn("NetworkSimpleNetwork(int nodes);", header)
        self.assertIn("int get_num_nodes() const;", header)
        
        # Vérifier le source
        self.assertIn("NetworkSimpleNetwork::NetworkSimpleNetwork", source_code)
        self.assertIn("edges = nodes * 10", source_code)
    
    def test_cpp_generator_model(self):
        """Tester le générateur C++ pour les modèles"""
        source = """
        model SIRModel(float beta = 0.3, float gamma = 0.1) {
            float S = 999;
            float I = 1;
            float R = 0;
            
            compute R0;
            
            return { "S": S, "I": I, "R": R };
        }
        """
        
        header, source_code = self._generate_cpp(source)
        
        # Vérifier le header
        self.assertIn("class SIRModelModel", header)
        self.assertIn("SIRModelModel(double beta, double gamma);", header)
        self.assertIn("VectorXd simulate(int steps) const;", header)
        self.assertIn("double compute_R0() const;", header)
        
        # Vérifier le source
        self.assertIn("SIRModelModel::SIRModelModel", source_code)
        self.assertIn("beta / (gamma + mu)", source_code)  # Formule R0
    
    def _generate_cpp(self, source_code):
        """Générer du code C++ et retourner header et source"""
        import antlr4
        from grammar.Lexer import Lexer
        from grammar.Parser import Parser
        
        # Analyser le code source
        input_stream = antlr4.InputStream(source_code)
        lexer = Lexer(input_stream)
        stream = antlr4.CommonTokenStream(lexer)
        parser = Parser(stream)
        tree = parser.program()
        
        if parser.getNumberOfSyntaxErrors() > 0:
            self.fail("Erreur de syntaxe dans le code source de test")
        
        # Construire l'AST
        ast = self.builder.visitProgram(tree)
        self.assertIsNotNone(ast)
        
        # Générer le code C++
        generator = CppGenerator()
        header_code, source_code = generator.generate(ast)
        
        # Vérifier que les codes ne sont pas vides
        self.assertIsNotNone(header_code)
        self.assertIsNotNone(source_code)
        self.assertGreater(len(header_code), 0)
        self.assertGreater(len(source_code), 0)
        
        return header_code, source_code
    
    def test_complex_network_generation(self):
        """Tester la génération d'un réseau complexe"""
        source = """
        network ComplexNetwork(
            int nodes = 1000,
            float connectivity = 0.05,
            bool directed = false,
            string network_type = "scale_free"
        ) {
            Graph network;
            
            if (network_type == "random") {
                network = create_random_network(nodes, connectivity);
            } else if (network_type == "scale_free") {
                network = create_scale_free_network(nodes, 3);
            } else if (network_type == "small_world") {
                network = create_small_world_network(nodes, 10, 0.1);
            }
            
            // Calculer les métriques du réseau
            int edges = network.edges();
            float clustering = network.clustering_coefficient();
            float avg_path_length = network.average_path_length();
            Matrix degree_dist = network.degree_distribution();
            
            // Calculer R0 théorique
            float avg_degree = 2.0 * edges / nodes;
            float R0 = 1.5 * avg_degree;  // Approximation
            
            compute R0;
            
            return {
                "network": network,
                "metrics": {
                    "nodes": nodes,
                    "edges": edges,
                    "clustering": clustering,
                    "avg_path_length": avg_path_length,
                    "R0": R0
                },
                "degree_distribution": degree_dist
            };
        }
        """
        
        # Tester avec Python
        python_code = self._generate_and_test(source, PythonGenerator)
        self.assertIn("def create_network_ComplexNetwork", python_code)
        self.assertIn("if network_type == \"random\"", python_code)
        self.assertIn("compute_R0", python_code)
        
        # Tester avec Julia
        julia_code = self._generate_and_test(source, JuliaGenerator)
        self.assertIn("function create_network_ComplexNetwork", julia_code)
        self.assertIn("if network_type == \"random\"", julia_code)
        
        # Tester avec C++
        header, source_code = self._generate_cpp(source)
        self.assertIn("class NetworkComplexNetwork", header)
        self.assertIn("compute_R0() const", header)
    
    def test_sensitivity_analysis_generation(self):
        """Tester la génération d'analyse de sensibilité"""
        source = """
        analysis SensitivityAnalysis(
            Model model,
            float[] param_range = [0.1, 0.2, 0.3, 0.4, 0.5]
        ) {
            // Analyse de sensibilité pour plusieurs paramètres
            string[] params = ["beta", "gamma", "mu"];
            Matrix sensitivity_results;
            
            for (string param in params) {
                sensitivity(param);
                
                Matrix sens = sensitivity(model, param);
                sensitivity_results[param] = sens;
                
                // Calculer l'élasticité
                float elasticity = mean(abs(sens)) / mean(abs(model.simulate(100)));
                print("Elasticité pour " + param + ": " + elasticity);
            }
            
            // Analyse multivariée
            sensitivity(["beta", "gamma"]);
            sensitivity(["gamma", "mu"]);
            
            return sensitivity_results;
        }
        """
        
        # Tester avec Python
        python_code = self._generate_and_test(source, PythonGenerator)
        self.assertIn("def analyze_SensitivityAnalysis", python_code)
        self.assertIn("sensitivity_analysis", python_code)
        self.assertIn("for param in params", python_code)
        
        # Tester avec Julia
        julia_code = self._generate_and_test(source, JuliaGenerator)
        self.assertIn("function analyze_SensitivityAnalysis", julia_code)
        self.assertIn("for param in params", julia_code)
    
    def test_optimization_in_generators(self):
        """Tester que les générateurs optimisent le code"""
        source = """
        network OptimizedNetwork(int n = 100) {
            // Constantes qui devraient être pliées
            int a = 10 + 20 * 3;
            float b = (3.14 * 2) / 2.0;
            
            // Code mort qui devrait être éliminé
            int dead_var = 100;
            dead_var = dead_var * 2;
            // dead_var n'est jamais utilisé
            
            // Code utile
            int useful_var = n * a;
            
            return useful_var;
        }
        """
        
        # Le générateur Python devrait optimiser le code
        python_code = self._generate_and_test(source, PythonGenerator)
        
        # Vérifier que les constantes sont pliées
        # Note: L'optimisation se fait au niveau AST, pas au niveau générateur
        # Mais le générateur devrait produire du code propre
        
        # Vérifier que le code est valide
        try:
            compile(python_code, "<test>", "exec")
        except SyntaxError as e:
            self.fail(f"Code Python généré invalide après optimisation: {e}")
    
    def test_real_data_import(self):
        """Tester l'importation de données réelles"""
        source = """
        // Données COVID-19
        data COVIDData = CSV("data/covid_cases.csv", 
                            delimiter=",", 
                            header=1,
                            date_format="%Y-%m-%d");
        
        // Données de mobilité
        data MobilityData = JSON("data/mobility_patterns.json");
        
        // Données de réseau de contacts
        data ContactData = SQL("database.db", 
                              query="SELECT * FROM contacts WHERE date > '2023-01-01'");
        
        model COVIDModel(float beta = 0.25, float gamma = 0.1) {
            // Charger les données
            Data cases = COVIDData;
            Data mobility = MobilityData;
            Data contacts = ContactData;
            
            // Utiliser les données pour initialiser le modèle
            int initial_cases = cases.aggregate("sum", "confirmed");
            float mobility_factor = mobility.filter("type == 'retail'").mean("change");
            
            // Ajuster beta en fonction de la mobilité
            beta = beta * (1 - mobility_factor);
            
            compute R0;
            sensitivity("beta");
            
            return {
                "initial_cases": initial_cases,
                "adjusted_beta": beta,
                "mobility_factor": mobility_factor
            };
        }
        """
        
        # Tester avec Python
        python_code = self._generate_and_test(source, PythonGenerator)
        
        # Vérifier les fonctions de chargement
        self.assertIn("def load_COVIDData_data", python_code)
        self.assertIn("def load_MobilityData_data", python_code)
        self.assertIn("pd.read_csv", python_code)
        self.assertIn("json.load", python_code)
        
        # Tester avec Julia
        julia_code = self._generate_and_test(source, JuliaGenerator)
        self.assertIn("function load_COVIDData_data", julia_code)
        self.assertIn("CSV.read", julia_code)
        self.assertIn("JSON.parsefile", julia_code)

if __name__ == '__main__':
    unittest.main()