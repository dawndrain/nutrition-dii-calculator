import streamlit as st
import pandas as pd
from scipy.stats import norm
import plotly.express as px

from dii_calculation import calculate_dii_score, CRONOMETER_DII_MAPPING, get_dii_param_details

st.title("Nutrition CSV Analyzer with DII Score")

# File upload section with source selection
st.subheader("Upload Data")
st.write("See https://github.com/dawndrain/nutrition-dii-calculator/blob/main/README.md for instructions on exporting data from Cronometer and MyFitnessPal, along with a couple example csv files.")

col1, col2 = st.columns([3, 1])
with col1:
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
with col2:
    data_source = st.selectbox(
        "Data Source",
        ["Cronometer", "MyFitnessPal"],
        help="Select the source of your CSV file"
    )


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
