import pandas as pd
import csv

# Configurations
R1_COLUMNS = ['R1_Sno', 'rank', 'R1_allotted_quota', 'R1_allotted_institute', 'R1_course',
              'R1_allotted_category', 'R1_candidate_category', 'R1_remarks']
R2_COLUMNS = ['R2_Sno', 'rank', 'R1_allotted_quota', 'R1_allotted_institute', 'R1_course', 'R1_remarks',
              'R2_allotted_quota', 'R2_allotted_institute', 'R2_course',
              'R2_allotted_category', 'R2_candidate_category', 'R2_option_no', 'R2_remarks']
R3_COLUMNS = ['rank', 'R1_allotted_quota', 'R1_allotted_institute', 'R1_course', 'R1_remarks',
              'R2_allotted_quota', 'R2_allotted_institute', 'R2_course', 'R2_remarks',
              'R3_allotted_quota', 'R3_allotted_institute', 'R3_course',
              'R3_allotted_category', 'R3_candidate_category', 'R3_option_no', 'R3_remarks']

EXPECTED_COLS = {
    'R1.csv': len(R1_COLUMNS),
    'R2.csv': len(R2_COLUMNS),
    'R3.csv': len(R3_COLUMNS)
}

# Load and clean CSV
def load_csv_clean(path, expected_cols, name):
    df = pd.read_csv(path, header=None, dtype=str)
    df = df.dropna(how='all')  # remove empty rows
    df = df[df.apply(lambda row: len(row.dropna()) > 0, axis=1)]
    df = df.replace("-", pd.NA)  # standardize null values

    # Filter valid and malformed rows
    valid_rows = df[df.apply(lambda row: len(row) == expected_cols, axis=1)].reset_index(drop=True)
    malformed_rows = df[df.apply(lambda row: len(row) != expected_cols, axis=1)]

    # Always log, even if empty
    with open("malformed_rows.log", "a", encoding="utf-8") as log_file:
        if malformed_rows.empty:
            log_file.write(f"No malformed rows found in {name} ✅\n")
        else:
            log_file.write(f"\nMalformed rows in {name}:\n")
            malformed_rows.to_string(log_file, index=False)

    return valid_rows


# Load CSVs
r1_df = load_csv_clean("R1.csv", EXPECTED_COLS['R1.csv'], "R1.csv")
r2_df = load_csv_clean("R2.csv", EXPECTED_COLS['R2.csv'], "R2.csv")
r3_df = load_csv_clean("R3.csv", EXPECTED_COLS['R3.csv'], "R3.csv")

# Final output rows
final_rows = []

for i, row in r3_df.iterrows():
    rank = row[0]

    # Default values
    final_quota = final_inst = final_course = final_category = candidate_category = final_remarks = final_round = None

    if pd.notna(row[10]):  # R3_allotted_institute
        final_round = "R3"
        final_quota = row[9]
        final_inst = row[10]
        final_course = row[11]
        final_category = row[12]
        candidate_category = row[13]
        final_remarks = row[15]

    elif pd.notna(row[6]):  # R2_allotted_institute
        final_round = "R2"
        final_quota = row[5]
        final_inst = row[6]
        final_course = row[7]
        # Get corresponding data from R2.csv
        r2_match = r2_df[r2_df[1] == rank]
        if not r2_match.empty:
            final_category = r2_match.iloc[0][9]
            candidate_category = r2_match.iloc[0][10]
            final_remarks = r2_match.iloc[0][12]

    elif pd.notna(row[2]):  # R1_allotted_institute
        final_round = "R1"
        final_quota = row[1]
        final_inst = row[2]
        final_course = row[3]
        # Get corresponding data from R1.csv
        r1_match = r1_df[r1_df[1] == rank]
        if not r1_match.empty:
            final_category = r1_match.iloc[0][5]
            candidate_category = r1_match.iloc[0][6]
            final_remarks = r1_match.iloc[0][7]

    # Add only if we found a final seat
    if final_inst:
        final_rows.append([
            rank,
            final_quota,
            final_inst,
            final_course,
            final_category,
            candidate_category,
            final_round,
            final_remarks
        ])

# Create final DataFrame
final_df = pd.DataFrame(final_rows, columns=[
    'rank',
    'allotted_quota',
    'allotted_institute',
    'course',
    'allotted_category',
    'candidate_category',
    'round',
    'remarks'
])

# Save final allocation
final_df.to_csv("final_seat_allocation.csv", index=False)
print("✅ Final seat allocation CSV created: final_seat_allocation.csv")
