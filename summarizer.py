import pandas as pd
import os
import numpy as np
from openai import OpenAI

# Initialize OpenAI client (set OPENAI_API_KEY environment variable)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load the CSV file
csv_file = "Rating Expressive Robot Gestures with Human Feedback_Iteration4.csv"
df_full = pd.read_csv(csv_file)

# Select only columns ending with "b"
columns_b = [col for col in df_full.columns if col.endswith('b')]

# Sort columns numerically by extracting the numeric part
columns_b_sorted = sorted(columns_b, key=lambda x: int(x[1:-1]))  # Extract number between Q and b
df_b = df_full[columns_b_sorted]

# Remove first 2 rows (headers)
df_b = df_b.iloc[2:].reset_index(drop=True)

# Convert to 2D array, replacing NaN with empty strings
array_2d = df_b.fillna('').values.T
print(array_2d[1])

print(f"Total feedback entries: {array_2d.shape[0]}")
print(f"Total columns: {array_2d.shape[1]}\n")
print("Sample feedback entries (first 5 rows):")

# Function to summarize text messages
def summarize_feedback(text_messages):
    """
    Summarize feedback text using OpenAI API
    
    Args:
        text_messages: List of text strings or a single string to summarize
    
    Returns:
        Summary string
    """
    if isinstance(text_messages, list):
        text_messages = " ".join([str(msg) for msg in text_messages if msg])
    
    # Remove empty strings and filter out short noise
    text_messages = " ".join([msg for msg in text_messages.split() if msg])
    
    if not text_messages or len(text_messages.strip()) == 0:
        return "No feedback provided"
    
    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=[
            {
                "role": "system", 
                "content": "You are a helpful assistant that summarizes user feedback concisely and clearly."
            },
            {
                "role": "user",
                "content": f"Please summarize the following feedback in 1-2 sentences like a feedback comment itself:\n\n{text_messages}"
            }
        ],
        temperature=0.7,
    )
    
    return response.choices[0].message.content

# Summarize each row of feedback
print("Summarizing feedback for each entry...\n")
summaries = []

for idx, row in enumerate(array_2d):
    # Combine all non-empty text from the row
    feedback = [text for text in row if text and len(str(text).strip()) > 0]
    
    if feedback:
        print(f"Entry {idx + 1}: Summarizing {len(feedback)} feedback items...")
        summary = summarize_feedback(feedback)
        summaries.append(summary)
        print(f"Summary: {summary}\n")
    else:
        print(f"Entry {idx + 1}: No feedback\n")
        summaries.append("No feedback provided")

# Save summaries to a new dataframe
df_summaries = pd.DataFrame({
    'Entry': range(1, len(summaries) + 1),
    'Summary': summaries
})

print("\n" + "="*80)
print("SUMMARIES")
print("="*80)
print(df_summaries.to_string(index=False))

# Optionally save to CSV
df_summaries.to_csv('feedback_summaries.csv', index=False)
print("\n✓ Summaries saved to 'feedback_summaries.csv'")
