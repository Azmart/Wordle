import streamlit as st
import requests
from typing import List, Optional
from wordle_solver import WordleSolver
from api_server import FeedbackItem
import time
import random

# Constants
API_URL = "http://localhost:8000"
MAX_DISPLAY_WORDS = 50
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds
SEED_RANGE = 1000000
MAX_GUESSES = 6


def get_feedback_from_api(guess: str, seed: Optional[int] = None) -> List[FeedbackItem]:
    """Get feedback from the API with retry logic."""
    params = {"guess": guess}
    if seed is not None:
        params["seed"] = seed
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(
                f"{API_URL}/random",
                params=params,
                timeout=5  # Add timeout
            )
            response.raise_for_status()  # Raise exception for bad status codes
            return [FeedbackItem(**item) for item in response.json()]
        except requests.exceptions.RequestException as e:
            if attempt == MAX_RETRIES - 1:  # Last attempt
                st.error(f"Failed to connect to API after {MAX_RETRIES} attempts. Please ensure the API server is running.")
                return []
            time.sleep(RETRY_DELAY)
    
    return []

def display_feedback(guess: str, feedback: List[FeedbackItem]):
    """Display the feedback for a guess with color coding."""
    cols = st.columns(5)
    for i, (col, letter, fb) in enumerate(zip(cols, guess, feedback)):
        with col:
            color = {
                "correct": "green",
                "present": "yellow",
                "absent": "gray"
            }.get(fb.result, "white")
            
            st.markdown(
                f'<div style="background-color: {color}; '
                f'color: white; text-align: center; padding: 10px; '
                f'border-radius: 5px; font-size: 24px;">{letter.upper()}</div>',
                unsafe_allow_html=True
            )

def is_win(feedback: List[FeedbackItem]) -> bool:
    return all(fb.result == "correct" for fb in feedback)

def main():
    st.title("Wordle Solver")
    
    # Add API status check
    try:
        requests.get(f"{API_URL}/docs", timeout=2)
        st.success("API server is running")
    except requests.exceptions.RequestException:
        st.error("⚠️ API server is not running. Please start it with: uvicorn api_server:app --reload")
        st.stop()
    
    # Initialize session state
    if "solver" not in st.session_state:
        st.session_state.solver = WordleSolver()
    if "guesses" not in st.session_state:
        st.session_state.guesses = []
    if "feedback" not in st.session_state:
        st.session_state.feedback = []
    if "seed" not in st.session_state:
        st.session_state.seed = None
    if "game_over" not in st.session_state:
        st.session_state.game_over = False
    if "win" not in st.session_state:
        st.session_state.win = False
    
    # Game controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("New Game"):
            st.session_state.solver = WordleSolver()
            st.session_state.guesses = []
            st.session_state.feedback = []
            st.session_state.seed = None
            st.session_state.game_over = False
            st.session_state.win = False
    
    with col2:
        use_seed = st.checkbox("Use custom seed")
        if use_seed:
            st.session_state.seed = st.number_input(
                "Seed", min_value=0, max_value=1000000, value=0
            )
    
    # Check for win or game over
    if st.session_state.feedback:
        if is_win(st.session_state.feedback[-1]):
            st.session_state.win = True
            st.session_state.game_over = True
        elif len(st.session_state.guesses) >= MAX_GUESSES:
            st.session_state.game_over = True

    # Make next guess
    make_guess_disabled = st.session_state.game_over
    if st.button("Make Next Guess", disabled=make_guess_disabled):
        with st.spinner("Calculating next guess..."):
            guess = st.session_state.solver.get_best_guess()
            if guess:
                feedback = get_feedback_from_api(guess, st.session_state.seed)
                if feedback:
                    st.session_state.guesses.append(guess)
                    st.session_state.feedback.append(feedback)
                    st.session_state.solver.make_guess(guess, feedback)
                    # Check for win after making guess
                    if is_win(feedback):
                        st.session_state.win = True
                        st.session_state.game_over = True
                    elif len(st.session_state.guesses) >= MAX_GUESSES:
                        st.session_state.game_over = True
    
    # Display game history
    for guess, feedback in zip(st.session_state.guesses, st.session_state.feedback):
        display_feedback(guess, feedback)
        st.markdown("---")
    
    # Show win/game over messages
    if st.session_state.win:
        st.success(f"You Win! The word was '{st.session_state.guesses[-1].upper()}'.")
    elif st.session_state.game_over:
        st.error("Game Over! You've used all 6 guesses.")
        if st.session_state.feedback:
            # Show the correct word if possible
            remaining = st.session_state.solver.get_remaining_words()
            if len(remaining) == 1:
                st.info(f"The correct word was: {remaining[0].upper()}")

    # Display remaining words
    remaining_words = st.session_state.solver.get_remaining_words()
    if remaining_words and not st.session_state.win:
        st.subheader(f"Remaining Possible Words ({len(remaining_words)})")
        words_to_show = remaining_words[:MAX_DISPLAY_WORDS]
        st.write(", ".join(words_to_show))
        if len(remaining_words) > MAX_DISPLAY_WORDS:
            st.write(f"... and {len(remaining_words) - MAX_DISPLAY_WORDS} more")

if __name__ == "__main__":
    main() 