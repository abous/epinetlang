"""
Tests du parseur et du constructeur d'AST
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path

# Configuration du chemin avant les imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Maintenant nous pouvons importer
from src.ast.builder import ASTBuilder

# Essayer d'importer ANTLR
try:
    import antlr4
    from grammar.Lexer import Lexer
    from grammar.Parser import Parser
    HAS_ANTLR = True
except ImportError:
    HAS_ANTLR = False
    print("ANTLR n'est pas disponible. Certains tests seront ignorés.")
    print("Pour générer les fichiers ANTLR, exécutez:")
    print("antlr4 -Dlanguage=Python3 grammar/*.g4 -o grammar/")

class TestParser(unittest.TestCase):
    """Tests du parseur EpiNetLang"""
    
    def setUp(self):
        if not HAS_ANTLR:
            self.skipTest("ANTLR n'est pas disponible")
        self.builder = ASTBuilder()
    
    def _parse_source(self, source_code):
        """Analyser le code source et retourner l'AST"""
        input_stream = antlr4.InputStream(source_code)
        lexer = Lexer(input_stream)
        stream = antlr4.CommonTokenStream(lexer)
        parser = Parser(stream)
        tree = parser.program()
        
        if parser.getNumberOfSyntaxErrors() > 0:
            return None
        
        ast = self.builder.visitProgram(tree)
        return ast
    
    def test_empty_program(self):
        """Tester un programme vide"""
        source = ""
        ast = self._parse_source(source)
        self.assertIsNotNone(ast)
        self.assertEqual(len(ast.declarations), 0)
    
    # ... [le reste des tests reste inchangé] ...
    
    @unittest.skipUnless(HAS_ANTLR, "ANTLR requis")
    def test_complex_model(self):
        """Tester un modèle complexe"""
        source = """
        model ComplexSIR(
            float beta = 0.3,
            float gamma = 0.1,
            float mu = 0.001,
            float birth_rate = 0.001,
            int population = 1000
        ) {
            // États initiaux
            float S = population - 10;
            float I = 10;
            float R = 0;
            
            // Équations différentielles
            float dS = birth_rate * population - beta * S * I / population - mu * S;
            float dI = beta * S * I / population - gamma * I - mu * I;
            float dR = gamma * I - mu * R;
            
            // Calcul analytique de R0
            float R0_analytic = beta / (gamma + mu);
            
            // Matrice de nouvelle génération
            Matrix G = [[0, beta * S / population],
                        [1/(gamma + mu), 0]];
            
            // Valeurs propres pour R0
            Matrix eigenvalues = eig(G);
            float R0_matrix = max(eigenvalues);
            
            // Analyse de sensibilité
            sensitivity("beta");
            sensitivity("gamma");
            sensitivity("mu");
            
            return {
                "states": [S, I, R],
                "derivatives": [dS, dI, dR],
                "R0_analytic": R0_analytic,
                "R0_matrix": R0_matrix,
                "next_generation": G
            };
        }
        """
        
        ast = self._parse_source(source)
        self.assertIsNotNone(ast)
        
        # Vérifier que le modèle complexe est parsé correctement
        model_decl = ast.declarations[0]
        self.assertEqual(model_decl.name, "ComplexSIR")
        self.assertEqual(len(model_decl.parameters), 5)
        self.assertGreater(len(model_decl.body.statements), 10)

if __name__ == '__main__':
    unittest.main()
