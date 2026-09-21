<p align="center">
  <img src="assets/banner.svg?v=2" alt="Riskarium, registre de risques et rattachement à l'ISO 27001" width="100%">
</p>

# Riskarium

Petit outil qui transforme une analyse de risques décrite en YAML en **registre de
risques**, **matrice de criticité** et **rattachement à ISO/IEC 27001:2022 et NIST CSF 2.0**,
avec une feuille de route par horizon.

**Stack :** Python · YAML · SVG · pytest · ruff · mypy

Le dépôt contient un premier cas, entièrement sourcé : la violation de données Free Mobile / Free
d'octobre 2024, sanctionnée par la CNIL en janvier 2026.

![Matrice des risques](cases/free-mobile-2024/heatmap.svg)

Rapport complet : [`cases/free-mobile-2024/report.md`](cases/free-mobile-2024/report.md)

---

## Pourquoi ce projet

En gouvernance, risque et conformité, le travail consiste à relier des **faits** à des
**risques**, des risques à des **contrôles**, et des contrôles à un **plan d'action**. Riskarium
rend cette chaîne explicite et vérifiable : chaque fait renvoie à une source publique, chaque
risque à des contrôles d'un référentiel, et le rapport se régénère à l'identique.

## Utilisation

```bash
pip install -e .
riskarium validate cases/free-mobile-2024/case.yaml
riskarium report cases/free-mobile-2024/case.yaml -o cases/free-mobile-2024
```

La commande `report` écrit `report.md` et `heatmap.svg`. Une entrée invalide est refusée avec un
message précis (cotation hors de 1 à 5, contrôle ISO inconnu, fait sourcé sans source...).

## Format d'un cas

```yaml
risks:
  - id: R1
    title: "Compromission de l'accès distant (VPN)"
    scenario: "..."
    likelihood: 4          # 1 à 5
    impact: 5              # 1 à 5
    facts:
      - kind: documented   # établi par une source
        source: S1
        text: "..."
      - kind: inferred     # raisonnement de l'analyste, signalé comme tel
        source: null
        text: "..."
    iso_controls: [A.8.5, A.5.15]
    nist_csf: [PR.AA]
    treatment:
      decision: reduce     # reduce | accept | transfer | avoid
      actions: ["..."]
      likelihood: 2        # cotation visée après traitement
      impact: 4
```

## Règles de calcul

Volontairement simples, pour pouvoir les expliquer en deux minutes :

- **Score** = vraisemblance × impact (chacun de 1 à 5).
- **Niveau** : critique ≥ 15, élevé 10 à 14, moyen 5 à 9, faible ≤ 4.
- **Horizon** de traitement, fixé par le niveau du risque inhérent : critique 0-3 mois,
  élevé 3-6 mois, moyen ou faible 6-12 mois.
- **Confiance** dans la cotation : *élevée* si tous les faits du risque sont sourcés, *moyenne* si
  certains relèvent de l'analyse, *faible* si aucun ne l'est. C'est ce qui distingue ce qu'une
  source établit de ce que l'analyste suppose.
- Un traitement ne peut pas **augmenter** la vraisemblance ou l'impact.

## Le cas Free Mobile / Free

Six risques tirés des manquements relevés par la CNIL (articles 32, 34 et 5-1-e du RGPD) : accès
VPN sans authentification multifacteur, détection d'anomalies inefficace, stockage faible des mots
de passe, conservation excessive des données, information insuffisante des personnes, et
réutilisation des données volées (ce dernier, non établi par la décision, est marqué comme
analyse). 16 contrôles de l'Annexe A y sont mobilisés.

Sources : communiqué de la CNIL du 14 janvier 2026 et délibération SAN-2026-001, listés dans le
rapport. **Analyse externe, fondée uniquement sur des sources publiques ; elle ne décrit pas
l'état interne actuel des sociétés concernées.**

## Tests et CI

Une cinquantaine de tests, dont une majorité de cas négatifs (entrée invalide refusée) et un test
qui échoue si le rapport stocké dans le dépôt n'est plus celui que produit le code.

Le pipeline `.github/workflows/ci.yml` exécute ruff, mypy en mode strict et pytest.

## Limites connues

- Les libellés du catalogue ISO sont des paraphrases courtes, pas le texte de la norme ; seuls les
  contrôles utilisés par les cas fournis y figurent.
- Les cotations sont un jugement d'analyste, pas une mesure.
- Pas de calcul de risque agrégé ni de modélisation des scénarios d'attaque : l'outil documente
  et rend traçable, il ne remplace pas une méthode complète comme EBIOS Risk Manager.

---

*Projet personnel : LAGRINI Mohamed Abdellah*
