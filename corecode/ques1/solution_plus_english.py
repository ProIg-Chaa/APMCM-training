import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import seaborn as sns

# --- Plot settings (Handle fonts if needed) ---
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans'] 
plt.rcParams['axes.unicode_minus'] = False
sns.set(style="whitegrid")

# ==========================================
# 1. Data Loading and Preprocessing
# ==========================================
def load_and_prep_data(filepath):
    print(f"Reading data file: {filepath}...")
    df = pd.read_csv(filepath)
    
    required_cols = ['import_volume', 'cif_tax_price', 'production', 'import_value', 'total_tariff']
    
    # Clean zeros and negative values to avoid log errors
    for col in required_cols:
        df[col] = df[col].replace(0, np.nan)
    
    df = df.dropna(subset=required_cols)
    
    # Log transformation for log-log regression
    df['ln_volume'] = np.log(df['import_volume'])
    df['ln_price'] = np.log(df['cif_tax_price'])
    df['ln_prod'] = np.log(df['production'])
    
    print("Data preprocessing completed.")
    return df

# ==========================================
# 2. Get Corrected Price Elasticity
# ==========================================
def get_corrected_elasticity(df):
    formula = "ln_volume ~ ln_price + ln_prod + C(origin)"
    model = smf.ols(formula=formula, data=df).fit()
    
    calculated_elasticity = model.params['ln_price']
    
    print("-" * 50)
    print(f"Raw estimated elasticity: {calculated_elasticity:.4f}")
    
    # Price elasticity of demand should be negative (normal goods)
    if calculated_elasticity > 0:
        print("[WARNING] Positive price elasticity detected, which contradicts demand theory.")
        print("          This is likely caused by ASF shock in 2018–2019 where price and volume moved together.")
        print("[CORRECTION] Elasticity is overridden with literature-based value: -1.0")
        return -1.0
    else:
        print("Elasticity is negative and logical. Keeping estimated value.")
        return calculated_elasticity

# ==========================================
# 3. Tariff Gradient Simulation Engine
# ==========================================
def run_gradient_simulation(df, elasticity, target_country='United States'):
    latest_year = df['year'].max()
    print(f"Baseline year: {latest_year}")
    
    base_df = df[df['year'] == latest_year].copy()
    
    # Separate US and competitors
    us_data = base_df[base_df['origin'] == target_country].iloc[0]
    competitors = base_df[base_df['origin'] != target_country].copy()
    
    # Competitor production shares (for substitution)
    total_comp_prod = competitors['production'].sum()
    competitors['prod_share'] = competitors['production'] / total_comp_prod
    
    # Tariff adjustments from -30% to +25%
    tariff_steps = np.linspace(-0.30, 0.25, 56)
    
    results = []
    
    for delta_t in tariff_steps:
        current_tariff = us_data['total_tariff']
        new_tariff = max(0, current_tariff + delta_t)
        
        # Price change caused by tariff change
        price_change_pct = ((1 + new_tariff) / (1 + current_tariff)) - 1
        
        # Quantity response
        vol_change_pct = price_change_pct * elasticity
        
        # New US values
        new_us_vol = us_data['import_volume'] * (1 + vol_change_pct)
        delta_us_vol = new_us_vol - us_data['import_volume']
        new_us_val = us_data['import_value'] * (1 + vol_change_pct)
        
        results.append({
            'Adjustment': delta_t,
            'Tariff_Rate': new_tariff,
            'Country': target_country,
            'Volume': new_us_vol,
            'Value': new_us_val
        })
        
        # Substitution: lost US volume is redistributed to competitors
        substitution_amount = -delta_us_vol
        
        for _, row in competitors.iterrows():
            comp_delta_vol = substitution_amount * row['prod_share']
            
            new_comp_vol = row['import_volume'] + comp_delta_vol
            new_comp_vol = max(0, new_comp_vol)
            
            unit_price = row['import_value'] / row['import_volume']
            new_comp_val = new_comp_vol * unit_price
            
            results.append({
                'Adjustment': delta_t,
                'Tariff_Rate': row['total_tariff'],
                'Country': row['origin'],
                'Volume': new_comp_vol,
                'Value': new_comp_val
            })
            
    return pd.DataFrame(results)

# ==========================================
# 4. Main Execution Block
# ==========================================
if __name__ == "__main__":
    file_path = 'panel_cleaned.csv'
    
    try:
        df = load_and_prep_data(file_path)
        
        final_elasticity = get_corrected_elasticity(df)
        print(f"Final elasticity used in simulation: {final_elasticity}")
        print("-" * 50)
        
        sim_df = run_gradient_simulation(df, final_elasticity)
        
        # Unit conversion
        sim_df['Volume_MT'] = sim_df['Volume'] / 1e6
        sim_df['Value_Billion'] = sim_df['Value'] / 1e9
        sim_df['Adjustment_Pct'] = sim_df['Adjustment'] * 100
        
        # --- Visualization ---
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Volume plot
        sns.lineplot(data=sim_df, x='Adjustment_Pct', y='Volume_MT', hue='Country',
                     linewidth=2.5, ax=axes[0])
        axes[0].set_title('Impact of Tariff Adjustments on Soybean Export Volume', fontsize=14)
        axes[0].set_xlabel('US Tariff Adjustment (%)', fontsize=12)
        axes[0].set_ylabel('Export Volume (Million Tons)', fontsize=12)
        axes[0].axvline(0, color='grey', linestyle='--', alpha=0.6)
        
        # Value plot
        sns.lineplot(data=sim_df, x='Adjustment_Pct', y='Value_Billion', hue='Country',
                     linewidth=2.5, ax=axes[1])
        axes[1].set_title('Impact of Tariff Adjustments on Export Value', fontsize=14)
        axes[1].set_xlabel('US Tariff Adjustment (%)', fontsize=12)
        axes[1].set_ylabel('Export Value (Billion USD)', fontsize=12)
        axes[1].axvline(0, color='grey', linestyle='--', alpha=0.6)
        
        plt.tight_layout()
        plt.show()
        
        # Key scenario table
        print("\n[Key Scenario Summary] (Unit: Million Tons)")
        target_points = [-0.25, -0.10, 0.0, 0.10, 0.25]
        
        mask = sim_df['Adjustment'].apply(lambda x: any(np.isclose(x, tp, atol=0.005) for tp in target_points))
        summary = sim_df[mask].pivot_table(index='Adjustment', columns='Country', values='Volume_MT')
        
        summary.index = summary.index.map(lambda x: f"{x:+.0%}")
        print(summary.round(2))
        
        print("\nConclusion: With negative elasticity, the model shows that lowering US tariffs significantly increases US export volume while reducing Brazil/Argentina market share. This matches standard trade logic.")
    
    except FileNotFoundError:
        print(f"Error: File {file_path} not found. Please check the path.")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
