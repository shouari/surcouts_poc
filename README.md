# Calculateur de Surcoûts

Une application interactive Streamlit conçue pour évaluer et justifier précisément les surcoûts liés aux installations physiques et aux intégrations technologiques. L'outil permet d'estimer les temps de main-d'œuvre supplémentaires en fonction de contraintes spécifiques telles que la hauteur sous plafond, la logistique de chantier, la météo, ou la complexité d'intégration.

## 🚀 Fonctionnalités

- **Calculateur de Majorations** : Estimez le temps total d'une tâche de base en y appliquant de multiples facteurs de surcoût (Mineur, Moyen, Sévère).
- **Intégration OpenStreetMap** : Calcul automatique et précis des distances et du temps de trajet entre votre bureau et l'adresse du client via les services de **Nominatim** et **OSRM**.
- **Générateur de Soumission** : Accumulez différentes tâches calculées dans une soumission globale.
- **Exportation des Données** : Téléchargez les calculs individuels au format **JSON** et la soumission complète sous forme de tableur **CSV**.
- **Référentiel Intégré** : Accès rapide à la matrice de tous les facteurs et pourcentages de surcoût (Matrice) directement depuis l'application.

## 🛠️ Prérequis et Installation

Assurez-vous d'avoir [Python 3.8+](https://www.python.org/) installé sur votre système.

1. **Cloner ou télécharger le dépôt** de l'application sur votre poste de travail.
2. **Créer un environnement virtuel (recommandé)** au sein du dossier du projet :
   ```bash
   python -m venv .venv
   
   # Activation sous Windows
   .venv\Scripts\activate
   
   # Activation sous macOS / Linux
   source .venv/bin/activate
   ```
3. **Installer les dépendances requises** :
   ```bash
   pip install streamlit pandas requests
   ```

## ⚙️ Configuration

Avant de lancer l'application pour la première fois, vous pouvez configurer l'adresse de départ par défaut pour le calcul des trajets routiers.
Ouvrez le fichier `app.py` dans un éditeur de texte et modifiez la constante `OFFICE_ADDRESS` :

```python
OFFICE_ADDRESS = "3178 boulevard le corbusier laval quebec canada"
```

## 🏃 Lancer l'application

Démarrez le serveur local Streamlit en tapant la commande suivante dans votre terminal :

```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur par défaut, à l'adresse habituelle : `http://localhost:8501`.

## 📖 Guide d'Utilisation

L'interface est divisée en 3 onglets principaux en haut de votre écran :

1. **Calculateur**
   - **Contexte** : Renseignez les détails de la tâche (Pièce, Famille, Description) et son Temps de base en minutes.
   - **Facteurs** : Déroulez les sous-blocs de facteurs (Hauteur, Accès, Immeuble, Logistique, etc.) et sélectionnez les niveaux de difficulté applicables à votre chantier. Un résumé cumulé des pourcentages sera généré.
   - **Déplacement** : Saisissez l'adresse de destination pour calculer instantanément la distance et la durée du trajet, puis précisez s'il s'agit d'un aller simple ou d'un aller-retour.
   - **Paramètres** : Ajustez le plafond maximum de majoration ou retirez le temps de déplacement du total global.
   - Mettez vos commentaires et appuyez sur **"Ajouter à la soumission"**.

2. **Matrice**
   - Consultez la table de référence complète. Utilisez le menu déroulant pour cibler une famille de surcoûts en particulier.

3. **Soumission**
   - Visualisez l'ensemble des tâches que vous avez traitées lors de votre session.
   - Vérifiez les métriques globales : temps de base, temps de déplacement, et coût cumulé de la soumission.
   - Utilisez le bouton de téléchargement pour exporter votre tableau en fichier `CSV` et l'importer dans vos logiciels comptables professionnels.

---
*Construit avec [Streamlit](https://streamlit.io/) et [Pandas](https://pandas.pydata.org/)*
