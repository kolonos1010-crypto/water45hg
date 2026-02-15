"""Configuration loader: reads notes.txt for MODULE and API_KEYS."""

import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class Config:
    module: int = 1
    api_keys: List[str] = field(default_factory=list)
    notes_path: str = "notes.txt"

    @classmethod
    def from_file(cls, path: str = "notes.txt") -> "Config":
        """Parse notes.txt and return a Config instance.

        Expected format:
            MODULE: 1
            API_KEYS: key1,key2,key3
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Notes file not found: {path}")

        module = 1
        api_keys: List[str] = []

        with open(path, "r", encoding="utf-8") as fh:
            for raw_line in fh:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue

                if line.upper().startswith("MODULE:"):
                    value = line.split(":", 1)[1].strip()
                    module = int(value)
                elif line.upper().startswith("API_KEYS:"):
                    value = line.split(":", 1)[1].strip()
                    api_keys = [k.strip() for k in value.split(",") if k.strip()]

        if not api_keys:
            raise ValueError("No API keys found in notes file")

        return cls(module=module, api_keys=api_keys, notes_path=path)

    @property
    def current_key(self) -> str:
        """Return the first available API key."""
        if not self.api_keys:
            raise ValueError("No API keys available")
        return self.api_keys[0]

    def rotate_key(self) -> str:
        """Move the current key to the end and return the new current key."""
        if len(self.api_keys) < 2:
            raise ValueError("No more API keys to rotate to")
        drained = self.api_keys.pop(0)
        return drained
