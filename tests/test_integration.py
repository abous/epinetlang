"""
Tests d'intégration pour EpiNetLang
"""

import unittest
import tempfile
import os
import subprocess
import sys
from pathlib import Path

class TestIntegration(unittest.TestCase):
    """Tests d'intégration du système complet"""
    
    def setUp(self):
        # Créer un répertoire temporaire pour les tests
        self.test_dir = tempfile.mkdtemp(prefix="epinetlang_test_")
        
        # Chemin vers l'exécutable CLI
        self.cli_path = os.path.join(os.path.dirname(__file__), "..", "src", "cli.py")
    
    def tearDown(self):
        # Nettoyer le répertoire temporaire
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_cli_help(self):
        """Tester l'affichage de l'aide du CLI"""
        result = subprocess.run(
            [sys.executable, self.cli_path, "--help"],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("EpiNetLang", result.stdout)
        self.assertIn("compile", result.stdout)
        self.assertIn("analyze", result.stdout)
    
    def test_cli_version(self):
        """Tester la commande version"""
        result = subprocess.run(
            [sys.executable, self.cli_path, "version"],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("EpiNetLang v1.0.0", result.stdout)
    
    def test_compile_simple_network(self):
        """Tester la compilation d'un réseau simple"""
        # Créer un fichier source de test
        source_file = os.path.join(self.test_dir, "test_network.enl")
        with open(source_file, "w") as f:
            f.write("""
            network TestNetwork(int nodes = 100) {
                int edges = nodes * 10;
                compute R0;
                return edges;
            }
            """)
        
        # Compiler vers Python
        output_file = os.path.join(self.test_dir, "test_network.py")
        result = subprocess.run(
            [sys.executable, self.cli_path, "compile", 
             source_file, "--target", "python", "--output", output_file],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0, 
                        f"Échec de la compilation: {result.stderr}")
        
        # Vérifier que le fichier de sortie existe
        self.assertTrue(os.path.exists(output_file))
        
        # Vérifier le contenu du fichier généré
        with open(output_file, "r") as f:
            generated_code = f.read()
        
        self.assertIn("def create_network_TestNetwork", generated_code)
        self.assertIn("compute_R0", generated_code)
    
    def test_compile_sir_model(self):
        """Tester la compilation d'un modèle SIR"""
        # Créer un fichier source de test
        source_file = os.path.join(self.test_dir, "sir_model.enl")
        with open(source_file, "w") as f:
            f.write("""
            model SIRModel(float beta = 0.3, float gamma = 0.1) {
                float S = 999;
                float I = 1;
                float R = 0;
                
                float dS = -beta * S * I / 1000;
                float dI = beta * S * I / 1000 - gamma * I;
                float dR = gamma * I;
                
                compute R0;
                sensitivity("beta");
                
                return { "S": S, "I": I, "R": R };
            }
            """)
        
        # Compiler vers Python avec optimisation
        output_file = os.path.join(self.test_dir, "sir_model.py")
        result = subprocess.run(
            [sys.executable, self.cli_path, "compile", 
             source_file, "--target", "python", "--output", output_file, "--optimize", "O2"],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0, 
                        f"Échec de la compilation: {result.stderr}")
        
        # Vérifier que le fichier peut être importé
        try:
            with open(output_file, "r") as f:
                code = f.read()
            compile(code, output_file, "exec")
        except SyntaxError as e:
            self.fail(f"Code Python généré invalide: {e}")
    
    def test_compile_to_julia(self):
        """Tester la compilation vers Julia"""
        source_file = os.path.join(self.test_dir, "test.jl.enl")
        with open(source_file, "w") as f:
            f.write("""
            network JuliaNetwork(int n = 50) {
                Graph net = create_random_network(n, 0.1);
                float r0 = compute_R0(net);
                return { "network": net, "R0": r0 };
            }
            """)
        
        output_file = os.path.join(self.test_dir, "test.jl")
        result = subprocess.run(
            [sys.executable, self.cli_path, "compile", 
             source_file, "--target", "julia", "--output", output_file],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists(output_file))
    
    def test_compile_to_cpp(self):
        """Tester la compilation vers C++"""
        source_file = os.path.join(self.test_dir, "test.cpp.enl")
        with open(source_file, "w") as f:
            f.write("""
            network CppNetwork(int nodes = 100) {
                int edges = nodes * 5;
                return edges;
            }
            """)
        
        output_base = os.path.join(self.test_dir, "test")
        result = subprocess.run(
            [sys.executable, self.cli_path, "compile", 
             source_file, "--target", "cpp", "--output", output_base],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        
        # Vérifier que les fichiers ont été créés
        header_file = output_base + ".hpp"
        source_file = output_base + ".cpp"
        
        self.assertTrue(os.path.exists(header_file))
        self.assertTrue(os.path.exists(source_file))
        
        # Vérifier le contenu du header
        with open(header_file, "r") as f:
            header_content = f.read()
        
        self.assertIn("class NetworkCppNetwork", header_content)
        self.assertIn("#ifndef EPINETLANG_GENERATED_HPP", header_content)
    
    def test_analyze_command(self):
        """Tester la commande analyze"""
        source_file = os.path.join(self.test_dir, "analyze_test.enl")
        with open(source_file, "w") as f:
            f.write("""
            network TestNetwork(int nodes = 100) {
                int edges = nodes * 10;
                return edges;
            }
            """)
        
        result = subprocess.run(
            [sys.executable, self.cli_path, "analyze", source_file],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Syntaxe correcte", result.stdout)
        self.assertIn("Sémantique correcte", result.stdout)
    
    def test_analyze_with_errors(self):
        """Tester l'analyse avec des erreurs"""
        source_file = os.path.join(self.test_dir, "error_test.enl")
        with open(source_file, "w") as f:
            f.write("""
            network TestNetwork() {
                // Variable non déclarée
                x = 10;
                
                // Type incorrect
                int y = "string";
                
                return y;
            }
            """)
        
        result = subprocess.run(
            [sys.executable, self.cli_path, "analyze", source_file],
            capture_output=True,
            text=True
        )
        
        # Le programme devrait détecter des erreurs
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("erreur", result.stdout.lower() or result.stderr.lower())
    
    def test_run_command_simple(self):
        """Tester la commande run avec un programme simple"""
        source_file = os.path.join(self.test_dir, "run_test.enl")
        with open(source_file, "w") as f:
            f.write("""
            network SimpleNetwork() {
                int result = 42;
                print("Le résultat est: " + result);
                return result;
            }
            """)
        
        result = subprocess.run(
            [sys.executable, self.cli_path, "run", source_file],
            capture_output=True,
            text=True,
            timeout=10  # Timeout pour éviter les boucles infinies
        )
        
        # Note: La commande run compile et exécute en Python
        # Vérifier que quelque chose a été exécuté
        self.assertIn("Le résultat est: 42", result.stdout or "")
    
    def test_optimization_levels(self):
        """Tester les différents niveaux d'optimisation"""
        source_file = os.path.join(self.test_dir, "optim_test.enl")
        with open(source_file, "w") as f:
            f.write("""
            network OptimTest(int n = 100) {
                // Code qui peut être optimisé
                int a = 10 + 20 + 30;
                int b = a * 2;
                int c = b / 2;
                
                // Code mort
                int dead = 1000;
                dead = dead * 2;
                
                // Code utile
                int result = n + c;
                
                return result;
            }
            """)
        
        # Tester différents niveaux d'optimisation
        for opt_level in ["O0", "O1", "O2", "O3"]:
            output_file = os.path.join(self.test_dir, f"optim_{opt_level}.py")
            result = subprocess.run(
                [sys.executable, self.cli_path, "compile", 
                 source_file, "--target", "python", "--output", output_file,
                 "--optimize", opt_level],
                capture_output=True,
                text=True
            )
            
            self.assertEqual(result.returncode, 0,
                            f"Échec avec optimisation {opt_level}: {result.stderr}")
            
            # Vérifier que le fichier a été créé
            self.assertTrue(os.path.exists(output_file))
    
    def test_complex_integration(self):
        """Test d'intégration complexe avec plusieurs fonctionnalités"""
        source_file = os.path.join(self.test_dir, "complex_test.enl")
        with open(source_file, "w") as f:
            f.write("""
            // Modèle épidémiologique complexe
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
                Matrix G = create_next_generation_matrix(beta, gamma, sigma, mu, S, population);
                
                // Analyse de sensibilité
                sensitivity("beta");
                sensitivity("gamma");
                sensitivity(["beta", "gamma"]);
                
                // Retourner les résultats
                return {
                    "states": [S, E, I, R],
                    "derivatives": [dS, dE, dI, dR],
                    "next_generation": G,
                    "parameters": {
                        "beta": beta,
                        "gamma": gamma,
                        "mu": mu,
                        "sigma": sigma
                    }
                };
            }
            
            // Analyse de scénarios
            analysis ScenarioAnalysis(Model model, float[] beta_values) {
                Matrix results;
                
                for (int i = 0; i < beta_values.size(); i++) {
                    float beta = beta_values[i];
                    
                    // Mettre à jour le paramètre
                    model.beta = beta;
                    
                    // Calculer R0
                    float r0 = compute_R0(model);
                    
                    // Simuler
                    Matrix simulation = model.simulate(200);
                    
                    // Stocker les résultats
                    results[i] = {
                        "beta": beta,
                        "R0": r0,
                        "simulation": simulation,
                        "peak_infections": max(simulation[:, 2])  // Colonne I
                    };
                }
                
                // Ajustement aux données
                data observed = CSV("data/observed.csv", delimiter=",");
                fit to observed;
                
                // Prévision
                forecast 60;
                
                return results;
            }
            """)
        
        # Compiler vers Python
        output_file = os.path.join(self.test_dir, "complex_model.py")
        result = subprocess.run(
            [sys.executable, self.cli_path, "compile", 
             source_file, "--target", "python", "--output", output_file,
             "--optimize", "O2", "--verbose"],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0,
                        f"Échec de la compilation complexe: {result.stderr}")
        
        # Vérifier que le fichier est valide
        try:
            with open(output_file, "r") as f:
                code = f.read()
            
            # Le code devrait être syntaxiquement correct
            compile(code, output_file, "exec")
            
            # Vérifier la présence de fonctionnalités clés
            self.assertIn("class ComplexModelModel", code)
            self.assertIn("compute_R0", code)
            self.assertIn("sensitivity_analysis", code)
            self.assertIn("def analyze_ScenarioAnalysis", code)
            
        except SyntaxError as e:
            self.fail(f"Code complexe généré invalide: {e}")
    
    def test_error_handling_integration(self):
        """Tester la gestion des erreurs en intégration"""
        # Test 1: Fichier inexistant
        result = subprocess.run(
            [sys.executable, self.cli_path, "compile", "nonexistent.enl"],
            capture_output=True,
            text=True
        )
        
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("non trouvé", result.stderr.lower())
        
        # Test 2: Code syntaxiquement incorrect
        bad_file = os.path.join(self.test_dir, "bad_syntax.enl")
        with open(bad_file, "w") as f:
            f.write("network Test { int x = ")  # Syntaxe incomplète
        
        result = subprocess.run(
            [sys.executable, self.cli_path, "compile", bad_file],
            capture_output=True,
            text=True
        )
        
        self.assertNotEqual(result.returncode, 0)
        
        # Test 3: Cible non supportée
        source_file = os.path.join(self.test_dir, "test_target.enl")
        with open(source_file, "w") as f:
            f.write("network Test() { return 1; }")
        
        result = subprocess.run(
            [sys.executable, self.cli_path, "compile", 
             source_file, "--target", "fortran"],  # Langage non supporté
            capture_output=True,
            text=True
        )
        
        self.assertNotEqual(result.returncode, 0)
    
    def test_data_import_integration(self):
        """Tester l'importation de données en intégration"""
        # Créer un fichier CSV de test
        data_dir = os.path.join(self.test_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        
        csv_file = os.path.join(data_dir, "test_data.csv")
        with open(csv_file, "w") as f:
            f.write("""date,cases,deaths,recovered
2023-01-01,100,5,50
2023-01-02,150,8,75
2023-01-03,200,12,100
""")
        
        # Créer le fichier source qui utilise ces données
        source_file = os.path.join(self.test_dir, "data_test.enl")
        with open(source_file, "w") as f:
            f.write(f'''
            data TestData = CSV("{csv_file}", delimiter=",", header=1);
            
            model DataDrivenModel() {{
                Data data = TestData;
                int total_cases = data.aggregate("sum", "cases");
                float avg_growth = data.filter("cases > 0").mean("daily_growth");
                
                print("Total cases: " + total_cases);
                print("Average growth: " + avg_growth);
                
                return {{ "total_cases": total_cases, "avg_growth": avg_growth }};
            }}
            ''')
        
        # Compiler
        output_file = os.path.join(self.test_dir, "data_model.py")
        result = subprocess.run(
            [sys.executable, self.cli_path, "compile", 
             source_file, "--target", "python", "--output", output_file],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        
        # Vérifier que le code généré contient la logique de chargement CSV
        with open(output_file, "r") as f:
            code = f.read()
        
        self.assertIn("pd.read_csv", code)
        self.assertIn("def load_TestData_data", code)

if __name__ == '__main__':
    unittest.main()