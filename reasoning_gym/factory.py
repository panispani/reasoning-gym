from dataclasses import is_dataclass
from typing import Any, Dict, Type, TypeVar

from .dataset import ProceduralDataset

# Type variables for generic type hints
ConfigT = TypeVar('ConfigT')
DatasetT = TypeVar('DatasetT', bound=ProceduralDataset)

# Global registry of datasets
_DATASETS: Dict[str, tuple[Type[ProceduralDataset], Type]] = {}

def register_dataset(
    name: str,
    dataset_cls: Type[DatasetT],
    config_cls: Type[ConfigT]
) -> None:
    """
    Register a dataset class with its configuration class.
    
    Args:
        name: Unique identifier for the dataset
        dataset_cls: Class derived from ProceduralDataset
        config_cls: Configuration dataclass for the dataset
    
    Raises:
        ValueError: If name is already registered or invalid types provided
    """
    if name in _DATASETS:
        raise ValueError(f"Dataset '{name}' is already registered")
    
    if not issubclass(dataset_cls, ProceduralDataset):
        raise ValueError(
            f"Dataset class must inherit from ProceduralDataset, got {dataset_cls}"
        )
    
    if not is_dataclass(config_cls):
        raise ValueError(
            f"Config class must be a dataclass, got {config_cls}"
        )
    
    _DATASETS[name] = (dataset_cls, config_cls)

def create_dataset(
    name: str,
    config: Any,
    seed: int = None,
    size: int = 500
) -> ProceduralDataset:
    """
    Create a dataset instance by name with the given configuration.
    
    Args:
        name: Registered dataset name
        config: Configuration instance for the dataset
        seed: Optional random seed
        size: Size of the dataset (default: 500)
    
    Returns:
        Configured dataset instance
        
    Raises:
        ValueError: If dataset not found or config type mismatch
    """
    if name not in _DATASETS:
        raise ValueError(f"Dataset '{name}' not found")
        
    dataset_cls, config_cls = _DATASETS[name]
    
    if not isinstance(config, config_cls):
        raise ValueError(
            f"Config must be instance of {config_cls.__name__}, got {type(config).__name__}"
        )
        
    return dataset_cls(config=config, seed=seed, size=size)