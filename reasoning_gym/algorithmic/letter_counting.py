"""Letter counting task generator"""
from dataclasses import dataclass
import re
from random import Random
from typing import List, Optional

from reasoning_gym.data import read_data_file

@dataclass
class LetterCountingConfig:
    """Configuration for letter counting task generation"""
    min_words: int = 5          # Minimum words in span
    max_words: int = 15         # Maximum words in span
    seed: Optional[int] = None
    size: int = 500            # Virtual dataset size

    def validate(self):
        """Validate configuration parameters"""
        assert self.min_words > 0, "min_words must be positive"
        assert self.max_words >= self.min_words, "max_words must be >= min_words"


class LetterCountingDataset:
    """Generates letter counting tasks from text spans"""

    def __init__(self, config: LetterCountingConfig):
        self.config = config
        self.config.validate()
        self.seed = config.seed if config.seed is not None else Random().randint(0, 2**32)
        
        # Load and preprocess text
        text = read_data_file("in_the_year_2889.txt")
        # Extract words and clean them to contain only alphanumeric characters
        self.words = [word for word in re.findall(r'\b\w+\b', text) if word.isalnum()]

    def __len__(self) -> int:
        return self.config.size

    def __iter__(self):
        self._current_idx = 0
        return self

    def __next__(self):
        if self._current_idx >= self.config.size:
            raise StopIteration
        item = self[self._current_idx]
        self._current_idx += 1
        return item

    def __getitem__(self, idx: int) -> dict:
        """Generate a single letter counting task"""
        rng = Random(self.seed + idx)
        
        # Select random span of words
        span_length = rng.randint(self.config.min_words, self.config.max_words)
        start_idx = rng.randint(0, len(self.words) - span_length)
        span = self.words[start_idx:start_idx + span_length]
        
        # Get all unique letters from span
        letters = set(''.join(span).lower())
        if not letters:
            letters = {'a'}  # Fallback if span has no letters
            
        # Select random letter that appears in the span
        target_letter = rng.choice(list(letters))
        
        # Count occurrences
        count = sum(word.lower().count(target_letter) for word in span)
        
        return {
            "question": f'How many times does the letter "{target_letter}" appear in the text: "{" ".join(span)}"?',
            "answer": str(count),
            "metadata": {
                "span_length": span_length,
                "target_letter": target_letter,
                "span": span
            }
        }


def letter_counting_dataset(
    min_words: int = 5,
    max_words: int = 15,
    seed: Optional[int] = None,
    size: int = 500,
) -> LetterCountingDataset:
    """Create a LetterCountingDataset with the given configuration."""
    config = LetterCountingConfig(
        min_words=min_words,
        max_words=max_words,
        seed=seed,
        size=size,
    )
    return LetterCountingDataset(config)