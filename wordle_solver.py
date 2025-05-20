from typing import List, Dict, Set, Tuple
from functools import lru_cache
from word_utils import WORDS, VALID_WORDS
from api_server import get_feedback, FeedbackItem
import random

class WordleSolver:
    def __init__(self):
        self.possible_words = set(WORDS)
        self.first_guess = "stare"  # Optimal first guess
        self._feedback_cache = {}
    
    @lru_cache(maxsize=10000)
    def get_feedback_key(self, feedback: Tuple[Tuple[int, str, str], ...]) -> str:
        """Convert feedback to a hashable key for caching."""
        return str(feedback)
    
    def filter_words(self, guess: str, feedback: List[FeedbackItem]) -> Set[str]:
        """Filter possible words based on feedback."""
        new_possible = set()
        feedback_tuple = tuple((f.slot, f.guess, f.result) for f in feedback)
        
        # Use cached feedback if available
        cache_key = (guess, feedback_tuple)
        if cache_key in self._feedback_cache:
            return self._feedback_cache[cache_key]
        
        for word in self.possible_words:
            word_feedback = get_feedback(guess, word)
            word_feedback_tuple = tuple((f.slot, f.guess, f.result) for f in word_feedback)
            if word_feedback_tuple == feedback_tuple:
                new_possible.add(word)
        
        # Cache the result
        self._feedback_cache[cache_key] = new_possible
        return new_possible
    
    def get_best_guess(self) -> str:
        """Get the best guess using an optimized minimax algorithm."""
        if not self.possible_words:
            return ""
        
        if len(self.possible_words) == 1:
            return next(iter(self.possible_words))
        
        # If this is the first guess, use the optimal starting word
        if len(self.possible_words) == len(WORDS):
            return self.first_guess
        
        # For small solution sets, just pick a random word
        if len(self.possible_words) <= 3:
            return random.choice(list(self.possible_words))
        
        # Use a subset of words for faster computation
        sample_size = min(100, len(self.possible_words))
        sample_words = random.sample(list(self.possible_words), sample_size)
        
        best_guess = None
        min_max_bucket_size = float('inf')
        
        # Consider only a subset of possible guesses
        guess_candidates = random.sample(list(VALID_WORDS), min(100, len(VALID_WORDS)))
        
        for guess in guess_candidates:
            # Simulate feedback for each possible solution
            buckets: Dict[str, Set[str]] = {}
            
            for solution in sample_words:
                feedback = get_feedback(guess, solution)
                feedback_key = self.get_feedback_key(
                    tuple((f.slot, f.guess, f.result) for f in feedback)
                )
                
                if feedback_key not in buckets:
                    buckets[feedback_key] = set()
                buckets[feedback_key].add(solution)
            
            # Find the size of the largest bucket
            max_bucket_size = max(len(bucket) for bucket in buckets.values())
            
            # Update best guess if this one has a smaller worst-case bucket
            if max_bucket_size < min_max_bucket_size:
                min_max_bucket_size = max_bucket_size
                best_guess = guess
        
        return best_guess or random.choice(list(self.possible_words))
    
    def make_guess(self, guess: str, feedback: List[FeedbackItem]) -> None:
        """Update possible words based on feedback from a guess."""
        self.possible_words = self.filter_words(guess, feedback)
    
    def get_remaining_words(self) -> List[str]:
        """Get list of remaining possible words."""
        return sorted(list(self.possible_words)) 