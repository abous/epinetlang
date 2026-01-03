"""
Chargeur de données pour EpiNetLang
"""

import pandas as pd
import numpy as np
import json
import sqlite3
import csv
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

class DataLoader:
    """Chargeur de données pour différents formats"""
    
    @staticmethod
    def load_csv(filepath: str, **kwargs) -> pd.DataFrame:
        """Charger des données depuis un fichier CSV"""
        try:
            # Paramètres par défaut
            default_kwargs = {
                'delimiter': ',',
                'header': 'infer',
                'encoding': 'utf-8'
            }
            default_kwargs.update(kwargs)
            
            return pd.read_csv(filepath, **default_kwargs)
        except Exception as e:
            raise ValueError(f"Erreur lors du chargement du CSV {filepath}: {e}")
    
    @staticmethod
    def load_json(filepath: str, **kwargs) -> Union[Dict, List]:
        """Charger des données depuis un fichier JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise ValueError(f"Erreur lors du chargement du JSON {filepath}: {e}")
    
    @staticmethod
    def load_sql(connection_string: str, query: str, **kwargs) -> pd.DataFrame:
        """Charger des données depuis une base de données SQL"""
        try:
            # Pour SQLite
            if connection_string.endswith('.db') or connection_string.endswith('.sqlite'):
                conn = sqlite3.connect(connection_string)
                df = pd.read_sql_query(query, conn)
                conn.close()
                return df
            else:
                # Pour d'autres bases de données, on pourrait utiliser SQLAlchemy
                raise NotImplementedError("Seul SQLite est supporté pour l'instant")
        except Exception as e:
            raise ValueError(f"Erreur lors du chargement SQL: {e}")
    
    @staticmethod
    def create_network_from_data(data: pd.DataFrame, 
                                source_col: str = 'source',
                                target_col: str = 'target',
                                weight_col: Optional[str] = None) -> Dict:
        """Créer un réseau à partir de données de liens"""
        try:
            import networkx as nx
            
            if weight_col:
                edges = list(zip(data[source_col], data[target_col], data[weight_col]))
                G = nx.Graph()
                G.add_weighted_edges_from(edges)
            else:
                edges = list(zip(data[source_col], data[target_col]))
                G = nx.Graph()
                G.add_edges_from(edges)
            
            # Calculer les métriques du réseau
            metrics = {
                'nodes': G.number_of_nodes(),
                'edges': G.number_of_edges(),
                'density': nx.density(G),
                'average_degree': sum(dict(G.degree()).values()) / G.number_of_nodes()
            }
            
            # Ajouter les attributs des nœuds si disponibles
            node_attributes = {}
            for col in data.columns:
                if col not in [source_col, target_col, weight_col]:
                    # Essayer d'associer les attributs aux nœuds
                    pass
            
            return {
                'graph': G,
                'metrics': metrics,
                'adjacency_matrix': nx.to_numpy_array(G)
            }
        except ImportError:
            raise ImportError("NetworkX est requis pour créer des réseaux")
        except Exception as e:
            raise ValueError(f"Erreur lors de la création du réseau: {e}")
    
    @staticmethod
    def prepare_epidemic_data(data: pd.DataFrame,
                             date_col: str = 'date',
                             case_col: str = 'cases',
                             population_col: Optional[str] = None) -> Dict:
        """Préparer des données épidémiologiques pour l'analyse"""
        try:
            # Assurer que la colonne de date est au bon format
            if date_col in data.columns:
                data[date_col] = pd.to_datetime(data[date_col])
                data = data.sort_values(date_col)
            
            # Calculer les nouvelles infections quotidiennes
            if case_col in data.columns:
                data['new_cases'] = data[case_col].diff().fillna(0)
                
                # Calculer le taux de croissance
                data['growth_rate'] = data['new_cases'].pct_change().fillna(0)
                
                # Lissage sur 7 jours
                data['new_cases_7day_avg'] = data['new_cases'].rolling(7).mean()
            
            # Calculer l'incidence si la population est disponible
            if population_col and population_col in data.columns:
                data['incidence'] = data[case_col] / data[population_col] * 100000
            
            return {
                'data': data,
                'summary': {
                    'total_cases': data[case_col].sum() if case_col in data.columns else None,
                    'peak_cases': data[case_col].max() if case_col in data.columns else None,
                    'start_date': data[date_col].min() if date_col in data.columns else None,
                    'end_date': data[date_col].max() if date_col in data.columns else None
                }
            }
        except Exception as e:
            raise ValueError(f"Erreur lors de la préparation des données: {e}")
    
    @staticmethod
    def export_to_csv(data: Union[pd.DataFrame, Dict], 
                     filepath: str, 
                     **kwargs) -> None:
        """Exporter des données vers CSV"""
        try:
            if isinstance(data, pd.DataFrame):
                data.to_csv(filepath, **kwargs)
            elif isinstance(data, Dict):
                # Convertir le dictionnaire en DataFrame
                df = pd.DataFrame(data)
                df.to_csv(filepath, **kwargs)
            else:
                raise ValueError("Type de données non supporté pour l'export CSV")
        except Exception as e:
            raise ValueError(f"Erreur lors de l'export vers CSV: {e}")
    
    @staticmethod
    def merge_datasets(datasets: List[pd.DataFrame], 
                      on: str, 
                      how: str = 'inner') -> pd.DataFrame:
        """Fusionner plusieurs jeux de données"""
        try:
            if len(datasets) < 2:
                raise ValueError("Au moins deux jeux de données sont requis")
            
            merged = datasets[0]
            for i in range(1, len(datasets)):
                merged = pd.merge(merged, datasets[i], on=on, how=how)
            
            return merged
        except Exception as e:
            raise ValueError(f"Erreur lors de la fusion des jeux de données: {e}")