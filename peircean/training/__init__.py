"""
Peircean Abduction: Training Module

Tools for generating training data that embeds abductive reasoning
patterns into language models.
"""

from .generator import AbductiveDataGenerator, AbductiveExample

__all__ = [
    "AbductiveDataGenerator",
    "AbductiveExample",
]
