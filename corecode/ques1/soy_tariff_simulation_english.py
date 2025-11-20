import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import warnings
import os

# Create save directory if it doesn't exist
save_dir = r"D:\GS_LearningAndWork\MATH-model\APMCM-training\corecode\ques1\resultdata_and_png"
os.makedirs(save_dir, exist_ok=True)

# Set Chinese font (try different fonts according to the system to avoid squares)
import matplotlib
plt.rcParams['axes.unicode_minus'] = False
try:
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
except:
    pass

warnings.filterwarnings("ignore")

# ========================== 1. Data Reading and Cleaning ==========================
print(">>> Reading data...")
df = pd.read_csv("panel_cleaned.csv")

# Filter three major countries
countries = ["United States", "Brazil", "Argentina"]
df = df[df["origin"].isin(countries)].copy()

# Calculate core variable: CIF price with tax
# P_tax = CIF price * (1 + total tariff rate)
df["price_tax"] = df["cif_price"] * (1 + df["total_tariff"])

# Get base period data (2025)
base_year = df["year"].max()
df_base = df[df["year"] == base_year].set_index("origin")

print(f"Base year: {base_year}")
print("-" * 30)

# ========================== 2. Status Quo Analysis (First part of Question 1) ==========================
print(f"\n>>> {base_year} China's Soybean Trade Status Analysis:")
total_import_vol = df_base["import_volume"].sum()
total_import_val = df_base["import_value"].sum()

status_quo = df_base[["import_volume", "import_value", "price_tax", "total_tariff"]].copy()
status_quo["Market Share (Volume)"] = status_quo["import_volume"] / total_import_vol
status_quo["Market Share (Value)"] = status_quo["import_value"] / total_import_val

# Print status quo table
print(status_quo.style.format({
    "import_volume": "{:,.0f}", 
    "import_value": "{:,.0f}", 
    "price_tax": "{:.1f}", 
    "Market Share (Volume)": "{:.1%}",
    "Market Share (Value)": "{:.1%}"
}).to_string())
print("-" * 30)

# ========================== 3. Elasticity Estimation (With Safety Checks) ==========================
# Default literature values (used when regression results are unreasonable)
# Demand elasticity (negative value): 1% price increase leads to 0.6% decrease in total demand
DEFAULT_ETA = -0.6  
# Substitution elasticity (positive value): 1% change in price ratio leads to 3.5% change in share ratio
DEFAULT_SIGMA = 3.5 
# Supply elasticity (positive value): 1% price increase leads to 0.8% increase in country's production/export
DEFAULT_SUPPLY = {"United States": 0.6, "Brazil": 0.8, "Argentina": 0.5} 

print("\n>>> Estimating model parameters (Safety check mode activated)...")

# --- (1) Overall demand elasticity η ---
try:
    agg_data = df.groupby("year").apply(
        lambda x: pd.Series({
            "Q": x["import_volume"].sum(),
            "P": np.average(x["price_tax"], weights=x["import_volume"])
        })
    ).reset_index()
    # Simple log regression: ln(Q) = C + η * ln(P)
    res_eta = smf.ols("np.log(Q) ~ np.log(P)", data=agg_data).fit()
    eta_est = res_eta.params["np.log(P)"]
    
    # Safety check: Demand elasticity must be negative
    if eta_est >= -0.1: 
        print(f"  [Warning] Estimated demand elasticity ({eta_est:.3f}) is unreasonable (non-negative or too small), using default value {DEFAULT_ETA}")
        eta = DEFAULT_ETA
    else:
        print(f"  [Success] Estimated demand elasticity η = {eta_est:.3f}")
        eta = eta_est
except:
    print(f"  [Failure] Regression error, using default demand elasticity {DEFAULT_ETA}")
    eta = DEFAULT_ETA

# --- (2) Armington substitution elasticity σ ---
# Simplified regression: ln(share) = C - σ * ln(price) + fixed effects
try:
    temp = df.copy()
    temp["share"] = temp["import_volume"] / temp.groupby("year")["import_volume"].transform("sum")
    res_sigma = smf.ols("np.log(share) ~ np.log(price_tax) + C(origin)", data=temp).fit()
    sigma_est = -res_sigma.params["np.log(price_tax)"]
    
    # Safety check: Substitution elasticity is usually between 1 and 10
    if not (1.0 < sigma_est < 10.0):
        print(f"  [Warning] Estimated substitution elasticity ({sigma_est:.3f}) is outside reasonable range, using default value {DEFAULT_SIGMA}")
        sigma = DEFAULT_SIGMA
    else:
        print(f"  [Success] Estimated substitution elasticity σ = {sigma_est:.3f}")
        sigma = sigma_est
except:
    print(f"  [Failure] Regression error, using default substitution elasticity {DEFAULT_SIGMA}")
    sigma = DEFAULT_SIGMA

# --- (3) Country-specific supply elasticities ---
supply_elas = {}
for c in countries:
    try:
        sub = df[df["origin"] == c].copy()
        # Supply regression: ln(production/export) = C + ε * ln(price)
        # Using production as a proxy for supply capacity here
        res_sup = smf.ols("np.log(production) ~ np.log(price_tax)", data=sub).fit()
        sup_est = res_sup.params["np.log(price_tax)"]
        
        # Safety check: Supply elasticity should not be too small (may cause division by zero/divergence) or negative
        if sup_est < 0.3: 
            print(f"  [Adjustment] {c} supply elasticity estimate {sup_est:.3f} is too low/negative, adjusted to {DEFAULT_SUPPLY[c]}")
            supply_elas[c] = DEFAULT_SUPPLY[c]
        else:
            print(f"  [Success] {c} supply elasticity = {sup_est:.3f}")
            supply_elas[c] = sup_est
    except:
        supply_elas[c] = DEFAULT_SUPPLY[c]

# ========================== 4. Simulation Model (Armington Solver) ==========================
def solve_equilibrium(tariff_shock_pct):
    """
    Simulate the impact of US tariff changes on equilibrium
    tariff_shock_pct: Additional percentage increase in US tariffs (e.g., 0.10 represents +10%)
    """
    # 1. Initialize base period data
    P0 = df_base["price_tax"].to_dict()  # Base period price with tax
    Q0 = df_base["import_volume"].to_dict() # Base period volume
    
    # US price is affected by additional tariff shock
    P_current = P0.copy()
    P_current["United States"] *= (1 + tariff_shock_pct)
    
    # 2. Iterate to find equilibrium
    max_iter = 500
    tol = 1e-5
    damping = 0.5
    
    Q_total_0 = sum(Q0.values())
    
    # Calculate base period price index
    def get_price_index(prices_dict):
        return sum(p ** (1 - sigma) for p in prices_dict.values()) ** (1 / (1 - sigma))
    
    for i in range(max_iter):
        # A. Demand side
        # Step 1: Calculate component weights
        weights = {c: P_current[c] ** (-sigma) for c in countries}
        sum_weights = sum(weights.values())
        
        # === Fixed this line ===
        shares = {country: weight / sum_weights for country, weight in weights.items()} 
        
        # Step 2: Calculate new average price
        P_avg_new = sum(P_current[c] * shares[c] for c in countries)
        P_avg_old = np.average(list(P0.values()), weights=list(Q0.values()))
        
        # Step 3: Calculate total demand change
        Q_total_new = Q_total_0 * (P_avg_new / P_avg_old) ** eta
        
        # Step 4: Get tentative import volumes for each country
        Q_new_demand = {c: Q_total_new * shares[c] for c in countries}
        
        # B. Supply side
        P_next = {}
        diff = 0
        for c in countries:
            supply_effect = (Q_new_demand[c] / Q0[c]) ** (1 / supply_elas[c])
            price_from_supply = P0[c] * supply_effect
            
            if c == "United States":
                tariff_multiplier = (1 + tariff_shock_pct)
                price_from_supply = max(price_from_supply, P0[c] * tariff_multiplier * 0.95)
            
            P_next[c] = (1 - damping) * P_current[c] + damping * price_from_supply
            diff += abs(P_next[c] - P_current[c]) / P_current[c]
        
        P_current = P_next
        if diff < tol:
            break
            
    V_new = {c: Q_new_demand[c] * P_current[c] for c in countries}
    
    return {
        "Scenario": f"US Tariff +{tariff_shock_pct*100:.0f}%",
        "Q_US": Q_new_demand["United States"],
        "Q_BR": Q_new_demand["Brazil"],
        "Q_AR": Q_new_demand["Argentina"],
        "V_US": V_new["United States"],
        "V_BR": V_new["Brazil"],
        "V_AR": V_new["Argentina"]
    }
# ========================== 5. Run Scenario Simulations ==========================
print("\n>>> Running scenario simulations...")

results = []
# Scenario 1: Status quo (baseline)
res0 = solve_equilibrium(0.0)
res0["Scenario"] = "Baseline (2025)"
results.append(res0)

# Scenario 2: US tariff +10%
results.append(solve_equilibrium(0.10))

# Scenario 3: US tariff +25%
results.append(solve_equilibrium(0.25))

res_df = pd.DataFrame(results)

# Calculate change rates
cols_Q = ["Q_US", "Q_BR", "Q_AR"]
cols_V = ["V_US", "V_BR", "V_AR"]

# Convert to more readable format (10,000 tons / 100 million USD)
display_df = res_df.copy()
for c in cols_Q:
    display_df[c] = display_df[c] / 10000  # 10,000 tons
for c in cols_V:
    display_df[c] = display_df[c] / 1e8    # 100 million USD

print("\n========== Simulation Results (Volume: 10,000 tons, Value: 100 million USD) ==========")
print(display_df.round(2).to_string(index=False))

# Save results
csv_path = os.path.join(save_dir, "simulation_result_final.csv")
display_df.round(2).to_csv(csv_path, index=False, encoding="utf-8-sig")
print(f"\nResults saved to {csv_path}")

# ========================== 6. Plotting ==========================
plt.figure(figsize=(10, 6))
x = np.arange(len(res_df))
width = 0.25

# Plot import volume changes
plt.bar(x - width, res_df["Q_US"]/10000, width, label='United States', color='#1f77b4')
plt.bar(x, res_df["Q_BR"]/10000, width, label='Brazil', color='#2ca02c')
plt.bar(x + width, res_df["Q_AR"]/10000, width, label='Argentina', color='#ff7f0e')

plt.ylabel('China Import Volume (10,000 tons)', fontsize=12)
plt.title('Simulated Changes in Soybean Exports from Three Countries Under Different Tariff Scenarios', fontsize=14)
plt.xticks(x, res_df["Scenario"], fontsize=11)
plt.legend()
plt.grid(axis='y', alpha=0.3)

plt.tight_layout()
png_path = os.path.join(save_dir, "tariff_impact_chart.png")
plt.savefig(png_path, dpi=300)
print(f"Chart saved to {png_path}")