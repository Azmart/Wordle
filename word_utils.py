import csv
from pathlib import Path
from typing import List, Set

# Default word list in case CSV is not available
DEFAULT_WORDS = [
    "stare", "crane", "slate", "trace", "adieu",
    "audio", "house", "mouse", "about", "above"
]

def load_words() -> List[str]:
    """Load words from CSV file or return default list if file not found."""
    try:
        csv_path = Path("wordle_merged.csv")
        if not csv_path.exists():
            print("Warning: wordle_merged.csv not found, using default word list")
            return DEFAULT_WORDS
        
        words = []
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            words = [row[0].lower() for row in reader if row and len(row[0]) == 5]
        
        if not words:
            print("Warning: No valid words found in CSV, using default word list")
            return DEFAULT_WORDS
            
        return words
    except Exception as e:
        print(f"Error loading words: {e}")
        return DEFAULT_WORDS

def is_valid_word(word: str, valid_words: Set[str]) -> bool:
    """Check if a word is valid (5 letters and in the word list)."""
    return len(word) == 5 and word.lower() in valid_words

# Load words once at module level
WORDS = load_words()
VALID_WORDS = set(WORDS) 