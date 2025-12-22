import json
import os

notebook_path = '/Users/junyoung/Document_SSD/Modeling/housing.ipynb'

with open(notebook_path, 'r') as f:
    nb = json.load(f)

# 1. Update Data Generation Cell
# Find the cell that creates the DataFrame (Execution count might change, look for source)
found_data_cell = False
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        if "house_price = np.linspace(3000,15000,100)" in source:
            # Replace source
            cell['source'] = [
                "import itertools\n",
                "\n",
                "house_prices = np.linspace(3000, 15000, 50)\n",
                "annual_rises = np.linspace(-0.02, 0.05, 50)\n",
                "annual_interest_rates = np.linspace(0.01, 0.05, 5)\n",
                "years = 20 # 20 years of loan\n",
                "\n",
                "# Create all combinations (Cartesian Product)\n",
                "combinations = list(itertools.product(house_prices, annual_rises, annual_interest_rates))\n",
                "df = pd.DataFrame(combinations, columns=['house_price', 'annual_rise', 'annual_interest_rate'])\n",
                "\n",
                "# Calculate derived columns\n",
                "df['monthly_payment'] = df['house_price'] / years / 12\n",
                "df['surface_profit'] = 0.04\n",
                "df['monthly_rent'] = df['house_price'] * df['surface_profit'] / 12\n",
                "\n",
                "# We need to make sure calculate_profit_diff is applied AFTER this.\n",
                "# The next cell does that, so we just setup the df here.\n"
            ]
            found_data_cell = True
            break

if not found_data_cell:
    print("Could not find data generation cell to replace.")
    # Fallback: Searching by ID if we knew it, but index is safer if structure is consistent.
    # We will assume it's one of the cells. If not found, we might be searching wrong string.

# 2. Add Crossover Analysis Cell at the end
crossover_source = [
    "# Crossover Analysis\n",
    "def get_crossover_val(group, target_col='buy_vs_rent_profit', x_col='annual_rise'):\n",
    "    # Finds the annual_rise where profit crosses 0\n",
    "    group = group.sort_values(x_col)\n",
    "    # Linear interpolation for 0 crossing\n",
    "    for i in range(len(group) - 1):\n",
    "        y1 = group.iloc[i][target_col]\n",
    "        y2 = group.iloc[i+1][target_col]\n",
    "        if y1 * y2 <= 0 and y1 != y2:\n",
    "            x1 = group.iloc[i][x_col]\n",
    "            x2 = group.iloc[i+1][x_col]\n",
    "            # x = x1 - y1 * (x2 - x1) / (y2 - y1)\n",
    "            return x1 - y1 * (x2 - x1) / (y2 - y1)\n",
    "    return np.nan\n",
    "\n",
    "# Calculate crossover for each price and rate\n",
    "crossover_results = []\n",
    "for (price, rate), group in df.groupby(['house_price', 'annual_interest_rate']):\n",
    "    breakeven = get_crossover_val(group)\n",
    "    crossover_results.append({'house_price': price, 'annual_interest_rate': rate, 'breakeven_annual_rise': breakeven})\n",
    "\n",
    "df_crossover = pd.DataFrame(crossover_results)\n",
    "\n",
    "# Plot Breakeven Surface\n",
    "fig = plt.figure(figsize=(12, 8))\n",
    "ax = fig.add_subplot(111, projection='3d')\n",
    "surf = ax.plot_trisurf(df_crossover['house_price'], df_crossover['annual_interest_rate'], df_crossover['breakeven_annual_rise'], cmap='viridis', edgecolor='none')\n",
    "ax.set_xlabel('House Price')\n",
    "ax.set_ylabel('Annual Interest Rate')\n",
    "ax.set_zlabel('Breakeven Annual Rise')\n",
    "ax.set_title('Breakeven Annual Rise required for Buying > Renting')\n",
    "fig.colorbar(surf, shrink=0.5, aspect=5)\n",
    "plt.show()\n",
    "\n",
    "# Heatmap for fixed interest rate of 0.03\n",
    "target_rate = 0.03\n",
    "subset = df[np.isclose(df['annual_interest_rate'], target_rate)]\n",
    "if not subset.empty:\n",
    "    pivot_table = subset.pivot(index='annual_rise', columns='house_price', values='buy_vs_rent_profit')\n",
    "    plt.figure(figsize=(10, 8))\n",
    "    sns.heatmap(pivot_table, cmap='RdBu', center=0)\n",
    "    plt.title(f'Profit Heatmap (Interest Rate = {target_rate})')\n",
    "    plt.gca().invert_yaxis()\n",
    "    plt.show()"
]

new_cell = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": crossover_source
}

nb['cells'].append(new_cell)

with open(notebook_path, 'w') as f:
    json.dump(nb, f, indent=4) # indent=1 is usually standard for ipynb but 4 is fine
