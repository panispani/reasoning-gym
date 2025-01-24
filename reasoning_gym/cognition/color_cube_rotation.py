import random
from dataclasses import dataclass
from enum import StrEnum
from typing import Dict, List, Optional, Tuple

from ..dataset import ProceduralDataset


class Color(StrEnum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    YELLOW = "yellow"
    WHITE = "white"
    ORANGE = "orange"


class Side(StrEnum):
    TOP = "top"
    RIGHT = "right"
    FRONT = "front"
    LEFT = "left"
    BACK = "back"
    BOTTOM = "bottom"


@dataclass
class Cube:
    """Represents a cube with colored sides"""
    colors: Dict[Side, Color]

    def rotate_front_to_top(self) -> None:
        """Rotate cube so front face becomes top"""
        old = self.colors.copy()
        self.colors[Side.TOP] = old[Side.FRONT]
        self.colors[Side.FRONT] = old[Side.BOTTOM]
        self.colors[Side.BOTTOM] = old[Side.BACK]
        self.colors[Side.BACK] = old[Side.TOP]
        # Right and left stay in place

    def rotate_right_to_top(self) -> None:
        """Rotate cube so right face becomes top"""
        old = self.colors.copy()
        self.colors[Side.TOP] = old[Side.RIGHT]
        self.colors[Side.RIGHT] = old[Side.BOTTOM]
        self.colors[Side.BOTTOM] = old[Side.LEFT]
        self.colors[Side.LEFT] = old[Side.TOP]
        # Front and back stay in place

    def rotate_back_to_top(self) -> None:
        """Rotate cube so back face becomes top"""
        old = self.colors.copy()
        self.colors[Side.TOP] = old[Side.BACK]
        self.colors[Side.BACK] = old[Side.BOTTOM]
        self.colors[Side.BOTTOM] = old[Side.FRONT]
        self.colors[Side.FRONT] = old[Side.TOP]
        # Right and left stay in place

    def rotate_left_to_top(self) -> None:
        """Rotate cube so left face becomes top"""
        old = self.colors.copy()
        self.colors[Side.TOP] = old[Side.LEFT]
        self.colors[Side.LEFT] = old[Side.BOTTOM]
        self.colors[Side.BOTTOM] = old[Side.RIGHT]
        self.colors[Side.RIGHT] = old[Side.TOP]
        # Front and back stay in place

    def rotate_bottom_to_top(self) -> None:
        """Rotate cube so bottom face becomes top"""
        old = self.colors.copy()
        self.colors[Side.TOP] = old[Side.BOTTOM]
        self.colors[Side.BOTTOM] = old[Side.TOP]
        self.colors[Side.FRONT] = old[Side.BACK]
        self.colors[Side.BACK] = old[Side.FRONT]
        # Right and left stay in place


@dataclass
class ColorCubeRotationConfig:
    """Configuration for color cube rotation task generation"""
    min_rotations: int = 1
    max_rotations: int = 3
    seed: Optional[int] = None
    size: int = 500

    def validate(self):
        """Validate configuration parameters"""
        assert self.min_rotations > 0, "min_rotations must be positive"
        assert self.max_rotations >= self.min_rotations, "max_rotations must be >= min_rotations"


class ColorCubeRotationDataset(ProceduralDataset):
    """Generates color cube rotation reasoning tasks"""

    def __init__(self, config: ColorCubeRotationConfig):
        self.config = config
        self.config.validate()
        super().__init__(seed=config.seed, size=config.size)

    def __getitem__(self, idx: int) -> dict:
        rng = random.Random(self.seed + idx)
        
        # Generate initial cube state
        cube = self._generate_cube(rng)
        initial_state = cube.colors.copy()
        
        # Generate sequence of rotations
        num_rotations = rng.randint(self.config.min_rotations, self.config.max_rotations)
        rotations = []
        for _ in range(num_rotations):
            from_side = rng.choice(list(Side))
            if from_side != Side.TOP:  # Skip meaningless top-to-top rotation
                rotations.append(from_side)
                self._rotate_to_top(cube, from_side)
        
        # Select target side for question
        target_side = rng.choice(list(Side))
        
        # Generate story
        story = self._generate_story(initial_state, rotations, target_side)
        
        return {
            "question": story,
            "answer": cube.colors[target_side],
            "metadata": {
                "initial_state": {k.value: v.value for k,v in initial_state.items()},
                "rotations": [r.value for r in rotations],
                "target_side": target_side.value,
                "num_rotations": num_rotations,
            }
        }

    def _generate_cube(self, rng: random.Random) -> Cube:
        """Generate a cube with random colors"""
        colors = list(Color)
        rng.shuffle(colors)  # Randomize color order
        return Cube({side: color for side, color in zip(Side, colors)})

    def _rotate_to_top(self, cube: Cube, from_side: Side) -> None:
        """Rotate cube so that given side becomes top"""
        rotation_map = {
            Side.FRONT: cube.rotate_front_to_top,
            Side.RIGHT: cube.rotate_right_to_top,
            Side.BACK: cube.rotate_back_to_top,
            Side.LEFT: cube.rotate_left_to_top,
            Side.BOTTOM: cube.rotate_bottom_to_top,
        }
        if from_side in rotation_map:
            rotation_map[from_side]()

    def _generate_story(self, initial_state: Dict[Side, Color], 
                       rotations: List[Side], target_side: Side) -> str:
        """Generate story describing cube state and rotations"""
        # Describe initial state
        story_parts = ["A cube has:"]
        for side in Side:
            story_parts.append(f"- a {initial_state[side].value} {side.value} side")
        
        # Describe rotations
        for from_side in rotations:
            story_parts.append(
                f"\nThe cube is rotated so that the side which was before at the {from_side.value} "
                "is now at the top."
            )
        
        # Ask question
        story_parts.append(f"\nWhat is now the color of the {target_side.value} side of the cube?")
        
        return "\n".join(story_parts)


def color_cube_rotation_dataset(
    min_rotations: int = 1,
    max_rotations: int = 3,
    seed: Optional[int] = None,
    size: int = 500,
) -> ColorCubeRotationDataset:
    """Create a ColorCubeRotationDataset with the given configuration"""
    config = ColorCubeRotationConfig(
        min_rotations=min_rotations,
        max_rotations=max_rotations,
        seed=seed,
        size=size,
    )
    return ColorCubeRotationDataset(config)