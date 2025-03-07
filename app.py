import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import norm
import plotly.express as px

st.title("Nutrition CSV Analyzer with DII Score")

# File upload section with source selection
st.subheader("Upload Data")
col1, col2 = st.columns([3, 1])
with col1:
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
with col2:
    data_source = st.selectbox(
        "Data Source",
        ["Cronometer", "MyFitnessPal"],
        help="Select the source of your CSV file"
    )




# Define DII parameters as tuples (variable_name, inflammatory_score, global_mean, standard_deviation)
# Sorted from most pro-inflammatory (positive score) to most anti-inflammatory (negative score)
DII_PARAMS = [
    # most pro-inflammatory
    ("SATFAT_DII", 0.373, 28.6, 8),       # Saturated fat - found in animal products, increases inflammatory markers and risk of heart disease
    ("TOTALFAT_DII", 0.298, 71.4, 19.4),  # Total fat consumption - high amounts may promote inflammation, especially from unhealthy sources
    ("TRANSFAT_DII", 0.229, 3.15, 3.75),  # Trans fats - artificial fats in processed foods that strongly promote inflammation
    ("KCAL_DII", 0.18, 2056, 338),        # Total calories - excess caloric intake can lead to metabolic inflammation
    ("CHOLES_DII", 0.11, 279.4, 51.2),    # Dietary cholesterol - may contribute to inflammation in some individuals
    ("VITB12_DII", 0.106, 5.15, 2.7),     # Vitamin B12 - though essential, can be mildly pro-inflammatory in some contexts
    ("CARB_DII", 0.097, 272.2, 40),       # Carbohydrates - particularly refined carbs can raise blood sugar and promote inflammation
    
    # neutral
    ("IRON_DII", 0.032, 13.35, 3.71),     # Iron - essential mineral with minimal inflammatory impact
    ("PROTEIN_DII", 0.021, 79.4, 13.9),   # Protein - generally neutral, though source matters (plant vs animal)
    ("MUFA_DII", -0.009, 27, 6.1),        # Monounsaturated fatty acids - found in olive oil, avocados; slightly anti-inflammatory
    ("ROSEMARY_DII", -0.013, 1, 15),      # Rosemary - herb with minimal anti-inflammatory properties
    ("RIBOFLAVIN_DII", -0.068, 1.7, 0.79), # Vitamin B2 - mild anti-inflammatory effects
    ("THIAMIN_DII", -0.098, 1.7, 0.66),   # Vitamin B1 - slight anti-inflammatory properties
    
    # mildly anti-inflammatory
    ("THYME_DII", -0.102, 0.33, 0.99),    # Thyme - herb containing anti-inflammatory compounds
    ("CAFFEINE_DII", -0.11, 8.05, 6.67),  # Caffeine - moderate consumption can reduce certain inflammatory markers
    ("ANTHOC_DII", -0.131, 18.05, 21.14), # Anthocyanins - plant compounds in berries with anti-inflammatory effects
    ("PEPPER_DII", -0.131, 10, 7.07),     # Black pepper - contains piperine which has anti-inflammatory properties
    ("EUGENOL_DII", -0.14, 0.01, 0.08),   # Eugenol - compound in cloves and cinnamon with anti-inflammatory effects
    ("SAFFRON_DII", -0.14, 0.37, 1.78),   # Saffron - spice with antioxidant and anti-inflammatory properties
    ("N6FAT_DII", -0.159, 10.8, 7.5),     # Omega-6 fatty acids - in moderate amounts, can have anti-inflammatory effects
    ("FOLICACID_DII", -0.19, 273, 70.7),  # Folate/Folic acid - B vitamin that helps reduce inflammation
    ("SE_DII", -0.191, 67, 25.1),         # Selenium - mineral with antioxidant properties that reduce inflammation
    ("NIACIN_DII", -0.246, 25.9, 11.77),  # Vitamin B3 - reduces inflammatory markers and improves lipid profiles
    ("FLAVONONES_DII", -0.25, 11.7, 3.82), # Flavanones - compounds in citrus fruits with anti-inflammatory properties
    ("ALCOHOL_DII", -0.278, 13.98, 3.72), # Alcohol - moderate consumption may have anti-inflammatory effects (though excess is harmful)
    
    # moderately anti-inflammatory
    ("ONION_DII", -0.301, 35.9, 18.4),    # Onions - contain quercetin and sulfur compounds that reduce inflammation
    ("ZN_DII", -0.313, 9.84, 2.19),       # Zinc - essential mineral that regulates immune function and reduces inflammation
    ("PUFA_DII", -0.337, 13.88, 3.76),    # Polyunsaturated fatty acids - found in nuts, seeds, fish; reduce inflammatory markers
    ("VITB6_DII", -0.365, 1.47, 0.74),    # Vitamin B6 - supports immune function and helps control inflammation
    ("VITA_DII", -0.401, 983.9, 518.6),   # Vitamin A - powerful anti-inflammatory that regulates immune response
    ("GARLIC_DII", -0.412, 4.35, 2.9),    # Garlic - contains sulfur compounds with strong anti-inflammatory effects
    ("FLA3OL_DII", -0.415, 95.8, 85.9),   # Flavan-3-ols - compounds in tea, cocoa, and berries that reduce inflammation
    ("VITE_DII", -0.419, 8.73, 1.49),     # Vitamin E - potent antioxidant that protects cells from inflammatory damage
    ("VITC_DII", -0.424, 118.2, 43.46),   # Vitamin C - reduces inflammation and supports immune function
    ("N3FAT_DII", -0.436, 1.06, 1.06),    # Omega-3 fatty acids - powerful anti-inflammatory fats found in fish, flax, walnuts
    ("VITD_DII", -0.446, 6.26, 2.21),     # Vitamin D - regulates immune response and has strong anti-inflammatory effects
    
    # strongly anti-inflammatory
    ("GINGER_DII", -0.453, 59, 63.2),     # Ginger - contains gingerols that block inflammatory pathways
    ("FLAVONOLS_DII", -0.467, 17.7, 6.79), # Flavonols - antioxidants in plants that significantly reduce inflammation
    ("MG_DII", -0.484, 310.1, 139.4),     # Magnesium - mineral that reduces production of inflammatory cytokines
    ("TEA_DII", -0.536, 1.69, 1.53),      # Tea - especially green tea, contains catechins with strong anti-inflammatory effects
    ("BCAROTENE_DII", -0.584, 3718, 1720), # Beta-carotene - powerful antioxidant in orange/yellow foods that reduces inflammation
    ("ISOFLAVONES_DII", -0.593, 1.2, 0.2), # Isoflavones - compounds in soy and legumes with potent anti-inflammatory effects
    ("FLAVONES_DII", -0.616, 1.55, 0.07), # Flavones - plant compounds in herbs and vegetables with strong anti-inflammatory properties
    ("FIBER_DII", -0.663, 18.8, 4.9),     # Fiber - supports gut health and strongly reduces systemic inflammation
    ("TURMERIC_DII", -0.785, 533.6, 754.3), # Turmeric - contains curcumin, one of the most potent natural anti-inflammatory compounds
]


def get_dii_param_details():
    """Get DII parameters and organize them for lookup access"""
    # Define DII parameters: (name, inflammatory_score, global_mean, sd)
    return {param[0]: param for param in DII_PARAMS}


# Create mappings for our columns to DII parameters based on data source
CRONOMETER_DII_MAPPING = {
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

# MyFitnessPal has different column names
MYFITNESSPAL_DII_MAPPING = {
    "Calories": "KCAL_DII",
    "Fat (g)": "TOTALFAT_DII",
    "Saturated Fat": "SATFAT_DII",
    "Polyunsaturated Fat": "PUFA_DII",
    "Monounsaturated Fat": "MUFA_DII",
    "Trans Fat": "TRANSFAT_DII",
    "Cholesterol": "CHOLES_DII",
    "Sodium (mg)": "SODIUM_DII",  # Not used in DII calculation but might be added later
    "Potassium": "POTASSIUM_DII", # Not used in DII calculation but might be added later
    "Carbohydrates (g)": "CARB_DII",
    "Fiber": "FIBER_DII",
    "Sugar": "SUGAR_DII",         # Not directly used in DII calculation
    "Protein (g)": "PROTEIN_DII",
    "Vitamin A": "VITA_DII",      # % RDA, converted in calculation
    "Vitamin C": "VITC_DII",      # % RDA, converted in calculation
    "Calcium": "CALCIUM_DII",     # % RDA, not directly used in DII calculation
    "Iron": "IRON_DII"            # % RDA, converted in calculation
}


def calculate_dii_score(df_row, data_source="Cronometer"):
    """
    Calculate the Dietary Inflammatory Index (DII) score for a single row of nutrition data.
    Based on the DII.R implementation.
    
    Args:
        df_row: DataFrame row containing nutrition data
        data_source: Source of the data ('Cronometer' or 'MyFitnessPal')
    """
    # Create a dictionary for faster lookup
    dii_param_dict = get_dii_param_details()
    
    # Select the appropriate column mapping based on data source
    if data_source == "Cronometer":
        column_mapping = CRONOMETER_DII_MAPPING
    else:  # MyFitnessPal
        column_mapping = MYFITNESSPAL_DII_MAPPING

    # Since we now log columns at the dataframe level, we don't need to do it again here
    
    # Calculate individual DII scores
    individual_scores = {}
    for csv_col, dii_var in column_mapping.items():
        if csv_col in df_row:
            value = df_row[csv_col]
            
            # Skip null or non-numeric values
            if pd.isna(value) or not isinstance(value, (int, float)):
                individual_scores[dii_var] = 0
                continue

            # Skip if this parameter isn't in our dictionary
            if dii_var not in dii_param_dict:
                individual_scores[dii_var] = 0
                continue

            # Get the parameters
            _, inflam_score, global_mean, sd = dii_param_dict[dii_var]

            # Special case for Vitamin D (convert IU to µg if needed)
            if csv_col == "Vitamin D (IU)":
                # Convert IU to µg (approximate conversion)
                value = value / 40.0
                
            # MyFitnessPal-specific unit conversions
            if data_source == "MyFitnessPal":
                # MyFitnessPal uses % RDA for vitamins and some minerals
                if csv_col == "Vitamin A":  # Percentage
                    # Convert % RDA to µg RAE (100% RDA ≈ 900 µg RAE)
                    value = value * 9
                if csv_col == "Vitamin C":  # Percentage 
                    # Convert % RDA to mg (100% RDA ≈ 90 mg)
                    value = value * 0.9
                if csv_col == "Calcium":  # Percentage
                    # Convert % RDA to mg (100% RDA ≈ 1000 mg)
                    value = value * 10
                if csv_col == "Iron":  # Percentage
                    # Convert % RDA to mg (100% RDA ≈ 18 mg)
                    value = value * 0.18
                # Potassium is already in mg so no conversion needed

            # Calculate Z-score
            z_score = (value - global_mean) / sd

            # Calculate percentile
            percentile = norm.cdf(z_score) * 2 - 1

            # Calculate individual DII score
            ind_score = percentile * inflam_score

            individual_scores[dii_var] = ind_score
        else:
            individual_scores[dii_var] = 0

    # Sum all individual scores to get the total DII score
    total_dii = sum(individual_scores.values())

    return total_dii, individual_scores



def visualize_dii_components(row, dii_score, component_scores, data_source="Cronometer"):
    """
    Create a detailed visualization of DII score components

    Args:
        row: DataFrame row containing nutrition data
        dii_score: Calculated DII score
        component_scores: Dictionary of component scores
        data_source: Source of the data ('Cronometer' or 'MyFitnessPal')

    Returns:
        None (displays visualization in Streamlit)
    """
    # Format the score with color
    if dii_score < -1:
        score_color = "green"
        interpretation = "Anti-inflammatory"
    elif dii_score < 1:
        score_color = "orange"
        interpretation = "Neutral"
    else:
        score_color = "red"
        interpretation = "Pro-inflammatory"

    st.markdown(
        f"**DII Score:** <span style='color:{score_color};font-size:1.5em;'>{dii_score:.2f}</span> ({interpretation})",
        unsafe_allow_html=True,
    )

    # Get DII parameter details
    dii_params = get_dii_param_details()

    # Show enhanced components visualization
    st.subheader("Top Contributors to DII Score")

    # Get non-zero components
    nonzero_components = {k: v for k, v in component_scores.items() if v != 0}

    # Sort by absolute value to get the most influential components
    sorted_components = sorted(
        nonzero_components.items(), key=lambda x: abs(x[1]), reverse=True
    )

    # Prepare detailed component information
    detailed_components = []
    for component, score in sorted_components[:10]:  # Top 10 components
        # Get parameter details
        param_details = dii_params.get(component)
        if not param_details:
            continue

        # Extract details
        _, infl_weight, global_mean, sd = param_details
        
        # Get the appropriate column mapping based on the data source
        if "data_source" not in locals():
            data_source = "Cronometer"  # Default
            
        col_mapping = CRONOMETER_DII_MAPPING if data_source == "Cronometer" else MYFITNESSPAL_DII_MAPPING
        
        friendly_name = next(
            (k for k, v in col_mapping.items() if v == component), component
        )

        # Get actual value from dataframe
        actual_value = row.get(friendly_name) if friendly_name in row else None

        # Special case for Vitamin D (convert to µg for comparison)
        if friendly_name == "Vitamin D (IU)" and actual_value is not None:
            actual_value_comp = actual_value / 40.0
        else:
            actual_value_comp = actual_value

        # Calculate z-score to determine if above/below global mean
        z_score = None
        if actual_value_comp is not None and sd > 0:
            z_score = (actual_value_comp - global_mean) / sd

        # Determine if counter-intuitive
        counter_intuitive = False
        if (infl_weight < 0 and score > 0) or (infl_weight > 0 and score < 0):
            counter_intuitive = True

        # Calculate percentage of total score
        pct_of_total = 0
        if dii_score != 0:
            pct_of_total = (abs(score) / abs(dii_score)) * 100

        detailed_components.append(
            {
                "component": component,
                "friendly_name": friendly_name,
                "score": score,
                "infl_weight": infl_weight,
                "global_mean": global_mean,
                "actual_value": actual_value,
                "z_score": z_score,
                "counter_intuitive": counter_intuitive,
                "pct_of_total": pct_of_total,
            }
        )

    # Create a DataFrame for tabular display
    df_components = pd.DataFrame(detailed_components)

    # First show the bar chart at full width
    chart_data = df_components.sort_values(by="score")
    chart_data = chart_data[["friendly_name", "score"]].rename(
        columns={"friendly_name": "Nutrient", "score": "Impact"}
    )

    # Create enhanced bar chart with directional indicators
    st.subheader("DII Component Impact")
    if not chart_data.empty:
        # Create a new column for the y-axis labels with directional arrows
        enhanced_labels = []

        for idx, row in chart_data.iterrows():
            # Find the component details
            component_name = row["Nutrient"]
            impact = row["Impact"]

            # Find the corresponding detailed component
            component_details = next(
                (
                    c
                    for c in detailed_components
                    if c["friendly_name"] == component_name
                ),
                None,
            )

            if component_details:
                # Get nutrient's inherent property (anti-inflammatory or pro-inflammatory)
                if component_details["infl_weight"] < 0:
                    # Inherently anti-inflammatory - down arrow
                    label = f"{component_name} ↓"
                else:
                    # Inherently pro-inflammatory - up arrow
                    label = f"{component_name} ↑"
            else:
                # Fallback if detailed info not found
                label = component_name

            enhanced_labels.append(label)

        # Update the chart data with the enhanced labels
        chart_data_enhanced = chart_data.copy()
        chart_data_enhanced["Enhanced_Nutrient"] = enhanced_labels

        # Create an information box to explain the arrows
        st.info("""
        **Understanding the arrows:**
        - **↑** means the nutrient is inherently pro-inflammatory (e.g., saturated fat)
        - **↓** means the nutrient is inherently anti-inflammatory (e.g., fiber, omega-3)
        
        The bar colors show whether your intake is currently increasing (red) or decreasing (green) inflammation.
        """)

        # Create the bar chart with enhanced labels
        fig = px.bar(
            chart_data_enhanced,
            x="Impact",
            y="Enhanced_Nutrient",
            orientation="h",
            color="Impact",
            color_continuous_scale=["green", "white", "red"],
            range_color=[
                -max(abs(chart_data["Impact"])),
                max(abs(chart_data["Impact"])),
            ],
        )

        # Update layout for better visualization
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=30, b=30),
            yaxis=dict(tickfont=dict(size=14), title=None),
            xaxis=dict(title=dict(text="Impact on Inflammation", font=dict(size=14))),
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Then add the detailed analysis
    rows = []
    for comp in detailed_components:
        # Create directional indicators
        if comp["infl_weight"] < 0:
            infl_direction = "↓"  # This nutrient generally reduces inflammation
            infl_type = "Anti-inflammatory"
        else:
            infl_direction = "↑"  # This nutrient generally increases inflammation
            infl_type = "Pro-inflammatory"

        if comp["z_score"] is not None and comp["z_score"] > 0:
            amount_direction = "Above"  # Eating more than average
        else:
            amount_direction = "Below"  # Eating less than average

        if comp["score"] < 0:
            effect_direction = "↓"  # Net anti-inflammatory effect
            effect = "Reducing"
        else:
            effect_direction = "↑"  # Net pro-inflammatory effect
            effect = "Increasing"

        # Generate recommendation
        if comp["counter_intuitive"]:
            if comp["infl_weight"] < 0 and comp["score"] > 0:
                # Anti-inflammatory nutrient causing pro-inflammatory effect
                recommendation = f"Increase intake (currently below global average)"
                action_color = "orange"
            else:
                # Pro-inflammatory nutrient causing anti-inflammatory effect
                recommendation = f"Continue limiting intake (below global average)"
                action_color = "green"
        else:
            if comp["infl_weight"] < 0 and comp["score"] < 0:
                # Anti-inflammatory nutrient with anti-inflammatory effect
                recommendation = f"Continue current intake (above global average)"
                action_color = "green"
            else:
                # Pro-inflammatory nutrient with pro-inflammatory effect
                recommendation = f"Consider reducing intake (above global average)"
                action_color = "red"

        # Format percent contribution
        pct = f"{comp['pct_of_total']:.1f}%" if comp["pct_of_total"] > 0 else "N/A"

        # Add row to table
        rows.append(
            {
                "Nutrient": comp["friendly_name"],
                "Your Value": f"{comp['actual_value']:.1f}"
                if comp["actual_value"] is not None
                else "N/A",
                "Avg Value": f"{comp['global_mean']:.1f}",
                "Type": infl_type,
                "Net Effect": effect,
                "Impact": f"{abs(comp['score']):.3f}",
                "% of Total": pct,
                "Recommendation": recommendation,
                "action_color": action_color,
            }
        )

    # Create DataFrame for display
    df_display = pd.DataFrame(rows)

    # Add legend
    st.subheader("DII Component Analysis")
    st.markdown("""
    **Understanding the components:**
    - **Type**: Whether a nutrient is inherently pro-inflammatory or anti-inflammatory
    - **Your Value**: Your intake compared to global average
    - **Net Effect**: Whether your intake is increasing or reducing inflammation
    - **Impact**: Magnitude of effect on your DII score
    - **% of Total**: How much this nutrient contributes to your total score
    """)

    # Display top components with more details (using expanders to save space)
    for i, row in df_display.iterrows():
        if i < 5:
            # Show top 5 contributors with more details
            with st.container():
                col1, col2 = st.columns([3, 7])
                with col1:
                    st.subheader(f"{i+1}. {row['Nutrient']}")
                    st.write(f"**Type:** {row['Type']}")
                with col2:
                    col2a, col2b = st.columns(2)
                    with col2a:
                        st.write(
                            f"**Your value:** {row['Your Value']} (Avg: {row['Avg Value']})"
                        )
                        st.write(f"**Effect:** {row['Net Effect']} inflammation")
                    with col2b:
                        st.write(f"**Impact:** {row['Impact']} ({row['% of Total']})")
                        st.markdown(
                            f"**Recommendation:** <span style='color:{row['action_color']};'>{row['Recommendation']}</span>",
                            unsafe_allow_html=True,
                        )
                st.markdown("---")
        else:
            # Use expanders for remaining components to save space
            with st.expander(
                f"{i+1}. {row['Nutrient']} - Impact: {row['Impact']} ({row['% of Total']})"
            ):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Type:** {row['Type']}")
                    st.write(
                        f"**Your value:** {row['Your Value']} (Avg: {row['Avg Value']})"
                    )
                with col2:
                    st.write(f"**Effect:** {row['Net Effect']} inflammation")
                    st.markdown(
                        f"**Recommendation:** <span style='color:{row['action_color']};'>{row['Recommendation']}</span>",
                        unsafe_allow_html=True,
                    )


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
    
    # Pre-process data for MyFitnessPal format if needed
    if data_source == "MyFitnessPal" and "Meal" in df.columns:
        st.info("Processing MyFitnessPal data format.")
        
        # Group by date and sum all nutrients
        # This handles the meal-by-meal breakdown in MyFitnessPal exports
        df = df.groupby("Date").sum().reset_index()
        
        # Drop non-numeric columns except Date
        for col in df.columns:
            if col != "Date" and not pd.api.types.is_numeric_dtype(df[col]):
                df = df.drop(columns=[col])
        
        st.write("Data aggregated by day from meal-level entries.")

    # Calculate DII score for each row
    if len(df) > 0:
        st.subheader("Dietary Inflammatory Index (DII) Score")
        
        # Check for unrecognized columns to help with debugging
        unrecognized_columns = []
        recognized_columns = []
        
        # Select the appropriate column mapping
        if data_source == "Cronometer":
            column_mapping = CRONOMETER_DII_MAPPING
        else:  # MyFitnessPal
            column_mapping = MYFITNESSPAL_DII_MAPPING
            
        # Get list of all column mappings
        all_mapped_columns = list(column_mapping.keys())
        
        # Check for columns in the data that aren't in our mapping
        for col in df.columns:
            if col in all_mapped_columns:
                recognized_columns.append(col)
            elif pd.api.types.is_numeric_dtype(df[col]) and col not in ["Date", "Meal", "Note", "Completed"]:
                unrecognized_columns.append(col)
                
        # Log recognized and unrecognized columns
        st.write(f"Using {len(recognized_columns)} nutrients for DII calculation")
        
        if unrecognized_columns and len(unrecognized_columns) > 0:
            with st.expander("Show unused nutrient columns"):
                st.info(f"Found {len(unrecognized_columns)} nutrient columns not used in DII calculation: {', '.join(unrecognized_columns[:10])}{' and more...' if len(unrecognized_columns) > 10 else ''}")
        
        # Check if we have multiple days
        has_multiple_days = "Date" in df.columns and df["Date"].nunique() > 1

        if has_multiple_days:
            st.write("Multiple days detected! Showing DII scores by day and average.")

            # Create tabs for each day and average
            day_tabs = st.tabs(
                ["Average"]
                + [f"Day {i+1}: {date}" for i, date in enumerate(df["Date"].unique())]
            )

            # First tab is the average score
            with day_tabs[0]:
                # Calculate average scores
                all_days_scores = []
                all_days_components = {}

                for idx, row in df.iterrows():
                    day_dii, day_components = calculate_dii_score(row, data_source)
                    all_days_scores.append(day_dii)

                    # Collect component scores for averaging
                    for comp, score in day_components.items():
                        if comp not in all_days_components:
                            all_days_components[comp] = []
                        all_days_components[comp].append(score)

                # Calculate average DII score
                avg_dii = sum(all_days_scores) / len(all_days_scores)

                # Calculate average component scores
                avg_components = {
                    comp: sum(scores) / len(scores)
                    for comp, scores in all_days_components.items()
                }

                # Create a "pseudo-row" with average values for visualization
                avg_row = {}

                # Get a list of all columns from the first row
                if len(df) > 0:
                    first_row = df.iloc[0]

                    # Calculate averages for each column
                    for col in first_row.index:
                        if col != "Date" and pd.api.types.is_numeric_dtype(df[col]):
                            avg_row[col] = df[col].mean()

                # Use the visualization function with avg_components
                visualize_dii_components(avg_row, avg_dii, avg_components, data_source)

            # Tabs for individual days
            for i, date in enumerate(df["Date"].unique()):
                with day_tabs[i + 1]:
                    day_data = df[df["Date"] == date].iloc[0]
                    day_dii, day_components = calculate_dii_score(day_data, data_source)

                    # Use the visualization function
                    visualize_dii_components(day_data, day_dii, day_components, data_source)
        else:
            # Single day processing
            for idx, row in df.iterrows():
                total_dii, component_scores = calculate_dii_score(row, data_source)

                # Use the visualization function
                visualize_dii_components(row, total_dii, component_scores, data_source)
