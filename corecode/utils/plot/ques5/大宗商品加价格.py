import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import os

# Set font to support English (optional, for consistency)
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# Read data
data_path = r'C:\Users\15963\Desktop\APMCM-training\data\raw\ques5\大宗商品与关键材料\commodity_prices_2016_2025.csv'
df = pd.read_csv(data_path)

# Preprocess data: set 'year' as index for heatmap
heatmap_data = df.set_index('year')

# Log-transform data to handle large value differences (improves color distribution)
heatmap_data_log = np.log10(heatmap_data)

# Create figure
plt.figure(figsize=(14, 8))

# Plot heatmap
ax = sns.heatmap(heatmap_data_log,
                 annot=heatmap_data,  # Show original values
                 fmt='g',  # Format as general numbers
                 cmap='YlOrRd',
                 linewidths=0.5,
                 cbar_kws={'label': 'Price (Log Scale)', 'shrink': 0.8})

# Set titles and labels
plt.title('Commodity Prices Heatmap (2016-2025)', fontsize=16, pad=20)
plt.xlabel('Commodity Type', fontsize=12, labelpad=10)
plt.ylabel('Year', fontsize=12, labelpad=10)

# Rotate x-axis labels to avoid overlap
plt.xticks(rotation=45, ha='right')

# Adjust layout
plt.tight_layout()

# Create save directory if it doesn't exist
save_dir = r'C:\Users\15963\Desktop\APMCM-training\results\figures\ques5\大宗商品与关键材料'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Save plot
save_path = os.path.join(save_dir, 'commodity_prices_heatmap.png')
plt.savefig(save_path, dpi=300, bbox_inches='tight')
plt.show()

print(f"Heatmap saved to: {save_path}")