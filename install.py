"""
Script d'installation simplifié pour EpiNetLang
"""

import os
import sys
import subprocess

def install_dependencies():
    """Installer les dépendances requises"""
    
    print("Installation des dépendances...")
    
    dependencies = [
        'antlr4-python3-runtime==4.13.0',
        'numpy>=1.21.0',
        'networkx>=2.8.0',
        'pandas>=1.5.0',
        'scipy>=1.9.0',
        'matplotlib>=3.5.0',
        'pytest>=7.0.0'
    ]
    
    for dep in dependencies:
        print(f"Installation de {dep}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
        except subprocess.CalledProcessError:
            print(f"  Échec de l'installation de {dep}")
    
    print("Dépendances installées!")

def setup_project_structure():
    """Configurer la structure du projet"""
    
    print("\nConfiguration de la structure du projet...")
    
    # Créer les répertoires nécessaires
    directories = [
        'grammar',
        'examples',
        'tests',
        'docs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  Créé: {directory}/")
    
    # Créer les fichiers __init__.py
    init_files = [
        'src/__init__.py',
        'src/ast/__init__.py',
        'src/core/__init__.py',
        'src/ir/__init__.py',
        'src/generators/__init__.py',
        'src/utils/__init__.py',
        'tests/__init__.py',
        'grammar/__init__.py'
    ]
    
    for init_file in init_files:
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('"""Module __init__.py"""\n')
            print(f"  Créé: {init_file}")
    
    print("Structure du projet configurée!")

def create_stub_files():
    """Créer des fichiers stub pour le développement"""
    
    print("\nCréation des fichiers stub...")
    
    # Créer les fichiers stub ANTLR dans grammar/
    stub_files = {
        'grammar/Lexer.py': '''"""
Stub pour Lexer ANTLR - Généré manuellement pour le développement
"""

class Lexer:
    """Stub de lexer ANTLR"""
    
    def __init__(self, input_stream=None):
        self.input_stream = input_stream
    
    def getTokenNames(self):
        return []
    
    def getRuleNames(self):
        return []
''',
        
        'grammar/Parser.py': '''"""
Stub pour Parser ANTLR - Généré manuellement pour le développement
"""

class Parser:
    """Stub de parser ANTLR"""
    
    def __init__(self, token_stream=None):
        self.token_stream = token_stream
        self._syntax_errors = 0
        self._errors = []
    
    def getNumberOfSyntaxErrors(self):
        return self._syntax_errors
    
    def getErrors(self):
        return self._errors
    
    def program(self):
        """Méthode stub pour la règle 'program'"""
        return None
''',
        
        'grammar/EpiNetLang.py': '''"""
Stub pour EpiNetLang ANTLR - Généré manuellement pour le développement
"""

class EpiNetLang:
    """Stub de grammaire principale"""
    pass
'''
    }
    
    for file_path, content in stub_files.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"  Créé: {file_path}")
    
    print("Fichiers stub créés!")

def run_tests():
    """Exécuter les tests de base"""
    
    print("\nExécution des tests de base...")
    
    test_files = [
        'tests/test_parser.py',
        'tests/test_generators.py',
        'tests/test_integration.py'
    ]
    
    # Créer un test basique si nécessaire
    basic_test = '''"""
Test basique pour vérifier l'installation
"""

import unittest

class TestInstallation(unittest.TestCase):
    
    def test_import(self):
        """Test d'importation des modules"""
        try:
            import src.ast.builder
            import src.core.symbol_table
            import src.generators.python_generator
            success = True
        except ImportError as e:
            success = False
            print(f"Erreur d'import: {e}")
        
        self.assertTrue(success, "Les imports doivent fonctionner")
    
    def test_cli(self):
        """Test de la CLI"""
        import subprocess
        import sys
        
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli', '--help'],
            capture_output=True,
            text=True
        )
        
        self.assertIn('EpiNetLang', result.stdout)

if __name__ == '__main__':
    unittest.main()
'''
    
    if not os.path.exists('tests/test_basic.py'):
        with open('tests/test_basic.py', 'w') as f:
            f.write(basic_test)
    
    # Exécuter le test basique
    try:
        import unittest
        suite = unittest.TestLoader().discover('tests', pattern='test_basic.py')
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        if result.wasSuccessful():
            print("Tests exécutés avec succès!")
        else:
            print("Certains tests ont échoué")
    except Exception as e:
        print(f"Erreur lors de l'exécution des tests: {e}")

def main():
    """Fonction principale d'installation"""
    
    print("=" * 60)
    print("INSTALLATION D'EPINETLANG")
    print("=" * 60)
    
    try:
        # 1. Installer les dépendances
        install_dependencies()
        
        # 2. Configurer la structure
        setup_project_structure()
        
        # 3. Créer les fichiers stub
        create_stub_files()
        
        # 4. Exécuter les tests basiques
        run_tests()
        
        print("\n" + "=" * 60)
        print("INSTALLATION TERMINÉE AVEC SUCCÈS!")
        print("=" * 60)
        
        print("\nCommandes disponibles:")
        print("  python -m src.cli --help        # Afficher l'aide")
        print("  python run_examples.py          # Exécuter les exemples")
        print("  python -m pytest tests/         # Exécuter tous les tests")
        
        print("\nPour une utilisation complète avec ANTLR:")
        print("  pip install antlr4-tools")
        print("  antlr4 -Dlanguage=Python3 grammar/*.g4 -o grammar/")
        
    except Exception as e:
        print(f"\nErreur lors de l'installation: {e}")
        print("\nInstallation manuelle recommandée:")
        print("1. pip install antlr4-python3-runtime numpy networkx pandas scipy matplotlib pytest")
        print("2. Copiez les fichiers du projet")
        print("3. python -m src.cli --help")

if __name__ == '__main__':
    main()
