import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import norm

st.title("Nutrition CSV Analyzer with DII Score")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# Create a mapping for our columns to DII parameters
DII_COL_MAPPING = {
    "Alcohol (g)": "ALCOHOL_DII",
    "B12 (Cobalamin) (µg)": "VITB12_DII",
    "B6 (Pyridoxine) (mg)": "VITB6_DII",
    # Beta-carotene not in our data
    "Caffeine (mg)": "CAFFEINE_DII",
    "Carbs (g)": "CARB_DII",
    "Cholesterol (mg)": "CHOLES_DII",
    "Energy (kcal)": "KCAL_DII",
    # Eugenol not in our data
    "Fat (g)": "TOTALFAT_DII",
    "Fiber (g)": "FIBER_DII",
    "Folate (µg)": "FOLICACID_DII",
    # Garlic, Ginger not in our data
    "Iron (mg)": "IRON_DII",
    "Magnesium (mg)": "MG_DII",
    "Monounsaturated (g)": "MUFA_DII",
    "B3 (Niacin) (mg)": "NIACIN_DII",
    "Omega-3 (g)": "N3FAT_DII",
    "Omega-6 (g)": "N6FAT_DII",
    # Onion not in our data
    "Protein (g)": "PROTEIN_DII",
    "Polyunsaturated (g)": "PUFA_DII",
    "B2 (Riboflavin) (mg)": "RIBOFLAVIN_DII",
    # Saffron not in our data
    "Saturated (g)": "SATFAT_DII",
    "Selenium (µg)": "SE_DII",
    "B1 (Thiamine) (mg)": "THIAMIN_DII",
    "Trans-Fats (g)": "TRANSFAT_DII",
    # Turmeric not in our data
    "Vitamin A (µg)": "VITA_DII",
    "Vitamin C (mg)": "VITC_DII",
    "Vitamin D (IU)": "VITD_DII",  # Note: IU vs µg - need conversion
    "Vitamin E (mg)": "VITE_DII",
    "Zinc (mg)": "ZN_DII",
    # Tea not in our data
    # Flavonoids not in our data
    # Pepper, Thyme, Rosemary not in our data
}


def calculate_dii_score(df_row):
    """
    Calculate the Dietary Inflammatory Index (DII) score for a single row of nutrition data.
    Based on the DII.R implementation.
    """
    # Define the parameters from DII.R
    variables = [
        "ALCOHOL_DII",
        "VITB12_DII",
        "VITB6_DII",
        "BCAROTENE_DII",
        "CAFFEINE_DII",
        "CARB_DII",
        "CHOLES_DII",
        "KCAL_DII",
        "EUGENOL_DII",
        "TOTALFAT_DII",
        "FIBER_DII",
        "FOLICACID_DII",
        "GARLIC_DII",
        "GINGER_DII",
        "IRON_DII",
        "MG_DII",
        "MUFA_DII",
        "NIACIN_DII",
        "N3FAT_DII",
        "N6FAT_DII",
        "ONION_DII",
        "PROTEIN_DII",
        "PUFA_DII",
        "RIBOFLAVIN_DII",
        "SAFFRON_DII",
        "SATFAT_DII",
        "SE_DII",
        "THIAMIN_DII",
        "TRANSFAT_DII",
        "TURMERIC_DII",
        "VITA_DII",
        "VITC_DII",
        "VITD_DII",
        "VITE_DII",
        "ZN_DII",
        "TEA_DII",
        "FLA3OL_DII",
        "FLAVONES_DII",
        "FLAVONOLS_DII",
        "FLAVONONES_DII",
        "ANTHOC_DII",
        "ISOFLAVONES_DII",
        "PEPPER_DII",
        "THYME_DII",
        "ROSEMARY_DII",
    ]

    inflammatory_scores = [
        -0.278,
        0.106,
        -0.365,
        -0.584,
        -0.11,
        0.097,
        0.11,
        0.18,
        -0.14,
        0.298,
        -0.663,
        -0.19,
        -0.412,
        -0.453,
        0.032,
        -0.484,
        -0.009,
        -0.246,
        -0.436,
        -0.159,
        -0.301,
        0.021,
        -0.337,
        -0.068,
        -0.14,
        0.373,
        -0.191,
        -0.098,
        0.229,
        -0.785,
        -0.401,
        -0.424,
        -0.446,
        -0.419,
        -0.313,
        -0.536,
        -0.415,
        -0.616,
        -0.467,
        -0.25,
        -0.131,
        -0.593,
        -0.131,
        -0.102,
        -0.013,
    ]

    global_means = [
        13.98,
        5.15,
        1.47,
        3718,
        8.05,
        272.2,
        279.4,
        2056,
        0.01,
        71.4,
        18.8,
        273,
        4.35,
        59,
        13.35,
        310.1,
        27,
        25.9,
        1.06,
        10.8,
        35.9,
        79.4,
        13.88,
        1.7,
        0.37,
        28.6,
        67,
        1.7,
        3.15,
        533.6,
        983.9,
        118.2,
        6.26,
        8.73,
        9.84,
        1.69,
        95.8,
        1.55,
        17.7,
        11.7,
        18.05,
        1.2,
        10,
        0.33,
        1,
    ]

    sds = [
        3.72,
        2.7,
        0.74,
        1720,
        6.67,
        40,
        51.2,
        338,
        0.08,
        19.4,
        4.9,
        70.7,
        2.9,
        63.2,
        3.71,
        139.4,
        6.1,
        11.77,
        1.06,
        7.5,
        18.4,
        13.9,
        3.76,
        0.79,
        1.78,
        8,
        25.1,
        0.66,
        3.75,
        754.3,
        518.6,
        43.46,
        2.21,
        1.49,
        2.19,
        1.53,
        85.9,
        0.07,
        6.79,
        3.82,
        21.14,
        0.2,
        7.07,
        0.99,
        15,
    ]

    # Calculate individual DII scores
    individual_scores = {}
    for csv_col, dii_var in DII_COL_MAPPING.items():
        if csv_col in df_row:
            value = df_row[csv_col]
            # Get the index for this variable
            idx = variables.index(dii_var)

            # Special case for Vitamin D (convert IU to µg if needed)
            if csv_col == "Vitamin D (IU)":
                # Convert IU to µg (approximate conversion)
                value = value / 40.0

            # Calculate Z-score
            z_score = (value - global_means[idx]) / sds[idx]

            # Calculate percentile
            percentile = norm.cdf(z_score) * 2 - 1

            # Calculate individual DII score
            ind_score = percentile * inflammatory_scores[idx]

            individual_scores[dii_var] = ind_score
        else:
            individual_scores[dii_var] = 0

    # Sum all individual scores to get the total DII score
    total_dii = sum(individual_scores.values())

    return total_dii, individual_scores


if uploaded_file is not None:
    # Read the CSV file
    df = pd.read_csv(uploaded_file)

    # Display the dataframe
    st.subheader("Data Preview")
    st.dataframe(df.head())

    # Generate some basic statistics
    st.subheader("Data Summary")
    st.write(f"Number of rows: {df.shape[0]}")
    st.write(f"Number of columns: {df.shape[1]}")

    # Calculate DII score for each row
    if len(df) > 0:
        st.subheader("Dietary Inflammatory Index (DII) Score")
        
        # Check if we have multiple days
        has_multiple_days = 'Date' in df.columns and df['Date'].nunique() > 1
        
        if has_multiple_days:
            st.write("Multiple days detected! Showing DII scores by day and average.")
            
            # Create tabs for each day and average
            day_tabs = st.tabs(["Average"] + [f"Day {i+1}: {date}" for i, date in enumerate(df['Date'].unique())])
            
            # First tab is the average score
            with day_tabs[0]:
                # Calculate average scores
                all_days_scores = []
                all_days_components = {}
                
                for idx, row in df.iterrows():
                    day_dii, day_components = calculate_dii_score(row)
                    all_days_scores.append(day_dii)
                    
                    # Collect component scores for averaging
                    for comp, score in day_components.items():
                        if comp not in all_days_components:
                            all_days_components[comp] = []
                        all_days_components[comp].append(score)
                
                # Calculate average DII score
                avg_dii = sum(all_days_scores) / len(all_days_scores)
                
                # Calculate average component scores
                avg_components = {comp: sum(scores)/len(scores) for comp, scores in all_days_components.items()}
                
                # Display average score
                if avg_dii < -1:
                    score_color = "green"
                    interpretation = "Anti-inflammatory"
                elif avg_dii < 1:
                    score_color = "orange" 
                    interpretation = "Neutral"
                else:
                    score_color = "red"
                    interpretation = "Pro-inflammatory"
                    
                st.markdown(f"**Average DII Score:** <span style='color:{score_color};font-size:1.5em;'>{avg_dii:.2f}</span> ({interpretation})", unsafe_allow_html=True)
                
                # Show which components contributed most
                st.write("**Top Contributors (Average):**")
                
                # Get non-zero components
                nonzero_components = {k: v for k, v in avg_components.items() if v != 0}
                
                # Sort by absolute value to get the most influential components
                sorted_components = sorted(nonzero_components.items(), key=lambda x: abs(x[1]), reverse=True)
                
                # Display top 5 contributors
                for i, (component, score) in enumerate(sorted_components[:5]):
                    # Reverse lookup in the mapping dictionary
                    friendly_name = next((k for k, v in DII_COL_MAPPING.items() if v == component), component)
                    effect = "anti-inflammatory" if score < 0 else "pro-inflammatory"
                    st.write(f"{i+1}. {friendly_name}: {score:.3f} ({effect})")
            
            # Tabs for individual days
            for i, date in enumerate(df['Date'].unique()):
                with day_tabs[i+1]:
                    day_data = df[df['Date'] == date].iloc[0]
                    day_dii, day_components = calculate_dii_score(day_data)
                    
                    # Format the score with color
                    if day_dii < -1:
                        score_color = "green"
                        interpretation = "Anti-inflammatory"
                    elif day_dii < 1:
                        score_color = "orange"
                        interpretation = "Neutral"
                    else:
                        score_color = "red"
                        interpretation = "Pro-inflammatory"
                        
                    st.markdown(f"**DII Score:** <span style='color:{score_color};font-size:1.5em;'>{day_dii:.2f}</span> ({interpretation})", unsafe_allow_html=True)
                    
                    # Show which components contributed most
                    st.write("**Top Contributors:**")
                    
                    # Get non-zero components
                    nonzero_components = {k: v for k, v in day_components.items() if v != 0}
                    
                    # Sort by absolute value to get the most influential components
                    sorted_components = sorted(nonzero_components.items(), key=lambda x: abs(x[1]), reverse=True)
                    
                    # Display top 5 contributors
                    for j, (component, score) in enumerate(sorted_components[:5]):
                        # Reverse lookup in the mapping dictionary
                        friendly_name = next((k for k, v in DII_COL_MAPPING.items() if v == component), component)
                        effect = "anti-inflammatory" if score < 0 else "pro-inflammatory"
                        st.write(f"{j+1}. {friendly_name}: {score:.3f} ({effect})")
        else:
            # Single day processing
            for idx, row in df.iterrows():
                total_dii, component_scores = calculate_dii_score(row)
                
                # Format the score with color
                if total_dii < -1:
                    score_color = "green"
                    interpretation = "Anti-inflammatory"
                elif total_dii < 1:
                    score_color = "orange"
                    interpretation = "Neutral"
                else:
                    score_color = "red"
                    interpretation = "Pro-inflammatory"
                    
                st.markdown(f"**DII Score:** <span style='color:{score_color};font-size:1.5em;'>{total_dii:.2f}</span> ({interpretation})", unsafe_allow_html=True)
                
                # Show which components contributed most
                st.write("**Top Contributors:**")
                
                # Get non-zero components
                nonzero_components = {k: v for k, v in component_scores.items() if v != 0}
                
                # Sort by absolute value to get the most influential components
                sorted_components = sorted(nonzero_components.items(), key=lambda x: abs(x[1]), reverse=True)
                
                # Display top 5 contributors
                for i, (component, score) in enumerate(sorted_components[:5]):
                    # Reverse lookup in the mapping dictionary
                    friendly_name = next((k for k, v in DII_COL_MAPPING.items() if v == component), component)
                    effect = "anti-inflammatory" if score < 0 else "pro-inflammatory"
                    st.write(f"{i+1}. {friendly_name}: {score:.3f} ({effect})")

    # # Column statistics
    # st.subheader("Column Information")
    # for column in df.columns:
    #     st.write(f"**{column}**")

    #     # Check if column is numeric
    #     if pd.api.types.is_numeric_dtype(df[column]):
    #         st.write(f"- Mean: {df[column].mean():.2f}")
    #         st.write(f"- Min: {df[column].min()}")
    #         st.write(f"- Max: {df[column].max()}")
    #     else:
    #         # For non-numeric columns, show unique values count
    #         st.write(f"- Unique values: {df[column].nunique()}")
    #         if df[column].nunique() < 10:  # Only show all values if there aren't too many
    #             st.write(f"- Values: {', '.join(str(x) for x in df[column].unique())}")
