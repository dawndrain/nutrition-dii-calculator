import pandas as pd
import numpy as np
from scipy.stats import norm
import os
import sys
from app import calculate_dii_score, DII_COL_MAPPING

def get_dii_param_details():
    """Get DII parameters and organize them for lookup access"""
    # Define DII parameters: (name, inflammatory_score, global_mean, sd)
    dii_params = [
        ("ALCOHOL_DII", -0.278, 13.98, 3.72),
        ("VITB12_DII", 0.106, 5.15, 2.7),
        ("VITB6_DII", -0.365, 1.47, 0.74),
        ("BCAROTENE_DII", -0.584, 3718, 1720),
        ("CAFFEINE_DII", -0.11, 8.05, 6.67),
        ("CARB_DII", 0.097, 272.2, 40),
        ("CHOLES_DII", 0.11, 279.4, 51.2),
        ("KCAL_DII", 0.18, 2056, 338),
        ("EUGENOL_DII", -0.14, 0.01, 0.08),
        ("TOTALFAT_DII", 0.298, 71.4, 19.4),
        ("FIBER_DII", -0.663, 18.8, 4.9),
        ("FOLICACID_DII", -0.19, 273, 70.7),
        ("GARLIC_DII", -0.412, 4.35, 2.9),
        ("GINGER_DII", -0.453, 59, 63.2),
        ("IRON_DII", 0.032, 13.35, 3.71),
        ("MG_DII", -0.484, 310.1, 139.4),
        ("MUFA_DII", -0.009, 27, 6.1),
        ("NIACIN_DII", -0.246, 25.9, 11.77),
        ("N3FAT_DII", -0.436, 1.06, 1.06),
        ("N6FAT_DII", -0.159, 10.8, 7.5),
        ("ONION_DII", -0.301, 35.9, 18.4),
        ("PROTEIN_DII", 0.021, 79.4, 13.9),
        ("PUFA_DII", -0.337, 13.88, 3.76),
        ("RIBOFLAVIN_DII", -0.068, 1.7, 0.79),
        ("SAFFRON_DII", -0.14, 0.37, 1.78),
        ("SATFAT_DII", 0.373, 28.6, 8),
        ("SE_DII", -0.191, 67, 25.1),
        ("THIAMIN_DII", -0.098, 1.7, 0.66),
        ("TRANSFAT_DII", 0.229, 3.15, 3.75),
        ("TURMERIC_DII", -0.785, 533.6, 754.3),
        ("VITA_DII", -0.401, 983.9, 518.6),
        ("VITC_DII", -0.424, 118.2, 43.46),
        ("VITD_DII", -0.446, 6.26, 2.21),
        ("VITE_DII", -0.419, 8.73, 1.49),
        ("ZN_DII", -0.313, 9.84, 2.19),
        ("TEA_DII", -0.536, 1.69, 1.53),
        ("FLA3OL_DII", -0.415, 95.8, 85.9),
        ("FLAVONES_DII", -0.616, 1.55, 0.07),
        ("FLAVONOLS_DII", -0.467, 17.7, 6.79),
        ("FLAVONONES_DII", -0.25, 11.7, 3.82),
        ("ANTHOC_DII", -0.131, 18.05, 21.14),
        ("ISOFLAVONES_DII", -0.593, 1.2, 0.2),
        ("PEPPER_DII", -0.131, 10, 7.07),
        ("THYME_DII", -0.102, 0.33, 0.99),
        ("ROSEMARY_DII", -0.013, 1, 15)
    ]
    return {param[0]: param for param in dii_params}

def test_dii_calculation():
    """
    Test the DII score calculation using the dailysummary.csv file.
    This lets us verify that the Python implementation matches the expected behavior.
    """
    # Load the test data
    csv_path = os.path.join(os.path.dirname(__file__), "dailysummary.csv")
    df = pd.read_csv(csv_path)
    
    if len(df) == 0:
        print("Error: No data found in dailysummary.csv")
        return False
    
    # Get DII parameter details for analysis
    dii_params = get_dii_param_details()
    
    # Reverse mapping to get CSV column names from DII variables
    reverse_col_mapping = {v: k for k, v in DII_COL_MAPPING.items()}
    
    # Calculate DII score for each row
    results = []
    for idx, row in df.iterrows():
        total_dii, component_scores = calculate_dii_score(row)
        
        # Collect detailed component information
        detailed_components = []
        for component, score in component_scores.items():
            if score == 0:
                continue  # Skip zero-impact components
                
            # Get the parameter details
            param_details = dii_params.get(component)
            if not param_details:
                continue
                
            _, infl_weight, global_mean, sd = param_details
            friendly_name = reverse_col_mapping.get(component, component)
            
            # Get actual value from CSV
            csv_col = reverse_col_mapping.get(component)
            actual_value = row.get(csv_col) if csv_col in row else None
            
            # Special case for Vitamin D (convert to µg for comparison)
            if csv_col == "Vitamin D (IU)" and actual_value is not None:
                actual_value = actual_value / 40.0
                
            # Calculate z-score to determine if above/below global mean
            z_score = None
            if actual_value is not None and sd > 0:
                z_score = (actual_value - global_mean) / sd
                
            # Calculate percentile for normalization (as in DII calculation)
            percentile = None
            if z_score is not None:
                percentile = norm.cdf(z_score) * 2 - 1
                
            # Determine if the score is counter-intuitive
            counter_intuitive = False
            if (infl_weight < 0 and score > 0) or (infl_weight > 0 and score < 0):
                counter_intuitive = True
                
            # Calculate percentage of total score
            pct_of_total = 0
            if total_dii != 0:
                pct_of_total = (score / abs(total_dii)) * 100
                
            detailed_components.append({
                "component": component,
                "friendly_name": friendly_name,
                "score": score,
                "infl_weight": infl_weight,
                "global_mean": global_mean,
                "actual_value": actual_value,
                "z_score": z_score,
                "percentile": percentile,
                "counter_intuitive": counter_intuitive,
                "pct_of_total": pct_of_total
            })
            
        # Sort by absolute score
        detailed_components.sort(key=lambda x: abs(x["score"]), reverse=True)
            
        # Get interpretation
        if total_dii < -1:
            interpretation = "Anti-inflammatory"
        elif total_dii < 1:
            interpretation = "Neutral"
        else:
            interpretation = "Pro-inflammatory"
            
        results.append({
            "date": row.get("Date", f"Row {idx}"),
            "dii_score": total_dii,
            "interpretation": interpretation,
            "detailed_components": detailed_components
        })
    
    # Print the results
    for result in results:
        print(f"\nDate: {result['date']}")
        print(f"DII Score: {result['dii_score']:.2f} ({result['interpretation']})")
        
        print("\nTop 10 Contributors by Impact (absolute value):")
        print("-" * 90)
        print(f"{'Nutrient':<20} {'Impact':<10} {'% of Total':<12} {'Recommendation':<48}")
        print("-" * 90)
        
        for i, comp in enumerate(result["detailed_components"][:10]):
            # Create directional indicators
            if comp["infl_weight"] < 0:
                infl_direction = "▼" # This nutrient generally reduces inflammation
            else:
                infl_direction = "▲" # This nutrient generally increases inflammation
                
            if comp["z_score"] > 0:
                amount_direction = "▲" # Eating more than average
            else:
                amount_direction = "▼" # Eating less than average
                
            if comp["score"] < 0:
                effect_direction = "▼" # Net anti-inflammatory effect
            else:
                effect_direction = "▲" # Net pro-inflammatory effect
                
            # Format percent of total
            if comp["pct_of_total"] > 0:
                pct_formatted = f"{comp['pct_of_total']:.1f}%"
            else:
                pct_formatted = "N/A"
                
            # Generate recommendation
            if comp["counter_intuitive"]:
                if comp["infl_weight"] < 0 and comp["score"] > 0:
                    # Anti-inflammatory nutrient causing pro-inflammatory effect
                    recommendation = f"Increase intake (currently below global average)"
                else:
                    # Pro-inflammatory nutrient causing anti-inflammatory effect
                    recommendation = f"Continue limiting intake (below global average)"
            else:
                if comp["infl_weight"] < 0 and comp["score"] < 0:
                    # Anti-inflammatory nutrient with anti-inflammatory effect
                    recommendation = f"Continue current intake (above global average)"
                else:
                    # Pro-inflammatory nutrient with pro-inflammatory effect
                    recommendation = f"Consider reducing intake (above global average)"
            
            # Format actual value and global mean for display
            actual_val = f"{comp['actual_value']:.1f}" if comp['actual_value'] is not None else "N/A"
            global_val = f"{comp['global_mean']:.1f}"
            
            # Print formatted row
            impact = f"{effect_direction} {abs(comp['score']):.3f}"
            print(f"{comp['friendly_name']:<20} {impact:<10} {pct_formatted:<12} {recommendation}")
            
        print("\nLegend:")
        print("▲ = Increases/Above   ▼ = Decreases/Below")
        print("\nDetailed Component Analysis:")
        print("-" * 90)
        print(f"{'Nutrient':<18} {'Your Value':<12} {'Global Avg':<12} {'Weight':<8} {'Effect':<8} {'% of Total':<10}")
        print("-" * 90)
        
        for i, comp in enumerate(result["detailed_components"][:15]):
            # Format values
            actual_val = f"{comp['actual_value']:.1f}" if comp['actual_value'] is not None else "N/A"
            global_val = f"{comp['global_mean']:.1f}"
            weight = f"{comp['infl_weight']:.3f}"
            effect = f"{comp['score']:.3f}"
            pct = f"{comp['pct_of_total']:.1f}%" if comp['pct_of_total'] > 0 else "N/A"
            
            print(f"{comp['friendly_name']:<18} {actual_val:<12} {global_val:<12} {weight:<8} {effect:<8} {pct:<10}")
    
    return True

if __name__ == "__main__":
    print("Testing DII Score Calculation")
    print("============================")
    success = test_dii_calculation()
    if success:
        print("\nTest completed successfully!")
    else:
        print("\nTest failed!")
        sys.exit(1)