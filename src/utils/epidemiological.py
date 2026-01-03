"""
Utilitaires épidémiologiques pour EpiNetLang
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from scipy import stats, optimize, integrate

class EpidemiologicalCalculations:
    """Calculs épidémiologiques"""
    
    @staticmethod
    def calculate_R0(beta: float, 
                    gamma: float, 
                    mu: float = 0.0,
                    sigma: Optional[float] = None) -> float:
        """
        Calculer le nombre de reproduction de base R0
        
        Args:
            beta: Taux de transmission
            gamma: Taux de guérison
            mu: Taux de mortalité (défaut: 0)
            sigma: Taux de progression vers l'état infectieux (pour SEIR)
        
        Returns:
            Valeur de R0
        """
        if sigma is not None:
            # Modèle SEIR: R0 = beta * sigma / ((sigma + mu) * (gamma + mu))
            return beta * sigma / ((sigma + mu) * (gamma + mu))
        else:
            # Modèle SIR: R0 = beta / (gamma + mu)
            return beta / (gamma + mu)
    
    @staticmethod
    def calculate_herd_immunity_threshold(R0: float) -> float:
        """
        Calculer le seuil d'immunité collective
        
        Args:
            R0: Nombre de reproduction de base
        
        Returns:
            Proportion de la population qui doit être immunisée
        """
        if R0 <= 1:
            return 0.0
        return 1 - (1 / R0)
    
    @staticmethod
    def calculate_doubling_time(growth_rate: float) -> Optional[float]:
        """
        Calculer le temps de doublement
        
        Args:
            growth_rate: Taux de croissance journalier
        
        Returns:
            Temps de doublement en jours, ou None si non applicable
        """
        if growth_rate <= 0:
            return None
        return np.log(2) / growth_rate
    
    @staticmethod
    def estimate_growth_rate_from_data(cases: List[float], 
                                      method: str = 'exponential') -> Dict:
        """
        Estimer le taux de croissance à partir des données de cas
        
        Args:
            cases: Liste des cas cumulés
            method: Méthode d'estimation ('exponential' ou 'linear')
        
        Returns:
            Dictionnaire avec les résultats de l'estimation
        """
        if len(cases) < 3:
            raise ValueError("Au moins 3 points de données sont requis")
        
        # Convertir en array numpy
        y = np.array(cases)
        x = np.arange(len(y))
        
        # Filtrer les valeurs nulles ou négatives pour le log
        mask = y > 0
        if not mask.any():
            raise ValueError("Aucune valeur positive dans les données")
        
        if method == 'exponential':
            # Ajustement exponentiel: y = a * exp(b * x)
            log_y = np.log(y[mask])
            x_filt = x[mask]
            
            # Régression linéaire sur les logarithmes
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_filt, log_y)
            
            return {
                'growth_rate': slope,
                'doubling_time': np.log(2) / slope if slope > 0 else None,
                'R_squared': r_value ** 2,
                'intercept': intercept,
                'method': 'exponential'
            }
        
        elif method == 'linear':
            # Ajustement linéaire sur les nouveaux cas
            new_cases = np.diff(y)
            if len(new_cases) < 2:
                raise ValueError("Pas assez de données pour l'ajustement linéaire")
            
            x_new = x[1:]
            mask_new = new_cases > 0
            
            if not mask_new.any():
                raise ValueError("Aucun nouveau cas positif")
            
            log_new = np.log(new_cases[mask_new])
            x_new_filt = x_new[mask_new]
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_new_filt, log_new)
            
            return {
                'growth_rate': slope,
                'doubling_time': np.log(2) / slope if slope > 0 else None,
                'R_squared': r_value ** 2,
                'intercept': intercept,
                'method': 'linear'
            }
        
        else:
            raise ValueError(f"Méthode non supportée: {method}")
    
    @staticmethod
    def simulate_SIR(S0: float, I0: float, R0: float,
                    beta: float, gamma: float, 
                    days: int = 100) -> Dict[str, np.ndarray]:
        """
        Simuler un modèle SIR
        
        Args:
            S0: Susceptibles initiaux
            I0: Infectés initiaux
            R0: Rétablis initiaux
            beta: Taux de transmission
            gamma: Taux de guérison
            days: Nombre de jours à simuler
        
        Returns:
            Dictionnaire avec les séries temporelles
        """
        N = S0 + I0 + R0
        
        def sir_equations(t, y):
            S, I, R = y
            dS = -beta * S * I / N
            dI = beta * S * I / N - gamma * I
            dR = gamma * I
            return [dS, dI, dR]
        
        # Conditions initiales
        y0 = [S0, I0, R0]
        t_span = (0, days)
        t_eval = np.arange(0, days + 1)
        
        # Résoudre les équations différentielles
        from scipy.integrate import solve_ivp
        solution = solve_ivp(sir_equations, t_span, y0, t_eval=t_eval)
        
        return {
            'time': solution.t,
            'S': solution.y[0],
            'I': solution.y[1],
            'R': solution.y[2],
            'total_cases': N - solution.y[0],  # Cas cumulés
            'new_cases': -np.diff(solution.y[0])  # Nouveaux cas par jour
        }
    
    @staticmethod
    def calculate_effective_reproduction_number(cases: List[float],
                                              serial_interval: float = 4.0,
                                              window: int = 7) -> np.ndarray:
        """
        Calculer le nombre de reproduction effectif Rt
        
        Args:
            cases: Liste des nouveaux cas par jour
            serial_interval: Intervalle série moyen (défaut: 4 jours)
            window: Fenêtre de lissage (défaut: 7 jours)
        
        Returns:
            Array des valeurs de Rt
        """
        cases = np.array(cases, dtype=float)
        
        if len(cases) < window + 1:
            raise ValueError(f"Au moins {window + 1} jours de données sont requis")
        
        # Lissage des cas
        smoothed = np.convolve(cases, np.ones(window)/window, mode='valid')
        
        # Calcul de Rt selon la méthode de Cori
        Rt = np.zeros_like(smoothed)
        for t in range(1, len(smoothed)):
            if smoothed[t-1] > 0:
                Rt[t] = smoothed[t] / smoothed[t-1]
            else:
                Rt[t] = np.nan
        
        # Ajustement pour l'intervalle série
        if serial_interval != 1.0:
            Rt = np.power(Rt, serial_interval)
        
        return Rt
    
    @staticmethod
    def sensitivity_analysis(model_func,
                           param_names: List[str],
                           baseline_values: Dict[str, float],
                           ranges: Dict[str, Tuple[float, float]],
                           n_points: int = 10) -> Dict:
        """
        Analyse de sensibilité d'un modèle
        
        Args:
            model_func: Fonction du modèle
            param_names: Noms des paramètres
            baseline_values: Valeurs de référence des paramètres
            ranges: Plages de variation pour chaque paramètre
            n_points: Nombre de points par paramètre
        
        Returns:
            Résultats de l'analyse de sensibilité
        """
        results = {}
        
        for param in param_names:
            if param not in baseline_values or param not in ranges:
                continue
            
            # Générer les valeurs du paramètre
            param_values = np.linspace(ranges[param][0], ranges[param][1], n_points)
            model_outputs = []
            
            # Évaluer le modèle pour chaque valeur
            for value in param_values:
                # Créer une copie des valeurs de référence
                params = baseline_values.copy()
                params[param] = value
                
                # Exécuter le modèle
                output = model_func(**params)
                model_outputs.append(output)
            
            # Calculer les mesures de sensibilité
            outputs_array = np.array(model_outputs)
            
            # Indice de sensibilité normalisé
            if len(outputs_array) > 1:
                sensitivity_index = np.std(outputs_array) / np.mean(outputs_array)
            else:
                sensitivity_index = 0.0
            
            results[param] = {
                'values': param_values.tolist(),
                'outputs': model_outputs,
                'sensitivity_index': float(sensitivity_index),
                'elasticity': float(sensitivity_index * baseline_values[param] / np.mean(outputs_array))
            }
        
        # Classer les paramètres par sensibilité
        sorted_params = sorted(results.items(), 
                              key=lambda x: x[1]['sensitivity_index'], 
                              reverse=True)
        
        results['ranking'] = [param for param, _ in sorted_params]
        
        return results
    
    @staticmethod
    def fit_model_to_data(model_func,
                         data: np.ndarray,
                         param_names: List[str],
                         initial_guess: Dict[str, float],
                         bounds: Optional[Dict[str, Tuple[float, float]]] = None) -> Dict:
        """
        Ajuster un modèle à des données observées
        
        Args:
            model_func: Fonction du modèle
            data: Données observées
            param_names: Noms des paramètres à ajuster
            initial_guess: Valeurs initiales des paramètres
            bounds: Bornes pour les paramètres
        
        Returns:
            Résultats de l'ajustement
        """
        def error_function(params):
            """Fonction d'erreur à minimiser"""
            try:
                predicted = model_func(**params)
                # Erreur quadratique moyenne
                error = np.mean((predicted - data) ** 2)
                return error
            except:
                return float('inf')
        
        # Préparer les bornes
        if bounds is None:
            bounds_list = [(0, None) for _ in param_names]
        else:
            bounds_list = [bounds.get(param, (0, None)) for param in param_names]
        
        # Fonction wrapper pour scipy.optimize
        def wrapper(x):
            params = dict(zip(param_names, x))
            return error_function(params)
        
        # Point initial
        x0 = [initial_guess[param] for param in param_names]
        
        # Minimisation
        result = optimize.minimize(wrapper, x0, bounds=bounds_list, method='L-BFGS-B')
        
        # Résultats
        fitted_params = dict(zip(param_names, result.x))
        
        return {
            'fitted_parameters': fitted_params,
            'error': float(result.fun),
            'success': result.success,
            'message': result.message,
            'predicted': model_func(**fitted_params)
        }