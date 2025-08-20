# generate_inference_table.py
import pandas as pd

RAW_CSV = "fully_normalized.csv"   # raw counselling data file
OUTPUT_CSV = "inference_table.csv"      # precomputed inference table

def generate_inference_table():
    df = pd.read_csv(RAW_CSV)

    # Precompute both min & max ranks per (college, course, quota, category)
    inference = df.groupby(
        ["allotted_institute", "course", "allotted_quota", "candidate_category"]
    )["rank"].agg(min_rank="min", cutoff_rank="max").reset_index()

    # Rename columns for clarity
    inference.rename(columns={
        "allotted_institute": "college",
        "allotted_quota": "quota",
        "candidate_category": "category"
    }, inplace=True)

    inference.to_csv(OUTPUT_CSV, index=False)
    print(f"Inference table saved to {OUTPUT_CSV} with {len(inference)} rows.")

if __name__ == "__main__":
    generate_inference_table()
