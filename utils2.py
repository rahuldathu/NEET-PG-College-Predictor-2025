import pandas as pd
import re
import csv

# Load CSV
df = pd.read_csv("final_seat_allocation.csv")

# Function to clean and normalize text
def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text)
    text = text.replace('\n', ' ')                     # Remove newlines
    text = re.sub(r',\s*,', ',', text)                 # Replace double commas
    text = re.sub(r'\s+', ' ', text)                   # Collapse multiple spaces
    text = re.sub(r'\s+,', ',', text)                  # Remove space before commas
    text = re.sub(r',\s+', ', ', text)                 # Ensure space after commas
    return text.strip()

# Clean original columns (removes newlines, extra spaces)
df['allotted_institute'] = df['allotted_institute'].apply(clean_text)
df['course'] = df['course'].apply(clean_text)

# Also create normalized (canonical) versions for comparison if needed
df['allotted_institute_normalized'] = df['allotted_institute'].str.title()
df['course_normalized'] = df['course'].str.title()

# Save with quoting to preserve all fields
df.to_csv("fully_normalized.csv", index=False, quoting=csv.QUOTE_ALL)

print("✅ Done! All rows are single-line and quoted properly in 'fully_normalized.csv'.")
