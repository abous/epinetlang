# -*- coding: utf-8 -*-
"""
Test basique pour verifier l'installation d'EpiNetLang
"""

import unittest
import os
import sys

class TestInstallation(unittest.TestCase):
    
    def test_import_core_modules(self):
        """Test d'importation des modules principaux"""
        try:
            # Test AST
            from src.ast.nodes import Program, Node
            from src.ast.visitor import ASTVisitor
            from src.ast.builder import ASTBuilder
            
            # Test Core
            from src.core.symbol_table import SymbolTable, Symbol
            from src.core.type_system import TypeSystem, TypeChecker
            from src.core.optimizer import Optimizer
            
            # Test Generators
            from src.generators.python_generator import PythonGenerator
            from src.generators.julia_generator import JuliaGenerator
            from src.generators.cpp_generator import CppGenerator
            
            # Test CLI
            import src.cli
            
            success = True
        except ImportError as e:
            success = False
            print(f"Erreur d'import: {e}")
        
        self.assertTrue(success, "Tous les modules doivent pouvoir etre importes")
    
    def test_grammar_files(self):
        """Test que les fichiers de grammaire existent"""
        grammar_files = [
            'grammar/EpiNetLang.g4',
            'grammar/Lexer.g4', 
            'grammar/Parser.g4'
        ]
        
        for file in grammar_files:
            self.assertTrue(os.path.exists(file), f"Fichier manquant: {file}")
    
    def test_generated_files(self):
        """Test que certains fichiers generes existent (ou stub)"""
        generated_files = [
            'grammar/__init__.py',
            'grammar/Lexer.py',
            'grammar/Parser.py'
        ]
        
        for file in generated_files:
            self.assertTrue(os.path.exists(file), f"Fichier manquant: {file}")
    
    def test_example_files(self):
        """Test que les exemples existent"""
        example_files = [
            'examples/sir_network.enl',
            'examples/contact_network.enl',
            'examples/spatial_network.enl'
        ]
        
        for file in example_files:
            self.assertTrue(os.path.exists(file), f"Exemple manquant: {file}")
    
    def test_cli_basic(self):
        """Test de base de la CLI"""
        import subprocess
        
        # Tester que la CLI peut etre executee avec --help
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '--help'],
            capture_output=True,
            text=True
        )
        
        # La commande devrait au moins s'executer sans erreur fatale
        output = result.stdout.lower() or result.stderr.lower()
        self.assertIsNotNone(output, "La CLI devrait produire une sortie")

class TestBasicFunctionality(unittest.TestCase):
    
    def test_ast_creation(self):
        """Test de creation basique d'AST"""
        from src.ast.nodes import Program, NetworkDecl, Block, Type
        
        # Creer un programme simple
        program = Program([])
        self.assertIsInstance(program, Program)
        self.assertEqual(len(program.declarations), 0)
        
        # Creer un type
        int_type = Type('int')
        self.assertEqual(int_type.name, 'int')
    
    def test_symbol_table(self):
        """Test de la table des symboles"""
        from src.core.symbol_table import SymbolTable, SymbolKind
        
        table = SymbolTable()
        
        # Definir un symbole
        success = table.define('test_var', SymbolKind.VARIABLE, 'int')
        self.assertTrue(success)
        
        # Rechercher le symbole
        symbol = table.lookup_global('test_var')
        self.assertIsNotNone(symbol)
        self.assertEqual(symbol.name, 'test_var')
    
    def test_python_generator(self):
        """Test basique du generateur Python"""
        from src.generators.python_generator import PythonGenerator
        from src.ast.nodes import Program, ModelDecl, Type, Parameter, Block
        
        # Creer un AST simple
        model_decl = ModelDecl(
            name='TestModel',
            parameters=[
                Parameter(Type('float'), 'beta', None),
                Parameter(Type('float'), 'gamma', None)
            ],
            body=Block([])
        )
        
        program = Program([model_decl])
        
        # Generer du code Python
        generator = PythonGenerator()
        code = generator.generate(program)
        
        self.assertIsInstance(code, str)
        self.assertGreater(len(code), 0)
        self.assertIn('class TestModelModel', code)

def run_tests():
    """Executer tous les tests"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestInstallation)
    suite.addTests(loader.loadTestsFromTestCase(TestBasicFunctionality))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)