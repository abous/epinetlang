"""
Tests complets d'EpiNetLang
"""

import unittest
import os
import sys
import tempfile
import subprocess
from pathlib import Path

# Ajouter le chemin
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestFullEpiNetLang(unittest.TestCase):
    """Tests complets du système EpiNetLang"""
    
    def setUp(self):
        """Préparation des tests"""
        self.test_dir = tempfile.mkdtemp(prefix="epinetlang_test_")
        
        # Chemin vers les exemples
        self.examples_dir = os.path.join(os.path.dirname(__file__), '..', 'examples')
        
        # Chemin vers le CLI
        self.cli_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'cli.py')
    
    def tearDown(self):
        """Nettoyage après les tests"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_compile_sir_example(self):
        """Compiler l'exemple SIR"""
        example_file = os.path.join(self.examples_dir, 'sir_network.enl')
        
        if not os.path.exists(example_file):
            self.skipTest(f"Fichier d'exemple non trouvé: {example_file}")
        
        # Compiler vers Python
        output_file = os.path.join(self.test_dir, 'sir_model.py')
        result = subprocess.run(
            [sys.executable, self.cli_path, 'compile', 
             example_file, '--target', 'python', '--output', output_file],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0,
                        f"Échec compilation SIR: {result.stderr}")
        
        # Vérifier que le fichier existe
        self.assertTrue(os.path.exists(output_file))
        
        # Vérifier le contenu
        with open(output_file, 'r') as f:
            content = f.read()
        
        self.assertIn("class SIRNetwork", content)
        self.assertIn("compute_R0", content)
    
    def test_compile_contact_example(self):
        """Compiler l'exemple de réseau de contacts"""
        example_file = os.path.join(self.examples_dir, 'contact_network.enl')
        
        if not os.path.exists(example_file):
            self.skipTest(f"Fichier d'exemple non trouvé: {example_file}")
        
        # Compiler vers Python
        output_file = os.path.join(self.test_dir, 'contact_model.py')
        result = subprocess.run(
            [sys.executable, self.cli_path, 'compile', 
             example_file, '--target', 'python', '--output', output_file],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0,
                        f"Échec compilation contact: {result.stderr}")
        
        # Vérifier que le fichier existe
        self.assertTrue(os.path.exists(output_file))
        
        # Vérifier le contenu
        with open(output_file, 'r') as f:
            content = f.read()
        
        self.assertIn("create_network_ContactNetwork", content)
        self.assertIn("class SEIRContactModel", content)
    
    def test_compile_spatial_example(self):
        """Compiler l'exemple spatial"""
        example_file = os.path.join(self.examples_dir, 'spatial_network.enl')
        
        if not os.path.exists(example_file):
            self.skipTest(f"Fichier d'exemple non trouvé: {example_file}")
        
        # Compiler vers Python
        output_file = os.path.join(self.test_dir, 'spatial_model.py')
        result = subprocess.run(
            [sys.executable, self.cli_path, 'compile', 
             example_file, '--target', 'python', '--output', output_file],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0,
                        f"Échec compilation spatial: {result.stderr}")
        
        # Vérifier que le fichier existe
        self.assertTrue(os.path.exists(output_file))
        
        # Vérifier le contenu
        with open(output_file, 'r') as f:
            content = f.read()
        
        self.assertIn("create_network_SpatialNetwork", content)
        self.assertIn("class MetapopulationSIRModel", content)
    
    def test_optimization_levels(self):
        """Tester les différents niveaux d'optimisation"""
        # Créer un fichier de test simple
        test_file = os.path.join(self.test_dir, 'test_optim.enl')
        with open(test_file, 'w') as f:
            f.write("""
            network TestNetwork(int n = 100) {
                int a = 10 + 20 + 30;
                int b = a * 2;
                int c = b / 2;
                int result = n + c;
                return result;
            }
            """)
        
        for opt_level in ['O0', 'O1', 'O2', 'O3']:
            output_file = os.path.join(self.test_dir, f'test_optim_{opt_level}.py')
            result = subprocess.run(
                [sys.executable, self.cli_path, 'compile',
                 test_file, '--target', 'python', '--output', output_file,
                 '--optimize', opt_level],
                capture_output=True,
                text=True
            )
            
            self.assertEqual(result.returncode, 0,
                            f"Échec avec optimisation {opt_level}: {result.stderr}")
            
            self.assertTrue(os.path.exists(output_file))
    
    def test_analyze_command(self):
        """Tester la commande analyze"""
        test_file = os.path.join(self.test_dir, 'test_analyze.enl')
        with open(test_file, 'w') as f:
            f.write("""
            network TestNetwork(int nodes = 100) {
                int edges = nodes * 5;
                return edges;
            }
            """)
        
        result = subprocess.run(
            [sys.executable, self.cli_path, 'analyze', test_file],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0,
                        f"Échec analyse: {result.stderr}")
        
        self.assertIn("Syntaxe correcte", result.stdout)
    
    def test_error_handling(self):
        """Tester la gestion des erreurs"""
        # Test 1: Fichier inexistant
        result = subprocess.run(
            [sys.executable, self.cli_path, 'compile', 'nonexistent.enl'],
            capture_output=True,
            text=True
        )
        
        self.assertNotEqual(result.returncode, 0)
        
        # Test 2: Syntaxe incorrecte
        bad_file = os.path.join(self.test_dir, 'bad_syntax.enl')
        with open(bad_file, 'w') as f:
            f.write("network Test { int x = ")  # Incomplet
        
        result = subprocess.run(
            [sys.executable, self.cli_path, 'compile', bad_file],
            capture_output=True,
            text=True
        )
        
        self.assertNotEqual(result.returncode, 0)
    
    def test_data_declaration(self):
        """Tester les déclarations de données"""
        # Créer un fichier CSV de test
        data_dir = os.path.join(self.test_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        csv_file = os.path.join(data_dir, 'test_data.csv')
        with open(csv_file, 'w') as f:
            f.write("date,cases,deaths\n2023-01-01,100,5\n2023-01-02,150,8\n")
        
        # Fichier avec déclaration de données
        test_file = os.path.join(self.test_dir, 'test_data.enl')
        with open(test_file, 'w') as f:
            f.write(f'''
            data TestData = CSV("{csv_file}", delimiter=",", header=1);
            
            model DataModel() {{
                int total_cases = 42;
                return total_cases;
            }}
            ''')
        
        # Compiler
        output_file = os.path.join(self.test_dir, 'data_model.py')
        result = subprocess.run(
            [sys.executable, self.cli_path, 'compile',
             test_file, '--target', 'python', '--output', output_file],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0,
                        f"Échec compilation avec données: {result.stderr}")
        
        # Vérifier que le code généré contient la fonction de chargement
        with open(output_file, 'r') as f:
            content = f.read()
        
        self.assertIn("def load_TestData_data", content)
        self.assertIn("pd.read_csv", content)
    
    def test_sensitivity_analysis(self):
        """Tester la génération d'analyse de sensibilité"""
        test_file = os.path.join(self.test_dir, 'test_sensitivity.enl')
        with open(test_file, 'w') as f:
            f.write("""
            model TestModel(float beta = 0.3, float gamma = 0.1) {
                float R0 = beta / gamma;
                sensitivity("beta");
                sensitivity("gamma");
                return R0;
            }
            """)
        
        # Compiler
        output_file = os.path.join(self.test_dir, 'sensitivity_model.py')
        result = subprocess.run(
            [sys.executable, self.cli_path, 'compile',
             test_file, '--target', 'python', '--output', output_file],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0,
                        f"Échec compilation sensibilité: {result.stderr}")
        
        # Vérifier le code généré
        with open(output_file, 'r') as f:
            content = f.read()
        
        self.assertIn("sensitivity_analysis", content)
        self.assertIn("sensitivity_analysis_beta", content)
    
    def test_R0_computation(self):
        """Tester la génération de calcul de R0"""
        test_file = os.path.join(self.test_dir, 'test_r0.enl')
        with open(test_file, 'w') as f:
            f.write("""
            model R0Model(float beta = 0.3, float gamma = 0.1) {
                compute R0;
                return beta / gamma;
            }
            """)
        
        # Compiler
        output_file = os.path.join(self.test_dir, 'r0_model.py')
        result = subprocess.run(
            [sys.executable, self.cli_path, 'compile',
             test_file, '--target', 'python', '--output', output_file],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0,
                        f"Échec compilation R0: {result.stderr}")
        
        # Vérifier le code généré
        with open(output_file, 'r') as f:
            content = f.read()
        
        self.assertIn("compute_R0", content)
    
    def test_forecast_generation(self):
        """Tester la génération de prévisions"""
        test_file = os.path.join(self.test_dir, 'test_forecast.enl')
        with open(test_file, 'w') as f:
            f.write("""
            model ForecastModel() {
                forecast 30;
                return 42;
            }
            """)
        
        # Compiler
        output_file = os.path.join(self.test_dir, 'forecast_model.py')
        result = subprocess.run(
            [sys.executable, self.cli_path, 'compile',
             test_file, '--target', 'python', '--output', output_file],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0,
                        f"Échec compilation forecast: {result.stderr}")
        
        # Vérifier le code généré
        with open(output_file, 'r') as f:
            content = f.read()
        
        self.assertIn("forecast_model", content)
    
    def test_complex_model_generation(self):
        """Tester la génération d'un modèle complexe"""
        test_file = os.path.join(self.test_dir, 'test_complex.enl')
        with open(test_file, 'w') as f:
            f.write("""
            model ComplexModel(
                float beta = 0.35,
                float gamma = 0.1,
                float mu = 0.005,
                float sigma = 0.2,
                int population = 10000
            ) {
                // États SEIR
                float S = population - 100;
                float E = 50;
                float I = 50;
                float R = 0;
                
                // Équations différentielles
                float dS = -beta * S * I / population + mu * (population - S);
                float dE = beta * S * I / population - sigma * E - mu * E;
                float dI = sigma * E - gamma * I - mu * I;
                float dR = gamma * I - mu * R;
                
                // Calculs avancés
                compute R0;
                
                // Matrice de nouvelle génération
                Matrix G = zeros(2, 2);
                
                // Analyse de sensibilité
                sensitivity("beta");
                sensitivity("gamma");
                sensitivity(["beta", "gamma"]);
                
                // Retourner les résultats
                return {
                    "states": [S, E, I, R],
                    "derivatives": [dS, dE, dI, dR],
                    "next_generation": G
                };
            }
            """)
        
        # Compiler
        output_file = os.path.join(self.test_dir, 'complex_model.py')
        result = subprocess.run(
            [sys.executable, self.cli_path, 'compile',
             test_file, '--target', 'python', '--output', output_file,
             '--optimize', 'O2'],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0,
                        f"Échec compilation complexe: {result.stderr}")
        
        # Vérifier le code généré
        with open(output_file, 'r') as f:
            content = f.read()
        
        # Vérifier les éléments clés
        self.assertIn("class ComplexModelModel", content)
        self.assertIn("compute_R0", content)
        self.assertIn("sensitivity_analysis", content)
        
        # Essayer de compiler le code Python
        try:
            compile(content, output_file, 'exec')
        except SyntaxError as e:
            self.fail(f"Code Python généré invalide: {e}")

if __name__ == '__main__':
    unittest.main()
