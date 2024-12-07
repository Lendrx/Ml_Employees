import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
from typing import List, Dict, Tuple, Optional
import logging
from datetime import datetime
import joblib

class EmployeeGroupingSystem:
    """
    Ein intelligentes System zur dynamischen Gruppierung von Mitarbeitern
    basierend auf verschiedenen Merkmalen und Verhaltensmustern.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialisiert das Gruppierungssystem mit optionalen Konfigurationsparametern.
        
        Args:
            config (Dict, optional): Konfigurationsparameter für das System
        """
        self.config = config or {
            'n_clusters': 5,
            'random_state': 42,
            'min_samples': 5,
            'eps': 0.5
        }
        
        # Logger Setup
        self.logger = self._setup_logger()
        
        # Modelle initialisieren
        self.models = {
            'kmeans': KMeans(n_clusters=self.config['n_clusters'], 
                           random_state=self.config['random_state']),
            'dbscan': DBSCAN(eps=self.config['eps'], 
                            min_samples=self.config['min_samples']),
            'gmm': GaussianMixture(n_components=self.config['n_clusters'], 
                                 random_state=self.config['random_state'])
        }
        
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=0.95)  # 95% der Varianz erhalten

    def _setup_logger(self) -> logging.Logger:
        """
        Richtet das Logging-System ein.
        """
        logger = logging.getLogger('EmployeeGrouping')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler('employee_grouping.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Bereitet die Rohdaten für die Analyse vor.
        
        Args:
            data (pd.DataFrame): Rohe Mitarbeiterdaten
            
        Returns:
            pd.DataFrame: Vorverarbeitete Daten
        """
        try:
            # Kopie erstellen um Originaldaten zu bewahren
            processed_data = data.copy()
            
            # Kategorische Variablen encodieren
            categorical_columns = processed_data.select_dtypes(include=['object']).columns
            for col in categorical_columns:
                processed_data[col] = pd.Categorical(processed_data[col]).codes
            
            # Fehlende Werte behandeln
            processed_data = processed_data.fillna(processed_data.mean())
            
            # Skalierung
            processed_data = pd.DataFrame(
                self.scaler.fit_transform(processed_data),
                columns=processed_data.columns
            )
            
            # Dimensionsreduktion mit PCA
            reduced_data = pd.DataFrame(
                self.pca.fit_transform(processed_data),
                index=processed_data.index
            )
            
            self.logger.info(f"Daten erfolgreich vorverarbeitet. Shape: {reduced_data.shape}")
            return reduced_data
            
        except Exception as e:
            self.logger.error(f"Fehler bei der Datenvorverarbeitung: {str(e)}")
            raise

    def identify_feature_importance(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Identifiziert die wichtigsten Merkmale für die Gruppierung.
        
        Args:
            data (pd.DataFrame): Vorverarbeitete Daten
            
        Returns:
            Dict[str, float]: Wichtigkeit der einzelnen Merkmale
        """
        feature_importance = {}
        for column in data.columns:
            importance = np.abs(data[column].corr(data.mean(axis=1)))
            feature_importance[column] = importance
            
        return dict(sorted(feature_importance.items(), 
                         key=lambda x: x[1], reverse=True))

    def analyze_groups(self, 
                      data: pd.DataFrame, 
                      labels: np.ndarray,
                      original_data: pd.DataFrame) -> Dict:
        """
        Analysiert die gefundenen Gruppen und erstellt Profile.
        
        Args:
            data (pd.DataFrame): Gruppierte Daten
            labels (np.ndarray): Gruppenzuordnungen
            original_data (pd.DataFrame): Originaldaten
            
        Returns:
            Dict: Gruppenprofile und Statistiken
        """
        profiles = {}
        
        for group_id in np.unique(labels):
            group_mask = labels == group_id
            group_data = original_data[group_mask]
            
            profile = {
                'size': len(group_data),
                'percentage': (len(group_data) / len(data)) * 100,
                'key_characteristics': self._get_key_characteristics(group_data),
                'statistics': self._calculate_group_statistics(group_data)
            }
            
            profiles[f'Group_{group_id}'] = profile
            
        return profiles

    def _get_key_characteristics(self, group_data: pd.DataFrame) -> Dict:
        """
        Ermittelt die Schlüsselmerkmale einer Gruppe.
        """
        characteristics = {}
        
        for column in group_data.columns:
            if group_data[column].dtype in ['int64', 'float64']:
                characteristics[column] = {
                    'mean': group_data[column].mean(),
                    'std': group_data[column].std()
                }
            else:
                characteristics[column] = group_data[column].mode()[0]
                
        return characteristics

    def _calculate_group_statistics(self, group_data: pd.DataFrame) -> Dict:
        """
        Berechnet detaillierte Statistiken für eine Gruppe.
        """
        return {
            'numerical_stats': group_data.describe().to_dict(),
            'correlations': group_data.corr().to_dict(),
            'unique_counts': {col: group_data[col].nunique() 
                            for col in group_data.columns}
        }

    def fit_predict(self, 
                   data: pd.DataFrame, 
                   method: str = 'kmeans') -> Tuple[np.ndarray, Dict]:
        """
        Führt die Gruppierung durch und gibt Labels und Profile zurück.
        
        Args:
            data (pd.DataFrame): Zu gruppierende Daten
            method (str): Verwendete Clustering-Methode
            
        Returns:
            Tuple[np.ndarray, Dict]: Gruppenlabels und Gruppenprofile
        """
        try:
            # Daten vorverarbeiten
            processed_data = self.preprocess_data(data)
            
            # Modell auswählen und anwenden
            model = self.models[method]
            labels = model.fit_predict(processed_data)
            
            # Gruppen analysieren
            profiles = self.analyze_groups(processed_data, labels, data)
            
            # Modell speichern
            self._save_model(model, method)
            
            self.logger.info(f"Gruppierung erfolgreich durchgeführt. Methode: {method}")
            return labels, profiles
            
        except Exception as e:
            self.logger.error(f"Fehler bei der Gruppierung: {str(e)}")
            raise

    def _save_model(self, model: object, method: str):
        """
        Speichert das trainierte Modell.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"models/employee_grouping_{method}_{timestamp}.joblib"
        joblib.dump(model, filename)
        self.logger.info(f"Modell gespeichert: {filename}")

    def evaluate_grouping(self, 
                         data: pd.DataFrame, 
                         labels: np.ndarray) -> Dict[str, float]:
        """
        Evaluiert die Qualität der Gruppierung.
        
        Args:
            data (pd.DataFrame): Gruppierte Daten
            labels (np.ndarray): Gruppenzuordnungen
            
        Returns:
            Dict[str, float]: Evaluationsmetriken
        """
        from sklearn.metrics import silhouette_score, calinski_harabasz_score
        
        metrics = {
            'silhouette_score': silhouette_score(data, labels),
            'calinski_harabasz_score': calinski_harabasz_score(data, labels)
        }
        
        self.logger.info(f"Gruppierungsevaluation abgeschlossen: {metrics}")
        return metrics

    def suggest_optimal_groups(self, 
                             data: pd.DataFrame, 
                             max_clusters: int = 10) -> int:
        """
        Schlägt die optimale Anzahl von Gruppen vor.
        
        Args:
            data (pd.DataFrame): Zu analysierende Daten
            max_clusters (int): Maximale Anzahl zu testender Cluster
            
        Returns:
            int: Optimale Anzahl von Gruppen
        """
        scores = []
        processed_data = self.preprocess_data(data)
        
        for n in range(2, max_clusters + 1):
            kmeans = KMeans(n_clusters=n, random_state=42)
            labels = kmeans.fit_predict(processed_data)
            score = silhouette_score(processed_data, labels)
            scores.append(score)
        
        optimal_clusters = scores.index(max(scores)) + 2
        self.logger.info(f"Optimale Gruppenanzahl gefunden: {optimal_clusters}")
        return optimal_clusters

if __name__ == "__main__":
    # Beispielverwendung
    grouping_system = EmployeeGroupingSystem()
    
    # Beispieldaten laden
    data = pd.read_csv("data/employee_data.csv")
    
    # Optimale Gruppenanzahl finden
    optimal_groups = grouping_system.suggest_optimal_groups(data)
    
    # System mit optimaler Gruppenzahl neu initialisieren
    grouping_system = EmployeeGroupingSystem({
        'n_clusters': optimal_groups,
        'random_state': 42,
        'min_samples': 5,
        'eps': 0.5
    })
    
    # Gruppierung durchführen
    labels, profiles = grouping_system.fit_predict(data)
    
    # Ergebnisse evaluieren
    evaluation = grouping_system.evaluate_grouping(data, labels)
    
    # Wichtige Merkmale identifizieren
    feature_importance = grouping_system.identify_feature_importance(data)