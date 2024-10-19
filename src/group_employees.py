import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import re
from collections import defaultdict


filepath = f"path to the sample data"

def load_data(file_path):
    return pd.read_csv(file_path)

def define_job_groups():
    return {
        'IT': ['informatiker', 'analyst', 'software', 'entwickler', 'programmierer', 'system', 'netzwerk', 'daten'],
        'Mechanik': ['mechaniker', 'techniker', 'schlosser', 'monteur'],
        'Elektrik': ['elektriker', 'elektroniker', 'elektrotechniker'],
        'Verwaltung': ['sachbearbeiter', 'bürokaufmann', 'sekretär', 'assistent', 'kaufmann'],
        'Management': ['leiter', 'manager', 'direktor', 'geschäftsführer', 'vorstand'],
        'Vertrieb': ['verkäufer', 'vertrieb', 'account', 'kundenberater'],
        'Personal': ['personal', 'hr', 'recruiter', 'personalreferent'],
        'Finanzen': ['buchhalter', 'controller', 'finanzen', 'steuer'],
        'Marketing': ['marketing', 'werbe', 'pr', 'kommunikation'],
        'Produktion': ['produktions', 'fertigung', 'maschinenbediener', 'operator'],
        'Logistik': ['logistik', 'lager', 'versand', 'spedition'],
        'Forschung': ['forscher', 'wissenschaftler', 'entwicklung', 'labor'],
        'Kundenservice': ['service', 'support', 'kundenbetreuung'],
        'Design': ['designer', 'gestalter', 'kreativ'],
        'Qualität': ['qualität', 'prüfer', 'tester'],
        'Rechtswesen': ['jurist', 'anwalt', 'rechts'],
        'Gesundheit': ['arzt', 'pfleger', 'medizin', 'gesundheit'],
        'Bildung': ['lehrer', 'dozent', 'trainer', 'ausbilder']
    }


def categorize_job(job_title, job_groups):
    job_title_lower = job_title.lower()
    for group, keywords in job_groups.items():
        if any(keyword in job_title_lower for keyword in keywords):
            return group
    return 'Sonstige'

def group_employees_rule_based(df, job_groups):
    df['Gruppe_Regelbasiert'] = df['Beschäftigungsart'].apply(lambda x: categorize_job(x, job_groups))
    return df

def preprocess_text(text):
    # Einfache Vorverarbeitung: Kleinschreibung und Entfernung von Sonderzeichen
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text

def train_ml_model(df):
    # Text-Vorverarbeitung
    df['Processed_Text'] = df['Beschäftigungsart'].apply(preprocess_text)

    # TF-IDF Vektorisierung
    vectorizer = TfidfVectorizer(max_features=1000)
    X = vectorizer.fit_transform(df['Processed_Text'])
    y = df['Gruppe_Regelbasiert']

    # Aufteilen in Trainings- und Testdaten
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Trainieren des Random Forest Classifiers
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    # Modell evaluieren
    y_pred = clf.predict(X_test)
    print("Klassifikationsbericht:")
    print(classification_report(y_test, y_pred))

    return clf, vectorizer

def apply_ml_model(df, clf, vectorizer):
    X = vectorizer.transform(df['Processed_Text'])
    df['Gruppe_ML'] = clf.predict(X)
    return df

def analyze_groups(df):
    for method in ['Regelbasiert', 'ML']:
        group_col = f'Gruppe_{method}'
        group_counts = df[group_col].value_counts()
        print(f"\nVerteilung der Mitarbeiter nach Gruppen ({method}):")
        print(group_counts)
        
        print(f"\nBeispiele für Berufsbezeichnungen in jeder Gruppe ({method}):")
        for group in df[group_col].unique():
            print(f"\n{group}:")
            print(df[df[group_col] == group]['Beschäftigungsart'].sample(min(5, len(df[df[group_col] == group]))).tolist())

def compare_methods(df):
    agreement = (df['Gruppe_Regelbasiert'] == df['Gruppe_ML']).mean()
    print(f"\nÜbereinstimmung zwischen regelbasierter und ML-Methode: {agreement:.2%}")

    disagreement_df = df[df['Gruppe_Regelbasiert'] != df['Gruppe_ML']]
    print("\nBeispiele für Unstimmigkeiten:")
    print(disagreement_df[['Beschäftigungsart', 'Gruppe_Regelbasiert', 'Gruppe_ML']].sample(min(10, len(disagreement_df))))

def main():
    file_path = 'mitarbeiterdaten.csv'
    df = load_data(file_path)
    job_groups = define_job_groups()
    
    # Regelbasierte Gruppierung
    df = group_employees_rule_based(df, job_groups)
    
    # ML-Modell trainieren und anwenden
    clf, vectorizer = train_ml_model(df)
    df = apply_ml_model(df, clf, vectorizer)
    
    # Analyse und Vergleich der Ergebnisse
    analyze_groups(df)
    compare_methods(df)
    
    # Speichern der gruppierten Daten und des ML-Modells
    df.to_csv('gruppierte_mitarbeiterdaten_ml.csv', index=False)
    joblib.dump(clf, 'job_classification_model.joblib')
    joblib.dump(vectorizer, 'job_classification_vectorizer.joblib')

if __name__ == "__main__":
    main()