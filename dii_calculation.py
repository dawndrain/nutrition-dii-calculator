import pandas as pd
from scipy.stats import norm

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


def test_calculate_dii_score():
    df = pd.read_csv('dailysummary.csv')
    assert calculate_dii_score(df.iloc[0])[0] == 0.6766225514700941
    