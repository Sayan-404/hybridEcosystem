# plot_stats.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load the data
filename = "bacteria_stats.csv"
if not os.path.exists(filename):
    print(f"[ERROR] File '{filename}' not found.")
    exit()

df = pd.read_csv(filename)

# Calculate derived metrics
df["Net Growth"] = df["Total Births"] - df["Total Deaths"]
df["Food-to-Bacteria Ratio"] = df["Food Population"] / (df["Bacteria Population"] + 1)

# Setup plotting style
sns.set(style="whitegrid")
plt.figure(figsize=(12, 5))  # Adjusted to better fit 2 subplots side by side

# 1. Bacteria and Food Population over Time
plt.subplot(1, 2, 1)
plt.plot(df["Step"], df["Bacteria Population"], label="Bacteria", color='blue')
plt.plot(df["Step"], df["Food Population"], label="Food", color='green')
plt.title("Population over Time")
plt.xlabel("Step")
plt.ylabel("Count")
plt.legend()

# 2. Food-to-Bacteria Ratio
plt.subplot(1, 2, 2)
plt.plot(df["Step"], df["Food-to-Bacteria Ratio"], color='brown')
plt.title("Food-to-Bacteria Ratio")
plt.xlabel("Step")
plt.ylabel("Ratio")

plt.tight_layout()
plt.savefig("bacteria_analysis.png")
plt.show()
