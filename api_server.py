import random
import logging
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from word_utils import WORDS, is_valid_word, VALID_WORDS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Wordle API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store solutions for each seed
SEED_SOLUTIONS = {}

class FeedbackItem(BaseModel):
    slot: int
    guess: str
    result: str

def get_feedback(guess: str, solution: str) -> List[FeedbackItem]:
    """Generate Wordle-style feedback for a guess against a solution."""
    feedback = []
    used = [False] * 5  # Track which solution letters have been matched
    
    # First pass: check for correct letters
    for i, (g, s) in enumerate(zip(guess, solution)):
        if g == s:
            feedback.append(FeedbackItem(slot=i, guess=g, result="correct"))
            used[i] = True
        else:
            feedback.append(FeedbackItem(slot=i, guess=g, result="absent"))
    
    # Second pass: check for present letters
    for i, (g, s) in enumerate(zip(guess, solution)):
        if g != s:  # Skip if already correct
            for j, (s2, u) in enumerate(zip(solution, used)):
                if g == s2 and not u:
                    feedback[i] = FeedbackItem(slot=i, guess=g, result="present")
                    used[j] = True
                    break
    
    return feedback

@app.get("/random")
async def get_random_feedback(
    guess: str,
    size: int = 5,
    seed: Optional[int] = None
) -> List[FeedbackItem]:
    """Get feedback for a guess against a seeded random word."""
    if len(guess) != size:
        raise HTTPException(status_code=400, detail=f"Guess must be {size} letters")
    
    if not is_valid_word(guess, VALID_WORDS):
        raise HTTPException(status_code=400, detail="Invalid guess word")
    
    # Use provided seed or generate random one
    if seed is None:
        seed = random.randint(0, 1000000)
    
    # Get or generate solution for this seed
    if seed not in SEED_SOLUTIONS:
        SEED_SOLUTIONS[seed] = random.choice(WORDS)
    
    solution = SEED_SOLUTIONS[seed]
    feedback = get_feedback(guess.lower(), solution)
    
    # Log the interaction
    logger.info(f"Seed: {seed}, Solution: {solution}, Guess: {guess}, Feedback: {feedback}")
    
    return feedback

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"} 