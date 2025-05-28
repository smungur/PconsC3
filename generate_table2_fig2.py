import pandas as pd
import matplotlib.pyplot as plt
import os

OUTPUT_DIR = "figures_and_tables"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1) Load the two CSVs
res = pd.read_csv("results_with_class.csv")
bench = pd.read_csv("benchmark_with_class.csv")

# 2) Table 2: average PPV₂ by structural class
table2 = (
    res
    .groupby("secondary_structure_class")["PPV"]
    .agg(Avg_PPV=("mean"), Count=("count"))
    .reset_index()
)
print("Table 2 – Average PPV₂ by structural class")
print(table2.to_string(index=False))
table2.to_csv(os.path.join(OUTPUT_DIR, "table2_average_ppv2_by_class.csv"), index=False)



# 3) Figure 2a: PPV₂ vs Beff on your 210‐protein benchmark (results)
plt.figure(figsize=(6,4))
plt.scatter(res["Beff"], res["PPV"], s=20, alpha=0.4)
plt.xscale("log")
plt.xlabel("Beff (effective sequences)")
plt.ylabel("PPV₂")
plt.title("Figure 2a: Benchmark PPV₂ vs Beff")
# rolling mean (window=30)
r = res.sort_values("Beff")
r["PPV_smooth"] = r["PPV"].rolling(30, center=True).mean()
plt.plot(r["Beff"], r["PPV_smooth"], color="black", lw=2)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "Figure2a_benchmark_ppv2_vs_beff.png"), dpi=300)

plt.show()


# 4) Figure 2b: PPV₂ vs Beff on Pfam (benchmarkset)
plt.figure(figsize=(6,4))
plt.scatter(bench["Beff"], bench["PPV"], s=5, c="gray", alpha=0.2)
plt.xscale("log")
plt.xlabel("Beff (effective sequences)")
plt.ylabel("PPV₂")
plt.title("Figure 2b: Pfam PPV₂ vs Beff")
# rolling mean (window=500)
b = bench.sort_values("Beff")
b["PPV_smooth"] = b["PPV"].rolling(500, center=True).mean()
plt.plot(b["Beff"], b["PPV_smooth"], color="black", lw=2)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "Figure2b_Pfam_ppv2_vs_beff.png"), dpi=300)
plt.show()
