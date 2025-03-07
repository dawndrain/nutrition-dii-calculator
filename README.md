# Nutrition CSV Analyzer with DII Score

A Streamlit web application that allows users to upload nutrition data CSV files and get Dietary Inflammatory Index (DII) score analysis.

## Running the App

```bash
streamlit run app.py
```

## Features

- Upload nutrition CSV files
- View data preview and basic statistics
- Calculate Dietary Inflammatory Index (DII) score using the same formula as the DII.R library
- Color-coded score interpretation (anti-inflammatory, neutral, pro-inflammatory)
- Show top contributing nutrients to the score
- Multi-day support: automatically detects multiple days from the "Date" column and:
  - Calculates scores for each individual day
  - Calculates an average DII score across all days
  - Shows most impactful nutrients for both individual days and average

## DII Calculation Method

The app calculates DII scores following the same methodology as in the R implementation:
1. Takes nutrition values and compares them to global means
2. Calculates Z-scores for each nutrient
3. Converts Z-scores to percentiles
4. Weights percentiles by inflammatory effect scores
5. Sums all weighted scores to get the final DII

The higher the score, the more pro-inflammatory the diet. Negative scores indicate an anti-inflammatory diet.

## CSV Format

The app expects a CSV with these columns (if available):
- Date (for multiple day tracking)
- Energy (kcal)
- Alcohol (g)
- Caffeine (mg)
- B1 (Thiamine) (mg)
- B2 (Riboflavin) (mg)
- ... and other nutritional values