"""
Employee Grouping System
-----------------------
Ein intelligentes System zur dynamischen Gruppierung und Analyse von Mitarbeiterdaten.
Verwendet fortschrittliche Machine Learning Techniken für Clustering und Klassifizierung.

Features:
- Dynamisches Clustering basierend auf verschiedenen Mitarbeiterattributen
- Zeitreihenanalyse für Entwicklungstrends
- Automatische Feature-Wichtigkeits-Erkennung
- Anpassungsfähige Gruppierungsstrategien
- Automatische Reportgenerierung
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
import joblib
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime
import json

class EmployeeGroupingSystem:
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialisiert das Employee Grouping System.
        
        Args:
            config_path: Pfad zur Konfigurationsdatei (optional)
        """
        self.logger = self._setup_logging()
        self.config = self._load_config(config_path)
        self.scalers = {}
        self.encoders = {}
        self.models = {}
        self.feature_importance = {}
        
    def _setup_logging(self) -> logging.Logger:
        """Konfiguriert das Logging-System."""
        logger = logging.getLogger('EmployeeGroupingSystem')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler('employee_grouping.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Lädt die Konfigurationsdatei oder verwendet Standardeinstellungen."""
        default_config = {
            'clustering_methods': ['kmeans', 'dbscan'],
            'feature_weights': {
                'performance': 1.5,
                'experience': 1.2,
                'skills': 1.3,
                'department': 1.0
            },
            'min_group_size': 3,
            'max_group_size': 50,
            'update_frequency': 'weekly'
        }
        
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    return {**default_config, **json.load(f)}
            except Exception as e:
                self.logger.warning(f"Konnte Konfigurationsdatei nicht laden: {e}")
                
        return default_config

    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Bereitet die Rohdaten für die Analyse vor.
        
        Args:
            data: DataFrame mit Mitarbeiterdaten
            
        Returns:
            Vorverarbeitete Daten als DataFrame
        """
        processed_data = data.copy()
        
        # Behandlung fehlender Werte
        for col in processed_data.columns:
            if processed_data[col].dtype in ['int64', 'float64']:
                processed_data[col].fillna(processed_data[col].median(), inplace=True)
            else:
                processed_data[col].fillna(processed_data[col].mode()[0], inplace=True)
        
        # Feature Engineering
        if 'hire_date' in processed_data.columns:
            processed_data['tenure'] = (
                pd.Timestamp.now() - pd.to_datetime(processed_data['hire_date'])
            ).dt.days / 365

        # Kategorische Variablen encodieren
        categorical_columns = processed_data.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if col not in self.encoders:
                self.encoders[col] = LabelEncoder()
            processed_data[col] = self.encoders[col].fit_transform(processed_data[col])

        # Numerische Features skalieren
        numeric_columns = processed_data.select_dtypes(include=['int64', 'float64']).columns
        if 'numeric_scaler' not in self.scalers:
            self.scalers['numeric_scaler'] = StandardScaler()
            processed_data[numeric_columns] = self.scalers['numeric_scaler'].fit_transform(
                processed_data[numeric_columns]
            )
        
        return processed_data

    def identify_groups(self, data: pd.DataFrame, method: str = 'auto') -> Dict:
        """
        Identifiziert optimale Mitarbeitergruppen basierend auf verschiedenen Merkmalen.
        
        Args:
            data: Vorverarbeitete Mitarbeiterdaten
            method: Clustering-Methode ('auto', 'kmeans', 'dbscan')
            
        Returns:
            Dictionary mit Gruppenzuordnungen und Metriken
        """
        if method == 'auto':
            # Automatische Methodenauswahl basierend auf Dateneigenschaften
            if len(data) > 1000:
                method = 'kmeans'  # Effizienter für große Datasets
            else:
                method = 'dbscan'  # Besser für kleinere Datasets mit unregelmäßigen Clustern

        if method == 'kmeans':
            # Optimale Cluster-Anzahl bestimmen
            n_clusters = self._determine_optimal_clusters(data)
            clustering = KMeans(n_clusters=n_clusters, random_state=42)
            labels = clustering.fit_predict(data)
            
        elif method == 'dbscan':
            # Parameter automatisch optimieren
            eps, min_samples = self._optimize_dbscan_params(data)
            clustering = DBSCAN(eps=eps, min_samples=min_samples)
            labels = clustering.fit_predict(data)

        # Gruppen-Charakteristiken analysieren
        group_profiles = self._analyze_group_profiles(data, labels)
        
        return {
            'labels': labels,
            'group_profiles': group_profiles,
            'method_used': method,
            'timestamp': datetime.now().isoformat()
        }

    def _determine_optimal_clusters(self, data: pd.DataFrame) -> int:
        """Bestimmt die optimale Anzahl von Clustern mittels Elbow-Methode."""
        inertias = []
        max_clusters = min(10, len(data) // 5)
        
        for k in range(2, max_clusters + 1):
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(data)
            inertias.append(kmeans.inertia_)
        
        # Elbow-Punkt finden
        diffs = np.diff(inertias)
        elbow_point = np.argmin(diffs) + 2
        
        return elbow_point

    def _optimize_dbscan_params(self, data: pd.DataFrame) -> Tuple[float, int]:
        """Optimiert die DBSCAN-Parameter für die gegebenen Daten."""
        # Nearest Neighbors Distance
        from sklearn.neighbors import NearestNeighbors
        neighbors = NearestNeighbors(n_neighbors=2)
        neighbors_fit = neighbors.fit(data)
        distances, _ = neighbors_fit.kneighbors(data)
        
        # Optimalen eps-Wert finden
        eps = np.percentile(distances[:, 1], 90)
        
        # min_samples basierend auf Datengröße
        min_samples = max(3, int(len(data) * 0.01))
        
        return eps, min_samples

    def _analyze_group_profiles(self, data: pd.DataFrame, labels: np.ndarray) -> Dict:
        """Analysiert die Charakteristiken jeder identifizierten Gruppe."""
        profiles = {}
        
        for label in np.unique(labels):
            if label == -1:  # Noise points in DBSCAN
                continue
                
            group_data = data[labels == label]
            
            profiles[f'group_{label}'] = {
                'size': len(group_data),
                'avg_values': group_data.mean().to_dict(),
                'std_values': group_data.std().to_dict(),
                'dominant_features': self._identify_dominant_features(group_data)
            }
        
        return profiles

    def _identify_dominant_features(self, group_data: pd.DataFrame) -> Dict:
        """Identifiziert die charakteristischsten Merkmale einer Gruppe."""
        feature_importance = {}
        
        # Standardabweichung vom Gesamtmittelwert
        for column in group_data.columns:
            z_score = abs((group_data[column].mean() - group_data[column].mean()) / 
                         group_data[column].std())
            feature_importance[column] = float(z_score)
        
        # Top 3 wichtigste Features
        return dict(sorted(feature_importance.items(), 
                         key=lambda x: x[1], 
                         reverse=True)[:3])

    def update_groups(self, new_data: pd.DataFrame) -> Dict:
        """
        Aktualisiert die Gruppenzuordnungen basierend auf neuen Daten.
        
        Args:
            new_data: Neue Mitarbeiterdaten
            
        Returns:
            Aktualisierte Gruppenzuordnungen
        """
        processed_data = self.preprocess_data(new_data)
        
        # Historische Gruppierungen berücksichtigen
        if hasattr(self, 'previous_groups'):
            # Gewichtete Kombination von alten und neuen Gruppierungen
            current_groups = self.identify_groups(processed_data)
            updated_groups = self._merge_groupings(
                self.previous_groups,
                current_groups,
                weight_previous=0.3,
                weight_current=0.7
            )
        else:
            updated_groups = self.identify_groups(processed_data)
        
        self.previous_groups = updated_groups
        return updated_groups

    def _merge_groupings(self, previous: Dict, current: Dict, 
                        weight_previous: float, weight_current: float) -> Dict:
        """Kombiniert alte und neue Gruppierungen mit Gewichtung."""
        # Implementierung der gewichteten Kombination
        merged_labels = []
        
        for prev_label, curr_label in zip(previous['labels'], current['labels']):
            merged_label = (prev_label * weight_previous + 
                          curr_label * weight_current)
            merged_labels.append(round(merged_label))
        
        return {
            'labels': np.array(merged_labels),
            'group_profiles': self._analyze_group_profiles(
                self.current_data, 
                np.array(merged_labels)
            ),
            'method_used': 'merged',
            'timestamp': datetime.now().isoformat()
        }

    def generate_report(self, grouping_results: Dict) -> str:
        """
        Generiert einen detaillierten Bericht über die Gruppierungsergebnisse.
        
        Args:
            grouping_results: Ergebnisse der Gruppierung
            
        Returns:
            Formatierter Bericht als String
        """
        report = []
        report.append("=== Mitarbeitergruppierung Analysebericht ===")
        report.append(f"Zeitpunkt: {grouping_results['timestamp']}")
        report.append(f"Verwendete Methode: {grouping_results['method_used']}")
        report.append("\nGruppenprofile:")
        
        for group_name, profile in grouping_results['group_profiles'].items():
            report.append(f"\n{group_name.upper()}:")
            report.append(f"Größe: {profile['size']} Mitarbeiter")
            report.append("Dominante Merkmale:")
            for feature, importance in profile['dominant_features'].items():
                report.append(f"  - {feature}: {importance:.2f}")
            
            report.append("Durchschnittswerte:")
            for metric, value in profile['avg_values'].items():
                report.append(f"  - {metric}: {value:.2f}")
        
        return "\n".join(report)

    def save_model(self, path: str):
        """Speichert das trainierte Modell und alle relevanten Komponenten."""
        model_data = {
            'scalers': self.scalers,
            'encoders': self.encoders,
            'models': self.models,
            'config': self.config,
            'feature_importance': self.feature_importance
        }
        joblib.dump(model_data, path)
        self.logger.info(f"Modell gespeichert unter: {path}")

    def load_model(self, path: str):
        """Lädt ein gespeichertes Modell."""
        try:
            model_data = joblib.load(path)
            self.scalers = model_data['scalers']
            self.encoders = model_data['encoders']
            self.models = model_data['models']
            self.config = model_data['config']
            self.feature_importance = model_data['feature_importance']
            self.logger.info(f"Modell erfolgreich geladen von: {path}")
        except Exception as e:
            self.logger.error(f"Fehler beim Laden des Modells: {e}")
            raise

# Beispielverwendung:
if __name__ == "__main__":
    # System initialisieren
    grouping_system = EmployeeGroupingSystem()
    
    # Beispieldaten laden
    sample_data = pd.DataFrame({
        'employee_id': range(1, 101),
        'department': np.random.choice(['IT', 'HR', 'Sales', 'Marketing'], 100),
        'performance': np.random.normal(3.5, 0.5, 100),
        'experience': np.random.normal(5, 2, 100),
        'skills': np.random.normal(4, 1, 100),
        'hire_date': pd.date_range(start='2015-01-01', periods=100, freq='W')
    })
    
    # Daten vorverarbeiten und Gruppen identifizieren
    processed_data = grouping_system.preprocess_data(sample_data)
    groups = grouping_system.identify_groups(processed_data)
    
    # Report generieren
    report = grouping_system.generate_report(groups)
    print(report)
    
    # Modell speichern
    grouping_system.save_model('employee_grouping_model.joblib')