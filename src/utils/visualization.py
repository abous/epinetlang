"""
Visualisation pour EpiNetLang
"""

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import networkx as nx

class EpiNetVisualizer:
    """Visualisation pour les modèles épidémiologiques"""
    
    def __init__(self, style: str = 'default'):
        """
        Initialiser le visualiseur
        
        Args:
            style: Style des graphiques ('default', 'seaborn', 'ggplot', etc.)
        """
        self.style = style
        self._setup_style()
    
    def _setup_style(self):
        """Configurer le style des graphiques"""
        if self.style == 'seaborn':
            plt.style.use('seaborn-v0_8')
        elif self.style == 'ggplot':
            plt.style.use('ggplot')
        elif self.style == 'dark':
            plt.style.use('dark_background')
        else:
            plt.style.use('default')
        
        # Configuration générale
        matplotlib.rcParams['figure.figsize'] = [10, 6]
        matplotlib.rcParams['font.size'] = 12
        matplotlib.rcParams['axes.titlesize'] = 14
        matplotlib.rcParams['axes.labelsize'] = 12
    
    def plot_epidemic_curves(self,
                           time: np.ndarray,
                           compartments: Dict[str, np.ndarray],
                           title: str = "Courbes épidémiques",
                           save_path: Optional[str] = None) -> plt.Figure:
        """
        Tracer les courbes épidémiques
        
        Args:
            time: Vecteur temps
            compartments: Dictionnaire des compartiments
            title: Titre du graphique
            save_path: Chemin pour sauvegarder la figure
        
        Returns:
            Figure matplotlib
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Tracer chaque compartiment
        colors = plt.cm.Set2(np.linspace(0, 1, len(compartments)))
        
        for (name, values), color in zip(compartments.items(), colors):
            ax.plot(time, values, label=name, linewidth=2, color=color)
        
        # Configuration du graphique
        ax.set_xlabel('Temps (jours)')
        ax.set_ylabel('Nombre d\'individus')
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Ajouter des annotations
        total_population = sum(values[-1] for values in compartments.values())
        ax.text(0.02, 0.98, f'Population totale: {total_population:.0f}',
                transform=ax.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_network(self,
                    graph: nx.Graph,
                    node_colors: Optional[Dict] = None,
                    node_sizes: Optional[Dict] = None,
                    title: str = "Réseau épidémiologique",
                    layout: str = 'spring',
                    save_path: Optional[str] = None) -> plt.Figure:
        """
        Visualiser un réseau
        
        Args:
            graph: Graphe NetworkX
            node_colors: Couleurs des nœuds par statut
            node_sizes: Tailles des nœuds
            title: Titre du graphique
            layout: Type de layout ('spring', 'circular', 'random', 'kamada_kawai')
            save_path: Chemin pour sauvegarder la figure
        
        Returns:
            Figure matplotlib
        """
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Choisir le layout
        if layout == 'spring':
            pos = nx.spring_layout(graph, seed=42)
        elif layout == 'circular':
            pos = nx.circular_layout(graph)
        elif layout == 'random':
            pos = nx.random_layout(graph, seed=42)
        elif layout == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(graph)
        else:
            pos = nx.spring_layout(graph, seed=42)
        
        # Définir les couleurs par défaut
        if node_colors is None:
            node_colors = ['skyblue' for _ in graph.nodes()]
        
        # Définir les tailles par défaut
        if node_sizes is None:
            degrees = dict(graph.degree())
            node_sizes = [300 + 10 * degrees[node] for node in graph.nodes()]
        
        # Dessiner le réseau
        nx.draw_networkx_nodes(graph, pos, 
                              node_color=node_colors, 
                              node_size=node_sizes,
                              alpha=0.8,
                              ax=ax)
        
        nx.draw_networkx_edges(graph, pos, 
                              alpha=0.3,
                              width=1,
                              ax=ax)
        
        # Dessiner les labels si le réseau n'est pas trop grand
        if len(graph.nodes()) <= 50:
            nx.draw_networkx_labels(graph, pos, 
                                   font_size=8,
                                   ax=ax)
        
        # Métriques du réseau
        metrics = {
            'Nœuds': graph.number_of_nodes(),
            'Arêtes': graph.number_of_edges(),
            'Densité': f"{nx.density(graph):.4f}",
            'Coefficient de clustering': f"{nx.average_clustering(graph):.3f}"
        }
        
        # Ajouter les métriques
        metrics_text = '\n'.join([f'{k}: {v}' for k, v in metrics.items()])
        ax.text(0.02, 0.02, metrics_text,
                transform=ax.transAxes, verticalalignment='bottom',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.set_title(title)
        ax.axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_degree_distribution(self,
                               graph: nx.Graph,
                               loglog: bool = False,
                               title: str = "Distribution des degrés",
                               save_path: Optional[str] = None) -> plt.Figure:
        """
        Tracer la distribution des degrés du réseau
        
        Args:
            graph: Graphe NetworkX
            loglog: Utiliser une échelle log-log
            title: Titre du graphique
            save_path: Chemin pour sauvegarder la figure
        
        Returns:
            Figure matplotlib
        """
        degrees = [d for _, d in graph.degree()]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if loglog:
            # Histogramme en échelle log-log
            bins = np.logspace(np.log10(min(degrees)), 
                              np.log10(max(degrees)), 
                              20)
            ax.hist(degrees, bins=bins, alpha=0.7, edgecolor='black')
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.set_xlabel('Degré (échelle logarithmique)')
            ax.set_ylabel('Fréquence (échelle logarithmique)')
        else:
            # Histogramme standard
            ax.hist(degrees, bins=20, alpha=0.7, edgecolor='black')
            ax.set_xlabel('Degré')
            ax.set_ylabel('Fréquence')
        
        # Statistiques
        stats_text = f"""
        Degré moyen: {np.mean(degrees):.2f}
        Écart-type: {np.std(degrees):.2f}
        Degré max: {max(degrees)}
        Degré min: {min(degrees)}
        """
        
        ax.text(0.02, 0.98, stats_text,
                transform=ax.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_sensitivity_analysis(self,
                                results: Dict,
                                title: str = "Analyse de sensibilité",
                                save_path: Optional[str] = None) -> plt.Figure:
        """
        Visualiser les résultats d'une analyse de sensibilité
        
        Args:
            results: Résultats de l'analyse de sensibilité
            title: Titre du graphique
            save_path: Chemin pour sauvegarder la figure
        
        Returns:
            Figure matplotlib
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        ax1, ax2, ax3, ax4 = axes.flatten()
        
        # 1. Indices de sensibilité
        params = list(results.keys())
        if 'ranking' in params:
            params.remove('ranking')
        
        sensitivity_indices = [results[param]['sensitivity_index'] for param in params]
        elasticities = [results[param]['elasticity'] for param in params]
        
        x = np.arange(len(params))
        width = 0.35
        
        ax1.bar(x - width/2, sensitivity_indices, width, label='Indice de sensibilité', alpha=0.7)
        ax1.bar(x + width/2, elasticities, width, label='Élasticité', alpha=0.7)
        ax1.set_xlabel('Paramètres')
        ax1.set_ylabel('Valeur')
        ax1.set_title('Indices de sensibilité')
        ax1.set_xticks(x)
        ax1.set_xticklabels(params, rotation=45)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Courbes de réponse
        for param in params[:4]:  # Limiter à 4 paramètres pour la lisibilité
            values = results[param]['values']
            outputs = results[param]['outputs']
            ax2.plot(values, outputs, 'o-', label=param, linewidth=2, markersize=4)
        
        ax2.set_xlabel('Valeur du paramètre')
        ax2.set_ylabel('Sortie du modèle')
        ax2.set_title('Courbes de réponse')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Diagramme en radar des sensibilités
        if len(params) >= 3:
            angles = np.linspace(0, 2 * np.pi, len(params), endpoint=False).tolist()
            sensitivity_indices_closed = sensitivity_indices + [sensitivity_indices[0]]
            angles_closed = angles + [angles[0]]
            
            ax3 = plt.subplot(2, 2, 3, projection='polar')
            ax3.plot(angles_closed, sensitivity_indices_closed, 'o-', linewidth=2)
            ax3.fill(angles_closed, sensitivity_indices_closed, alpha=0.25)
            ax3.set_xticks(angles)
            ax3.set_xticklabels(params)
            ax3.set_title('Diagramme en radar des sensibilités')
            ax3.grid(True)
        else:
            ax3.axis('off')
            ax3.text(0.5, 0.5, 'Diagramme radar nécessite\nau moins 3 paramètres',
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=ax3.transAxes)
        
        # 4. Heatmap de corrélation (si multivarié)
        ax4.text(0.5, 0.5, 'Heatmap de corrélation\n(implémentation à compléter)',
                horizontalalignment='center',
                verticalalignment='center',
                transform=ax4.transAxes)
        ax4.set_title('Corrélations entre paramètres')
        ax4.axis('off')
        
        plt.suptitle(title, fontsize=16)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_R0_analysis(self,
                        R0_values: np.ndarray,
                        time: Optional[np.ndarray] = None,
                        threshold: float = 1.0,
                        title: str = "Évolution de Rₜ",
                        save_path: Optional[str] = None) -> plt.Figure:
        """
        Tracer l'évolution du nombre de reproduction effectif
        
        Args:
            R0_values: Valeurs de Rₜ
            time: Vecteur temps (optionnel)
            threshold: Seuil critique (défaut: 1.0)
            title: Titre du graphique
            save_path: Chemin pour sauvegarder la figure
        
        Returns:
            Figure matplotlib
        """
        if time is None:
            time = np.arange(len(R0_values))
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Tracer Rₜ
        ax.plot(time, R0_values, 'b-', linewidth=2, label='Rₜ')
        
        # Ligne de seuil
        ax.axhline(y=threshold, color='r', linestyle='--', alpha=0.7, 
                  label=f'Seuil (Rₜ = {threshold})')
        
        # Remplir les zones
        ax.fill_between(time, R0_values, threshold, 
                       where=(R0_values >= threshold),
                       color='red', alpha=0.2, label='Rₜ ≥ 1')
        
        ax.fill_between(time, R0_values, threshold,
                       where=(R0_values < threshold),
                       color='green', alpha=0.2, label='Rₜ < 1')
        
        # Statistiques
        mean_R0 = np.nanmean(R0_values)
        max_R0 = np.nanmax(R0_values)
        min_R0 = np.nanmin(R0_values)
        
        stats_text = f"""
        Rₜ moyen: {mean_R0:.2f}
        Rₜ max: {max_R0:.2f}
        Rₜ min: {min_R0:.2f}
        """
        
        ax.text(0.02, 0.98, stats_text,
                transform=ax.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        ax.set_xlabel('Temps (jours)')
        ax.set_ylabel('Rₜ')
        ax.set_title(title)
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_forecast_comparison(self,
                               observed: np.ndarray,
                               forecast: np.ndarray,
                               confidence_intervals: Optional[Tuple[np.ndarray, np.ndarray]] = None,
                               title: str = "Prévision vs Observations",
                               save_path: Optional[str] = None) -> plt.Figure:
        """
        Comparer les prévisions aux observations
        
        Args:
            observed: Données observées
            forecast: Prévisions
            confidence_intervals: Intervalles de confiance (lower, upper)
            title: Titre du graphique
            save_path: Chemin pour sauvegarder la figure
        
        Returns:
            Figure matplotlib
        """
        time_obs = np.arange(len(observed))
        time_fore = np.arange(len(observed), len(observed) + len(forecast))
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Observations
        ax.plot(time_obs, observed, 'bo-', linewidth=2, markersize=4, label='Observations')
        
        # Prévisions
        ax.plot(time_fore, forecast, 'r-', linewidth=2, label='Prévisions')
        
        # Intervalles de confiance
        if confidence_intervals is not None:
            lower, upper = confidence_intervals
            ax.fill_between(time_fore, lower, upper, color='red', alpha=0.2, label='Intervalle de confiance 95%')
        
        # Ligne verticale séparant observations et prévisions
        ax.axvline(x=len(observed) - 0.5, color='gray', linestyle='--', alpha=0.7)
        
        ax.text(len(observed) / 2, ax.get_ylim()[1] * 0.9, 'Période\nd\'observation',
                horizontalalignment='center',
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='blue', alpha=0.1))
        
        ax.text(len(observed) + len(forecast) / 2, ax.get_ylim()[1] * 0.9, 'Période de\nprévision',
                horizontalalignment='center',
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='red', alpha=0.1))
        
        # Métriques d'erreur (si nous avons des observations pour la période de prévision)
        if len(observed) > len(forecast):
            obs_forecast = observed[-len(forecast):]
            mae = np.mean(np.abs(forecast - obs_forecast))
            rmse = np.sqrt(np.mean((forecast - obs_forecast) ** 2))
            
            metrics_text = f"""
            MAE: {mae:.2f}
            RMSE: {rmse:.2f}
            """
            
            ax.text(0.02, 0.98, metrics_text,
                    transform=ax.transAxes, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        ax.set_xlabel('Temps (jours)')
        ax.set_ylabel('Nombre de cas')
        ax.set_title(title)
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def create_dashboard(self,
                        simulation_results: Dict,
                        network: Optional[nx.Graph] = None,
                        title: str = "Tableau de bord épidémiologique",
                        save_path: Optional[str] = None) -> plt.Figure:
        """
        Créer un tableau de bord complet
        
        Args:
            simulation_results: Résultats de simulation
            network: Réseau (optionnel)
            title: Titre du dashboard
            save_path: Chemin pour sauvegarder la figure
        
        Returns:
            Figure matplotlib
        """
        fig = plt.figure(figsize=(20, 12))
        
        # Disposition des sous-graphiques
        if network is not None:
            gs = fig.add_gridspec(3, 3)
            
            # 1. Courbes épidémiques (en haut à gauche, sur 2 colonnes)
            ax1 = fig.add_subplot(gs[0, :2])
            
            # 2. Réseau (en haut à droite)
            ax2 = fig.add_subplot(gs[0, 2])
            
            # 3. Distribution des degrés (milieu gauche)
            ax3 = fig.add_subplot(gs[1, 0])
            
            # 4. Évolution de Rₜ (milieu centre)
            ax4 = fig.add_subplot(gs[1, 1])
            
            # 5. Analyse de sensibilité (milieu droite)
            ax5 = fig.add_subplot(gs[1, 2])
            
            # 6. Statistiques (bas, sur 3 colonnes)
            ax6 = fig.add_subplot(gs[2, :])
        else:
            gs = fig.add_gridspec(2, 3)
            
            # 1. Courbes épidémiques
            ax1 = fig.add_subplot(gs[0, :])
            
            # 2. Évolution de Rₜ
            ax2 = fig.add_subplot(gs[1, 0])
            
            # 3. Distribution temporelle
            ax3 = fig.add_subplot(gs[1, 1])
            
            # 4. Statistiques
            ax4 = fig.add_subplot(gs[1, 2])
        
        # Remplir les graphiques avec les données
        # (Cette partie serait remplie avec les données spécifiques)
        
        plt.suptitle(title, fontsize=20, y=0.98)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig