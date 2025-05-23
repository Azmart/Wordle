# Wordle Solver

A Wordle puzzle solver that uses Knuth's minimax algorithm to find the solution. The solver includes a FastAPI backend and a Streamlit frontend.

## Features

- FastAPI backend with seeded word selection
- Streamlit frontend with visual feedback
- Knuth's minimax algorithm implementation
- Proper handling of duplicate letters
- Caching for improved performance
- Optional seed for reproducible games

## Setup

1. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2. **Start the FastAPI server:**
    ```bash
    uvicorn api_server:app --reload
    ```
3. **In a new terminal, start the Streamlit frontend:**
    ```bash
    streamlit run app.py
    ```

## Usage

1. Open your browser to [http://localhost:8501](http://localhost:8501)
2. Click **"New Game"** to start
3. Optionally set a seed for reproducible games
4. Click **"Make Next Guess"** to see the solver's next move
5. The solver will automatically narrow down the possible words based on feedback

## Project Structure

- `api_server.py`: FastAPI backend with word selection and feedback logic
- `wordle_solver.py`: Implementation of Knuth's minimax algorithm
- `word_utils.py`: Shared utilities for word loading and validation
- `app.py`: Streamlit frontend with game controls and visual feedback
- `wordle_merged.csv`: Dictionary of valid 5-letter words

## Notes

- The solver starts with **"stare"** as its first guess, which is an optimal starting word
- The minimax algorithm ensures the solver minimizes the worst-case number of remaining possible words
- Feedback is color-coded: green for correct, yellow for present, gray for absent
- The first 50 remaining possible words are displayed at each step

## Credits

Credit goes to Github user Steve Casica for providing the [wordle.csv](https://github.com/steve-kasica/wordle-words/blob/master/wordle.csv) file.  
Also to Florida State University for providing a dataset with over 32,000 5-letter words: [Pentagram Word List](https://people.sc.fsu.edu/~jburkardt/datasets/words/pentagram.html#Wordle)