import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_employee_id():
    return f"EMP{np.random.randint(10000, 99999)}"

def generate_name():
    first_names = ["Anna", "Max", "Laura", "Tom", "Sophie", "Felix", "Emma", "Paul", "Lisa", "Jan"]
    last_names = ["Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker", "Schulz", "Hoffmann"]
    return f"{np.random.choice(first_names)} {np.random.choice(last_names)}"

def generate_job_title():
    job_titles = [
        "Software Entwickler", "Systemadministrator", "Datenanalyst", 
        "Netzwerktechniker", "IT-Projektmanager", "Maschinenbauingenieur",
        "Elektrotechniker", "Mechatroniker", "Produktionstechniker",
        "Buchhalter", "Controller", "Finanzanalyst", "Steuerberater",
        "Personalreferent", "HR-Manager", "Recruiter", "Vertriebsmitarbeiter",
        "Key Account Manager", "Marketing Manager", "PR-Berater", "Grafikdesigner",
        "Produktmanager", "Qualitätsingenieur", "Logistikkoordinator",
        "Einkäufer", "Jurist", "Verwaltungsangestellter", "Kundenbetreuer",
        "Forschungsingenieur", "Laborant", "Produktionsleiter", "Facility Manager",
        "Datenschutzbeauftragter", "Business Analyst", "Scrum Master",
        "DevOps Engineer", "Cloud Architekt", "UX Designer", "SEO Spezialist",
        "Social Media Manager", "Content Creator", "Produktionsmitarbeiter"
    ]
    return np.random.choice(job_titles)

def generate_department():
    departments = ["IT", "Entwicklung", "Produktion", "Finanzen", "Personal", "Vertrieb", 
                   "Marketing", "Einkauf", "Logistik", "Qualitätsmanagement", "Recht", 
                   "Forschung & Entwicklung", "Kundenservice"]
    return np.random.choice(departments)

def generate_location():
    locations = ["Berlin", "Hamburg", "München", "Köln", "Frankfurt", "Stuttgart", 
                 "Düsseldorf", "Leipzig", "Dortmund", "Essen", "Bremen", "Dresden"]
    return np.random.choice(locations)

def generate_salary():
    return np.random.randint(30000, 120000)

def generate_hire_date():
    start_date = datetime(2010, 1, 1)
    end_date = datetime.now()
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = np.random.randint(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)

def generate_performance_rating():
    return np.random.choice(["Ausgezeichnet", "Gut", "Befriedigend", "Verbesserungswürdig"], p=[0.1, 0.5, 0.3, 0.1])

def generate_education_level():
    levels = ["Hochschulabschluss", "Bachelor", "Master", "Promotion", "Ausbildung", "Abitur"]
    return np.random.choice(levels)

def generate_sample_data(num_employees):
    data = []
    for _ in range(num_employees):
        employee = {
            "MitarbeiterID": generate_employee_id(),
            "Name": generate_name(),
            "Beschäftigungsart": generate_job_title(),
            "Abteilung": generate_department(),
            "Standort": generate_location(),
            "Gehalt": generate_salary(),
            "Einstellungsdatum": generate_hire_date(),
            "Leistungsbewertung": generate_performance_rating(),
            "Bildungsniveau": generate_education_level()
        }
        data.append(employee)
    return pd.DataFrame(data)

def main():
    num_employees = 1800  # Anzahl der zu generierenden Mitarbeiterdatensätze
    df = generate_sample_data(num_employees)
    
    # Speichern der Daten als CSV
    df.to_csv("beispiel_mitarbeiterdaten.csv", index=False)
    print(f"{num_employees} Beispiel-Mitarbeiterdatensätze wurden generiert und in 'beispiel_mitarbeiterdaten.csv' gespeichert.")

    # Einige Beispiele anzeigen
    print("\nHier sind einige Beispieldatensätze:")
    print(df.head())

    # Einige Statistiken anzeigen
    print("\nStatistiken über die generierten Daten:")
    print(df.describe(include='all'))

if __name__ == "__main__":
    main()