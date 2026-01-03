"""
Interface en ligne de commande pour EpiNetLang
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

# from src.ast.builder import ASTBuilder  # Éviter l'import circulaire
# Utiliser un import dynamique dans la fonction
# Utiliser un import dynamique dans la fonction
from src.core.symbol_table import SemanticAnalyzer
from src.core.type_system import TypeChecker
from src.core.optimizer import Optimizer
from src.ir.ir_builder import IRBuilder
from src.ir.passes import IROptimizer
from src.generators.python_generator import PythonGenerator
from src.generators.julia_generator import JuliaGenerator
from src.generators.cpp_generator import CppGenerator

def get_ast_builder():
    """Obtenir le builder d'AST (import dynamique pour éviter les problèmes circulaires)"""
# from src.ast.builder import ASTBuilder  # Éviter l'import circulaire
# Utiliser un import dynamique dans la fonction
    return ASTBuilder

def get_ast_builder():
    """Obtenir le builder d'AST (import dynamique pour éviter les problèmes circulaires)"""
    from src.ast.builder import ASTBuilder
    return ASTBuilder

class EpiNetLangCLI:
    """Interface en ligne de commande pour EpiNetLang"""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self):
        """Créer le parser d'arguments"""
        parser = argparse.ArgumentParser(
            description="EpiNetLang - Langage de modélisation de réseaux épidémiologiques",
            epilog="Exemple: epinetlang compile model.enl --target python --output model.py"
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
        
        # Commande compile
        compile_parser = subparsers.add_parser('compile', help='Compiler un fichier EpiNetLang')
        compile_parser.add_argument('input', help='Fichier source .enl')
        compile_parser.add_argument('--target', '-t', choices=['python', 'julia', 'cpp', 'ir'],
                                   default='python', help='Langage cible')
        compile_parser.add_argument('--output', '-o', help='Fichier de sortie')
        compile_parser.add_argument('--optimize', '-O', choices=['O0', 'O1', 'O2', 'O3'],
                                   default='O2', help='Niveau d\'optimisation')
        compile_parser.add_argument('--verbose', '-v', action='store_true',
                                   help='Mode verbeux')
        
        # Commande analyze
        analyze_parser = subparsers.add_parser('analyze', help='Analyser un fichier EpiNetLang')
        analyze_parser.add_argument('input', help='Fichier source .enl')
        analyze_parser.add_argument('--syntax', action='store_true',
                                   help='Vérifier uniquement la syntaxe')
        analyze_parser.add_argument('--semantic', action='store_true',
                                   help='Vérifier la sémantique')
        analyze_parser.add_argument('--type', action='store_true',
                                   help='Vérifier les types')
        
        # Commande run
        run_parser = subparsers.add_parser('run', help='Exécuter un fichier EpiNetLang')
        run_parser.add_argument('input', help='Fichier source .enl')
        run_parser.add_argument('--args', nargs='*', help='Arguments du programme')
        
        # Commande test
        test_parser = subparsers.add_parser('test', help='Exécuter les tests')
        test_parser.add_argument('--directory', '-d', default='tests',
                               help='Répertoire des tests')
        test_parser.add_argument('--pattern', '-p', default='test_*.py',
                               help='Pattern des fichiers de test')
        
        # Commande version
        subparsers.add_parser('version', help='Afficher la version')
        
        return parser
    
    def run(self, args=None):
        """Exécuter le CLI"""
        if args is None:
            args = sys.argv[1:]
        
        if not args:
            self.parser.print_help()
            return 0
        
        parsed_args = self.parser.parse_args(args)
        
        if parsed_args.command == 'compile':
            return self._handle_compile(parsed_args)
        elif parsed_args.command == 'analyze':
            return self._handle_analyze(parsed_args)
        elif parsed_args.command == 'run':
            return self._handle_run(parsed_args)
        elif parsed_args.command == 'test':
            return self._handle_test(parsed_args)
        elif parsed_args.command == 'version':
            return self._handle_version(parsed_args)
        else:
            self.parser.print_help()
            return 1
    
    def _handle_compile(self, args):
        """Gérer la commande compile"""
        try:
            # Lire le fichier source
            with open(args.input, 'r') as f:
                source_code = f.read()
            
            if args.verbose:
                print(f"Compilation de {args.input}...")
                print(f"Code source ({len(source_code)} caractères):")
                print("=" * 50)
                print(source_code)
                print("=" * 50)
            
            # Analyser la syntaxe
            ast = self._parse_source(source_code, args.input)
            if ast is None:
                return 1
            
            # Vérifier la sémantique
            if args.verbose:
                print("\nAnalyse sémantique...")
            
            semantic_analyzer = SemanticAnalyzer()
            errors, warnings = semantic_analyzer.analyze(ast)
            
            if errors:
                print("Erreurs sémantiques:")
                for error in errors:
                    print(f"  - {error}")
                return 1
            
            if warnings and args.verbose:
                print("Avertissements sémantiques:")
                for warning in warnings:
                    print(f"  - {warning}")
            
            # Vérifier les types
            if args.verbose:
                print("\nVérification des types...")
            
            type_checker = TypeChecker()
            type_errors = type_checker.check_program(ast)
            
            if type_errors:
                print("Erreurs de type:")
                for error in type_errors:
                    print(f"  - {error}")
                return 1
            
            # Optimiser l'AST
            if args.verbose:
                print(f"\nOptimisation (niveau {args.optimize})...")
            
            optimizer = Optimizer()
            ast = optimizer.optimize(ast, level=args.optimize)
            
            # Générer le code cible
            if args.verbose:
                print(f"\nGénération de code {args.target}...")
            
            if args.target == 'python':
                generator = PythonGenerator()
                output_code = generator.generate(ast)
                output_ext = '.py'
            
            elif args.target == 'julia':
                generator = JuliaGenerator()
                output_code = generator.generate(ast)
                output_ext = '.jl'
            
            elif args.target == 'cpp':
                generator = CppGenerator()
                header_code, source_code = generator.generate(ast)
                output_ext = '.cpp'
                # Pour C++, nous avons deux fichiers
                output_name = args.output or Path(args.input).stem
                header_file = f"{output_name}.hpp"
                source_file = f"{output_name}.cpp"
                
                with open(header_file, 'w') as f:
                    f.write(header_code)
                
                with open(source_file, 'w') as f:
                    f.write(source_code)
                
                if args.verbose:
                    print(f"Fichiers générés: {header_file}, {source_file}")
                return 0
            
            elif args.target == 'ir':
                # Générer l'IR
                ir_builder = IRBuilder()
                ir_module = ir_builder.build_from_ast(ast)
                
                # Optimiser l'IR
                ir_optimizer = IROptimizer()
                ir_module = ir_optimizer.optimize(ir_module, level=args.optimize)
                
                output_code = str(ir_module)
                output_ext = '.ir'
            
            else:
                print(f"Langage cible non supporté: {args.target}")
                return 1
            
            # Déterminer le fichier de sortie
            if args.output:
                output_file = args.output
            else:
                input_stem = Path(args.input).stem
                output_file = f"{input_stem}{output_ext}"
            
            # Écrire le fichier de sortie
            with open(output_file, 'w') as f:
                f.write(output_code)
            
            if args.verbose:
                print(f"Code généré ({len(output_code)} caractères):")
                print("=" * 50)
                print(output_code)
                print("=" * 50)
                print(f"\nFichier écrit: {output_file}")
            else:
                print(f"Compilation réussie: {output_file}")
            
            return 0
            
        except FileNotFoundError:
            print(f"Fichier non trouvé: {args.input}")
            return 1
        except Exception as e:
            print(f"Erreur lors de la compilation: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1
    
    def _handle_analyze(self, args):
        """Gérer la commande analyze"""
        try:
            # Lire le fichier source
            with open(args.input, 'r') as f:
                source_code = f.read()
            
            print(f"Analyse de {args.input}...")
            
            # Analyser la syntaxe
            ast = self._parse_source(source_code, args.input)
            if ast is None:
                return 1
            
            print("✓ Syntaxe correcte")
            
            if args.semantic or (not args.syntax and not args.type):
                # Vérifier la sémantique
                semantic_analyzer = SemanticAnalyzer()
                errors, warnings = semantic_analyzer.analyze(ast)
                
                if errors:
                    print("✗ Erreurs sémantiques:")
                    for error in errors:
                        print(f"  - {error}")
                    return 1
                else:
                    print("✓ Sémantique correcte")
                
                if warnings:
                    print("⚠ Avertissements sémantiques:")
                    for warning in warnings:
                        print(f"  - {warning}")
            
            if args.type or (not args.syntax and not args.semantic):
                # Vérifier les types
                type_checker = TypeChecker()
                type_errors = type_checker.check_program(ast)
                
                if type_errors:
                    print("✗ Erreurs de type:")
                    for error in type_errors:
                        print(f"  - {error}")
                    return 1
                else:
                    print("✓ Types corrects")
            
            print("\nAnalyse terminée avec succès!")
            return 0
            
        except FileNotFoundError:
            print(f"Fichier non trouvé: {args.input}")
            return 1
        except Exception as e:
            print(f"Erreur lors de l'analyse: {e}")
            return 1
    
    def _handle_run(self, args):
        """Gérer la commande run"""
        try:
            # Pour l'exécution, nous compilons en Python et exécutons
            if args.verbose:
                print(f"Exécution de {args.input}...")
            
            # Compiler en Python
            import tempfile
            import subprocess
            
            with open(args.input, 'r') as f:
                source_code = f.read()
            
            ast = self._parse_source(source_code, args.input)
            if ast is None:
                return 1
            
            # Générer le code Python
            generator = PythonGenerator()
            python_code = generator.generate(ast)
            
            # Écrire dans un fichier temporaire
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(python_code)
                temp_file = f.name
            
            try:
                # Exécuter le code Python
                cmd = ['python', temp_file]
                if args.args:
                    cmd.extend(args.args)
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                print("Sortie standard:")
                print(result.stdout)
                
                if result.stderr:
                    print("Erreur standard:")
                    print(result.stderr)
                
                return result.returncode
                
            finally:
                # Nettoyer le fichier temporaire
                os.unlink(temp_file)
            
        except FileNotFoundError:
            print(f"Fichier non trouvé: {args.input}")
            return 1
        except Exception as e:
            print(f"Erreur lors de l'exécution: {e}")
            return 1
    
    def _handle_test(self, args):
        """Gérer la commande test"""
        try:
            import pytest
            
            test_dir = args.directory
            test_pattern = args.pattern
            
            if not os.path.exists(test_dir):
                print(f"Répertoire de tests non trouvé: {test_dir}")
                return 1
            
            print(f"Exécution des tests dans {test_dir}...")
            
            # Exécuter pytest
            pytest_args = [
                test_dir,
                f'--tb=short',
                '-v'
            ]
            
            return pytest.main(pytest_args)
            
        except ImportError:
            print("pytest n'est pas installé. Installez-le avec: pip install pytest")
            return 1
        except Exception as e:
            print(f"Erreur lors de l'exécution des tests: {e}")
            return 1
    
    def _handle_version(self, args):
        """Gérer la commande version"""
        print("EpiNetLang v1.0.0")
        print("Langage de modélisation de réseaux épidémiologiques")
        print("Copyright (c) 2024")
        return 0
    
    def _parse_source(self, source_code: str, filename: str = "<input>"):
        """Analyser le code source et construire l'AST"""
        try:
            import antlr4
            from grammar.Lexer import Lexer
            from grammar.Parser import Parser
            
            # Créer le flux d'entrée
            input_stream = antlr4.InputStream(source_code)
            
            # Créer le lexer et le parser
            lexer = Lexer(input_stream)
            stream = antlr4.CommonTokenStream(lexer)
            parser = Parser(stream)
            
            # Analyser le programme
            tree = parser.program()
            
            # Vérifier les erreurs de syntaxe
            if parser.getNumberOfSyntaxErrors() > 0:
                print("Erreurs de syntaxe:")
                for error in parser.getErrors():
                    print(f"  - {error}")
                return None
            
            # Construire l'AST
            builder = ASTBuilder()
            ast = builder.visitProgram(tree)
            
            return ast
            
        except ImportError as e:
            print(f"Erreur d'importation: {e}")
            print("Assurez-vous que les grammaires ANTLR sont générées.")
            print("Exécutez: antlr4 -Dlanguage=Python3 grammar/*.g4")
            return None
        except Exception as e:
            print(f"Erreur d'analyse syntaxique: {e}")
            return None

def main():
    """Fonction principale"""
    cli = EpiNetLangCLI()
    sys.exit(cli.run())

if __name__ == "__main__":
    main()