# Installation

## Prérequis

- Python 3.11+
- Docker
- Node.js (pour dotenv-cli)

---

## Python — Extraction

**1. Environnement virtuel et dépendances**

```bash
py -m venv venv
.\venv\Scripts\activate
pip install poetry
poetry install --no-root
```

**2. Variables d'environnement**

Le fichier .env est temporairement ajouté au repo.

**3. Base de données**

```bash
docker-compose up -d
```

**4. Lancer l'extraction**

```bash
py -m extract.application
```

---

## dbt — Transformation

**1. Installation**

```bash
cd transform
.\venv\Scripts\activate
pip install dbt-postgres dbt-score
./load_env.ps1 # Lance un script qui trouve le .env
```

Si les variables d'environnement sont toujours introuvables, ajouter:
```bash
dotenv -e ../.env
```
avant chaque commande

**2. Dépendances dbt**

```bash
dbt deps
```

**3. Tester la connexion**

```bash
dbt debug
```

**4. Lancer les modèles**

```bash
# Un modèle spécifique
dbt run --select stg_artistes

# Tous les staging
dbt run --select models/1_staging

# Tous les modèles
dbt run

# Tous les tests
dbt test
```

**5. Commandes utiles**

```bash
# Générer la documentation
dbt docs generate

# Générer le schema.yml d'un modèle
dbt run-operation generate_model_yaml --args '{"model_names": ["stg_artistes"]}'


# Ouvre une interface web locale pour visualiser les modèles
dbt docs serve
```

---

## Note SSL (réseau DIIAGE)

Si tu rencontres des erreurs SSL :

```bash
git config http.sslVerify false
```