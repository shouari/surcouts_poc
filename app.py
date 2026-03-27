import json
import time

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Calculateur de Surcoûts", page_icon="🧮", layout="wide")

OFFICE_ADDRESS = "3178 boulevard le corbusier laval quebec canada"
NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org/search"
OSRM_ROUTE_URL = "https://router.project-osrm.org/route/v1/driving"
REQUEST_HEADERS = {
    "User-Agent": "CableEtSon-Surcouts-POC/1.0 (internal testing)"
}

MATRIX = {
    "Installation physique": [
        {"Sous-bloc": "Hauteur", "Facteur": "Plafond 12 pi", "Mineur": 3, "Moyen": None, "Sévère": None, "Notes": ""},
        {"Sous-bloc": "Hauteur", "Facteur": "Plafond 15 pi", "Mineur": 10, "Moyen": None, "Sévère": None, "Notes": ""},
        {"Sous-bloc": "Hauteur", "Facteur": "Plafond 18 pi", "Mineur": 19, "Moyen": None, "Sévère": None, "Notes": ""},
        {"Sous-bloc": "Hauteur", "Facteur": "Plafond 20 pi", "Mineur": 25, "Moyen": None, "Sévère": None, "Notes": ""},
        {"Sous-bloc": "Accès physique", "Facteur": "Échafaudage fixe requis", "Mineur": 40, "Moyen": None, "Sévère": None, "Notes": "Montage et démontage inclus"},
        {"Sous-bloc": "Support", "Facteur": "Béton armé — murs", "Mineur": 50, "Moyen": None, "Sévère": None, "Notes": "Perçage, fixation"},
        {"Sous-bloc": "Support", "Facteur": "Béton armé — colonnes", "Mineur": 100, "Moyen": None, "Sévère": None, "Notes": ""},
        {"Sous-bloc": "Mode de pose", "Facteur": "Installation exposée", "Mineur": 20, "Moyen": None, "Sévère": None, "Notes": "Chemins de câbles"},
        {"Sous-bloc": "Contrainte physique", "Facteur": "Espace restreint / confiné", "Mineur": 20, "Moyen": 30, "Sévère": 40, "Notes": ""},
        {"Sous-bloc": "Encombrement", "Facteur": "Plancher encombré vs dégagé", "Mineur": 25, "Moyen": None, "Sévère": None, "Notes": "Perte de productivité"},
        {"Sous-bloc": "Type de projet", "Facteur": "Rénovation vs neuf", "Mineur": 25, "Moyen": 50, "Sévère": 100, "Notes": ""},
        {"Sous-bloc": "Type de projet", "Facteur": "Bâtiment patrimonial / centenaire", "Mineur": 25, "Moyen": 40, "Sévère": 50, "Notes": ""},
        {"Sous-bloc": "Occupation", "Facteur": "Bâtiment occupé pendant les travaux", "Mineur": 25, "Moyen": 35, "Sévère": 50, "Notes": ""},
        {"Sous-bloc": "Tirage / fishing", "Facteur": "Câblage en murs fermés vs murs ouverts", "Mineur": 100, "Moyen": 150, "Sévère": 200, "Notes": ""},
        {"Sous-bloc": "Immeuble", "Facteur": "Tour 3–6 étages", "Mineur": 1, "Moyen": None, "Sévère": None, "Notes": "Logistique"},
        {"Sous-bloc": "Immeuble", "Facteur": "Tour 7–14 étages", "Mineur": 5, "Moyen": None, "Sévère": None, "Notes": "Le PDF indique 2–5 %; cette V1 prend la borne haute pour simplifier"},
        {"Sous-bloc": "Immeuble", "Facteur": "Tour 15–19 étages", "Mineur": 7, "Moyen": None, "Sévère": None, "Notes": "Logistique"},
        {"Sous-bloc": "Immeuble", "Facteur": "Tour 20–30 étages", "Mineur": 13, "Moyen": None, "Sévère": None, "Notes": "Logistique"},
        {"Sous-bloc": "Logistique verticale", "Facteur": "Haute tour — ascenseur, transport matériel", "Mineur": 15, "Moyen": 20, "Sévère": 30, "Notes": ""},
    ],
    "Conditions d’exécution": [
        {"Sous-bloc": "Météo", "Facteur": "Hiver extérieur 0 à -10 °C", "Mineur": 10, "Moyen": 20, "Sévère": None, "Notes": ""},
        {"Sous-bloc": "Météo", "Facteur": "Hiver extérieur -10 à -20 °C", "Mineur": 25, "Moyen": 35, "Sévère": None, "Notes": ""},
        {"Sous-bloc": "Météo", "Facteur": "Hiver extérieur -20 °C et moins", "Mineur": 40, "Moyen": 50, "Sévère": None, "Notes": ""},
        {"Sous-bloc": "Coordination", "Facteur": "Multi-corps de métier (stacking)", "Mineur": 10, "Moyen": 20, "Sévère": 30, "Notes": ""},
        {"Sous-bloc": "Accès", "Facteur": "Accès restreint au chantier", "Mineur": 5, "Moyen": 12, "Sévère": 30, "Notes": ""},
        {"Sous-bloc": "Logistique", "Facteur": "Livraison, stationnement, logistique", "Mineur": 10, "Moyen": 25, "Sévère": 50, "Notes": ""},
    ],
    "Programmation / intégration technologique": [
        {"Sous-bloc": "Reprise", "Facteur": "Système installé par un autre intégrateur", "Mineur": 50, "Moyen": 100, "Sévère": 230, "Notes": ""},
        {"Sous-bloc": "Intégration", "Facteur": "Multi-plateformes", "Mineur": 10, "Moyen": 15, "Sévère": 25, "Notes": "Control4 + Lutron + réseau + sécurité"},
        {"Sous-bloc": "Héritage", "Facteur": "Équipement non standard / hérité", "Mineur": 100, "Moyen": 200, "Sévère": 233, "Notes": ""},
    ],
    "Cas spécialisés / sous-systèmes": [
        {"Sous-bloc": "Vidéosurveillance", "Facteur": "Installation caméras sur béton / brique extérieure", "Mineur": 30, "Moyen": 50, "Sévère": 75, "Notes": ""},
        {"Sous-bloc": "Contrôle d’accès", "Facteur": "Rénovation vs neuf (par porte)", "Mineur": 50, "Moyen": 100, "Sévère": 150, "Notes": ""},
        {"Sous-bloc": "Câblage structuré", "Facteur": "Cat6A vs Cat6", "Mineur": 10, "Moyen": 15, "Sévère": None, "Notes": "Rigidité du câble"},
    ],
}

SECTION_OPTIONS = [
    "Salon", "Salle familiale", "Cinéma maison", "Cuisine", "Chambre",
    "Bureau", "Rack / salle technique", "Entrée", "Extérieur", "Autre"
]

LEVEL_TO_COL = {
    "Aucun": None,
    "Mineur": "Mineur",
    "Moyen": "Moyen",
    "Sévère": "Sévère",
}

if "quote_lines" not in st.session_state:
    st.session_state.quote_lines = []


def fmt_pct(value):
    try:
        return f"{int(value)} %"
    except (ValueError, TypeError):
        return "—"


def get_factor_value(row, level):
    col = LEVEL_TO_COL[level]
    if col is None:
        return 0
    value = row.get(col)
    return 0 if value is None else float(value)


def render_family_reference(family):
    df = pd.DataFrame(MATRIX[family])[["Sous-bloc", "Facteur", "Mineur", "Moyen", "Sévère", "Notes"]]
    for col in ["Mineur", "Moyen", "Sévère"]:
        df[col] = df[col].apply(fmt_pct)
    st.dataframe(df, width="stretch", hide_index=True)


def compute_totals(base_minutes, selected_factors, cap_percent, travel_minutes):
    raw_percent = sum(item["pourcentage"] for item in selected_factors)
    applied_percent = min(raw_percent, cap_percent)
    adjusted_task_minutes = base_minutes * (1 + applied_percent / 100)
    total_with_travel = adjusted_task_minutes + travel_minutes
    return raw_percent, applied_percent, adjusted_task_minutes, total_with_travel


@st.cache_data(show_spinner=False)
def geocode_address(address: str):
    params = {
        "q": address,
        "format": "jsonv2",
        "limit": 1,
        "countrycodes": "ca",
    }
    response = requests.get(
        NOMINATIM_BASE_URL,
        params=params,
        headers=REQUEST_HEADERS,
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()

    if not data:
        return None

    first = data[0]
    return {
        "lat": float(first["lat"]),
        "lon": float(first["lon"]),
        "display_name": first.get("display_name", address),
    }


@st.cache_data(show_spinner=False)
def get_route(office_address: str, client_address: str):
    origin = geocode_address(office_address)

    # Respect minimal de la politique publique Nominatim
    time.sleep(1.1)

    destination = geocode_address(client_address)

    if origin is None:
        raise ValueError("Adresse bureau introuvable.")
    if destination is None:
        raise ValueError("Adresse client introuvable.")

    coords = f'{origin["lon"]},{origin["lat"]};{destination["lon"]},{destination["lat"]}'
    url = f"{OSRM_ROUTE_URL}/{coords}"

    params = {
        "overview": "false",
        "steps": "false",
        "alternatives": "false",
    }

    response = requests.get(url, params=params, headers=REQUEST_HEADERS, timeout=20)
    response.raise_for_status()
    data = response.json()

    if data.get("code") != "Ok" or not data.get("routes"):
        raise ValueError("Aucun trajet routier trouvé.")

    route = data["routes"][0]
    return {
        "distance_km_one_way": route["distance"] / 1000,
        "duration_min_one_way": route["duration"] / 60,
        "origin_label": origin["display_name"],
        "destination_label": destination["display_name"],
    }


st.title("Calculateur de surcoûts")
st.caption("Version 0.0.1 pour valider l'utilsation et la pertinence.")

tab_calc, tab_matrix, tab_quote = st.tabs(["Calculateur", "Matrice", "Soumission"])

with tab_calc:
    left, right = st.columns([1.05, 0.95], gap="large")

    with left:
        with st.container(border=True):
            st.subheader("1. Contexte")
            c1, c2 = st.columns(2)
            with c1:
                section = st.selectbox("Section / pièce", SECTION_OPTIONS, index=0)
            with c2:
                family = st.selectbox("Famille", list(MATRIX.keys()), index=0)

            task_name = st.text_input("Tâche / description", placeholder="Ex. installation haut-parleur salon")
            base_minutes = st.number_input(
                "Temps de base (minutes)",
                min_value=1,
                max_value=10000,
                value=30,
                step=5
            )

        with st.container(border=True):
            st.subheader("2. Facteurs")
            st.caption("Choisir surtout les facteurs dominants.")

            selected_factors = []
            family_rows = MATRIX[family]

            blocks = []
            seen = set()
            for row in family_rows:
                sb = row["Sous-bloc"]
                if sb not in seen:
                    blocks.append(sb)
                    seen.add(sb)

            for block in blocks:
                block_rows = [r for r in family_rows if r["Sous-bloc"] == block]
                with st.expander(block, expanded=False):
                    for idx, row in enumerate(block_rows):
                        factor_key = f"{family}_{block}_{idx}_{row['Facteur']}"
                        options = ["Aucun"] + [lvl for lvl in ["Mineur", "Moyen", "Sévère"] if row.get(lvl) is not None]

                        cols = st.columns([1.7, 0.9, 0.8, 0.8, 0.8])
                        cols[0].write(row["Facteur"])
                        level = cols[1].selectbox(
                            "Niveau",
                            options,
                            key=f"factor_{factor_key}",
                            label_visibility="collapsed"
                        )
                        cols[2].write(fmt_pct(row.get("Mineur")))
                        cols[3].write(fmt_pct(row.get("Moyen")))
                        cols[4].write(fmt_pct(row.get("Sévère")))

                        val = get_factor_value(row, level)
                        if level != "Aucun" and val > 0:
                            selected_factors.append({
                                "sous_bloc": row["Sous-bloc"],
                                "facteur": row["Facteur"],
                                "niveau": level,
                                "pourcentage": val,
                                "notes": row.get("Notes", "")
                            })

                        if row.get("Notes"):
                            st.caption(row["Notes"])

        with st.container(border=True):
            st.subheader("3. Déplacement")
            st.caption("Calcul automatique avec OpenStreetMap.")
            st.text_input("Adresse bureau", value=OFFICE_ADDRESS, disabled=True)

            client_address = st.text_input(
                "Adresse client",
                value="",
                placeholder="Ex. 123 rue Exemple, Montréal, QC"
            )

            trip_mode = st.radio("Trajet", ["Aller simple", "Aller-retour"], horizontal=True)
            include_travel = st.checkbox("Inclure le déplacement dans le temps total", value=True)

            route_data = None
            route_error = None

            if client_address.strip():
                try:
                    with st.spinner("Calcul du trajet..."):
                        route_data = get_route(OFFICE_ADDRESS, client_address.strip())
                except Exception as e:
                    route_error = str(e)

            if route_error:
                st.error(route_error)

            if route_data:
                travel_multiplier = 2 if trip_mode == "Aller-retour" else 1
                travel_minutes = route_data["duration_min_one_way"] * travel_multiplier
                travel_km = route_data["distance_km_one_way"] * travel_multiplier

                c1, c2 = st.columns(2)
                c1.metric("Distance estimée", f"{travel_km:.1f} km")
                c2.metric("Temps estimé", f"{travel_minutes:.0f} min")

                st.caption(f"Origine : {route_data['origin_label']}")
                st.caption(f"Destination : {route_data['destination_label']}")
            else:
                travel_minutes = 0
                travel_km = 0.0

        with st.container(border=True):
            st.subheader("4. Paramètres")
            cap_percent = st.number_input(
                "Plafond de majoration (%)",
                min_value=0,
                max_value=500,
                value=250,
                step=5
            )
            comment = st.text_area(
                "Commentaire / justification",
                height=100,
                placeholder="Ex. béton + bâtiment occupé + accès restreint."
            )

    with right:
        raw_percent, applied_percent, adjusted_task_minutes, total_with_travel = compute_totals(
            base_minutes=base_minutes,
            selected_factors=selected_factors,
            cap_percent=cap_percent,
            travel_minutes=travel_minutes if include_travel else 0
        )

        with st.container(border=True):
            st.subheader("Résultat")
            m1, m2 = st.columns(2)
            m1.metric("Majoration brute", f"{raw_percent:.0f} %")
            m2.metric("Majoration appliquée", f"{applied_percent:.0f} %")

            m3, m4 = st.columns(2)
            m3.metric("Temps ajusté tâche", f"{adjusted_task_minutes:.1f} min")
            m4.metric("Temps total", f"{total_with_travel:.1f} min")

        with st.container(border=True):
            st.markdown("**Résumé**")
            st.write(f"Section : **{section}**")
            st.write(f"Famille : **{family}**")
            st.write(f"Tâche : **{task_name or '—'}**")
            st.write(f"Temps de base : **{base_minutes} min**")
            if include_travel:
                st.write(f"Déplacement estimé : **{travel_minutes:.0f} min** / **{travel_km:.1f} km**")
            else:
                st.write("Déplacement : **non inclus**")

        with st.container(border=True):
            st.markdown("**Facteurs retenus**")
            if not selected_factors:
                st.write("Aucun facteur sélectionné.")
            else:
                factor_df = pd.DataFrame(selected_factors)[["sous_bloc", "facteur", "niveau", "pourcentage"]]
                factor_df.columns = ["Sous-bloc", "Facteur", "Niveau", "%"]
                factor_df["%"] = factor_df["%"].map(lambda x: f"{x:.0f} %")
                st.dataframe(factor_df, width="stretch", hide_index=True)

        if raw_percent > cap_percent:
            st.warning(f"La majoration brute dépasse le plafond. Valeur plafonnée à {cap_percent} %.")

        if len(selected_factors) > 5:
            st.warning("Plus de 5 facteurs sont sélectionnés.")

        cadd, cdl = st.columns(2)

        with cadd:
            if st.button("Ajouter à la soumission", width="stretch"):
                st.session_state.quote_lines.append({
                    "Section": section,
                    "Famille": family,
                    "Tâche": task_name,
                    "Temps base (min)": base_minutes,
                    "Majoration brute (%)": raw_percent,
                    "Majoration appliquée (%)": applied_percent,
                    "Temps ajusté tâche (min)": round(adjusted_task_minutes, 1),
                    "Déplacement inclus": "Oui" if include_travel else "Non",
                    "Déplacement (min)": round(travel_minutes if include_travel else 0, 1),
                    "Déplacement (km)": round(travel_km if include_travel else 0, 1),
                    "Temps total (min)": round(total_with_travel, 1),
                    "Adresse bureau": OFFICE_ADDRESS,
                    "Adresse client": client_address,
                    "Commentaire": comment,
                })
                st.success("Ligne ajoutée à la soumission.")

        with cdl:
            payload = {
                "section": section,
                "famille": family,
                "tache": task_name,
                "temps_base_min": base_minutes,
                "majoration_brute_pct": raw_percent,
                "majoration_appliquee_pct": applied_percent,
                "temps_ajuste_tache_min": round(adjusted_task_minutes, 1),
                "deplacement_min": round(travel_minutes if include_travel else 0, 1),
                "deplacement_km": round(travel_km if include_travel else 0, 1),
                "temps_total_min": round(total_with_travel, 1),
                "facteurs": selected_factors,
                "adresse_bureau": OFFICE_ADDRESS,
                "adresse_client": client_address,
                "commentaire": comment,
            }

            st.download_button(
                "Télécharger le calcul (JSON)",
                data=json.dumps(payload, ensure_ascii=False, indent=2),
                file_name="calcul_surcout.json",
                mime="application/json",
                width="stretch"
            )

with tab_matrix:
    st.subheader("Référentiel — Matrice de calcul")
    selected_ref_family = st.selectbox("Famille à afficher", list(MATRIX.keys()), key="ref_family")
    render_family_reference(selected_ref_family)

with tab_quote:
    st.subheader("Soumission")
    if not st.session_state.quote_lines:
        st.info("Aucune ligne ajoutée pour le moment.")
    else:
        quote_df = pd.DataFrame(st.session_state.quote_lines)
        st.dataframe(quote_df, width="stretch", hide_index=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Temps de base total", f"{float(quote_df['Temps base (min)'].sum()):.1f} min")
        c2.metric("Déplacement total", f"{float(quote_df['Déplacement (min)'].sum()):.1f} min")
        c3.metric("Temps total soumission", f"{float(quote_df['Temps total (min)'].sum()):.1f} min")

        st.download_button(
            "Télécharger la soumission (CSV)",
            data=quote_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="soumission_surcouts.csv",
            mime="text/csv"
        )

        if st.button("Vider la soumission"):
            st.session_state.quote_lines = []
            st.rerun()