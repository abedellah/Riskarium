"""Reference data used to validate case files.

Only the ISO/IEC 27001:2022 Annex A controls and NIST CSF 2.0 categories that the
bundled cases refer to are listed. Labels are short paraphrases (in French), not the
standards' full text. To use another control in a case, add it here first: a case that
cites an unknown identifier is rejected.
"""

ANNEX_A_TOTAL = 93  # number of controls in ISO/IEC 27001:2022 Annex A

ANNEX_A: dict[str, str] = {
    "A.5.5": "Contacts avec les autorités",
    "A.5.15": "Contrôle d'accès",
    "A.5.17": "Informations d'authentification",
    "A.5.24": "Planification et préparation de la gestion des incidents",
    "A.5.25": "Appréciation et décision sur les événements de sécurité",
    "A.5.26": "Réponse aux incidents de sécurité",
    "A.5.31": "Exigences légales, réglementaires et contractuelles",
    "A.5.33": "Protection des enregistrements",
    "A.5.34": "Vie privée et protection des données personnelles",
    "A.6.7": "Télétravail",
    "A.8.5": "Authentification sécurisée",
    "A.8.10": "Suppression d'informations",
    "A.8.15": "Journalisation",
    "A.8.16": "Activités de surveillance",
    "A.8.20": "Sécurité des réseaux",
    "A.8.24": "Utilisation de la cryptographie",
}

CSF_CATEGORIES: dict[str, str] = {
    "GV.OC": "Organizational Context",
    "GV.RM": "Risk Management Strategy",
    "GV.RR": "Roles, Responsibilities, and Authorities",
    "GV.PO": "Policy",
    "GV.OV": "Oversight",
    "GV.SC": "Cybersecurity Supply Chain Risk Management",
    "ID.AM": "Asset Management",
    "ID.RA": "Risk Assessment",
    "ID.IM": "Improvement",
    "PR.AA": "Identity Management, Authentication, and Access Control",
    "PR.AT": "Awareness and Training",
    "PR.DS": "Data Security",
    "PR.PS": "Platform Security",
    "PR.IR": "Technology Infrastructure Resilience",
    "DE.CM": "Continuous Monitoring",
    "DE.AE": "Adverse Event Analysis",
    "RS.MA": "Incident Management",
    "RS.AN": "Incident Analysis",
    "RS.CO": "Incident Response Reporting and Communication",
    "RS.MI": "Incident Mitigation",
    "RC.RP": "Incident Recovery Plan Execution",
    "RC.CO": "Incident Recovery Communication",
}
