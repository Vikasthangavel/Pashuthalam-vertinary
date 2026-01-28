# Antibiotic Dosage Conversion: mg to ml

## Overview
This document explains how the medical shop application converts antibiotic dosages from milligrams (mg) to milliliters (ml) for practical administration to poultry.

## Dataset Information
- **Source**: `poultry_dataset_optimal.csv`
- **Dosage Column**: Contains dosage values in **mg** (milligrams)
- **Format**: Numerical values representing the weight of active ingredient

## Conversion Process

### 1. Standard Concentrations Used
The system uses veterinary-standard antibiotic concentrations for conversion:

```python
# Standard antibiotic concentrations (mg/ml)
ANTIBIOTIC_CONCENTRATIONS = {
    'Doxycycline': 50,      # 50 mg/ml
    'Amoxicillin': 150,     # 150 mg/ml  
    'Enrofloxacin': 100,    # 100 mg/ml
    'Tylosin': 200,         # 200 mg/ml
    'Florfenicol': 300,     # 300 mg/ml
    'Colistin': 100         # 100 mg/ml
}
```

### 2. Conversion Formula
```
Volume (ml) = Dosage (mg) ÷ Concentration (mg/ml)
```

### 3. Example Calculations

#### Example 1: Doxycycline
- **Dataset dosage**: 53.8 mg
- **Standard concentration**: 50 mg/ml
- **Calculation**: 53.8 ÷ 50 = 1.076 ml
- **Rounded result**: 1.08 ml

#### Example 2: Amoxicillin  
- **Dataset dosage**: 75.0 mg
- **Standard concentration**: 150 mg/ml
- **Calculation**: 75.0 ÷ 150 = 0.5 ml
- **Result**: 0.5 ml

#### Example 3: Enrofloxacin
- **Dataset dosage**: 120.0 mg
- **Standard concentration**: 100 mg/ml
- **Calculation**: 120.0 ÷ 100 = 1.2 ml
- **Result**: 1.2 ml

## Implementation in Code

### Function: `get_veterinary_dosage_standards()`
```python
def get_veterinary_dosage_standards():
    """Convert mg dosages to ml using standard veterinary concentrations"""
    if poultry_df is None:
        return {}
    
    # Standard concentrations (mg/ml)
    concentrations = {
        'Doxycycline': 50,
        'Amoxicillin': 150, 
        'Enrofloxacin': 100,
        'Tylosin': 200,
        'Florfenicol': 300,
        'Colistin': 100
    }
    
    dosage_standards = {}
    
    for _, row in poultry_df.iterrows():
        antibiotic = row['Suggested Antibiotic']
        dosage_mg = float(row['Dosage'])
        
        # Convert mg to ml using standard concentration
        if antibiotic in concentrations:
            concentration = concentrations[antibiotic]
            dosage_ml = round(dosage_mg / concentration, 2)
            
            dosage_standards[antibiotic] = {
                'dosage_mg': dosage_mg,
                'dosage_ml': dosage_ml,
                'concentration': f"{concentration} mg/ml"
            }
    
    return dosage_standards
```

## Practical Benefits

### 1. **Accurate Administration**
- Farmers get precise ml measurements for injection/oral administration
- Reduces medication errors and overdosing risks

### 2. **Standardized Concentrations**
- Uses veterinary-approved concentration standards
- Ensures consistency across different suppliers

### 3. **Easy Measurement**
- ml is easier to measure with syringes and measuring devices
- More practical for field administration

## Dosage Conversion Table

| Antibiotic | Concentration | Example Dosage (mg) | Converted (ml) |
|------------|---------------|---------------------|----------------|
| Doxycycline | 50 mg/ml | 53.8 mg | 1.08 ml |
| Amoxicillin | 150 mg/ml | 75.0 mg | 0.50 ml |
| Enrofloxacin | 100 mg/ml | 120.0 mg | 1.20 ml |
| Tylosin | 200 mg/ml | 100.0 mg | 0.50 ml |
| Florfenicol | 300 mg/ml | 150.0 mg | 0.50 ml |
| Colistin | 100 mg/ml | 80.0 mg | 0.80 ml |

## Important Notes

### 1. **Concentration Standards**
- Concentrations are based on commonly available veterinary formulations
- May vary by manufacturer - always check product labels

### 2. **Rounding**
- Results are rounded to 2 decimal places for practical measurement
- Ensures accuracy while maintaining usability

### 3. **Administration Routes**
- **Intramuscular (IM)**: Most common for antibiotics
- **Oral**: For water-soluble formulations
- **Subcutaneous (SC)**: For specific antibiotics

### 4. **Safety Guidelines**
- Always follow withdrawal periods before consuming poultry products
- Consult veterinarian for dosage adjustments
- Monitor birds for adverse reactions

## Future Enhancements

1. **Dynamic Concentrations**: Allow users to input custom concentrations
2. **Multiple Formulations**: Support different concentration options per antibiotic
3. **Route-Specific Dosing**: Adjust dosages based on administration route
4. **Weight-Based Calculations**: Factor in individual bird weights for more precise dosing

---
*This conversion system ensures that farmers receive practical, measurable dosage instructions while maintaining the scientific accuracy of the original dataset recommendations.*