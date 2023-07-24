from dataclasses import dataclass
from typing import Optional

import codetiming


@dataclass
class Timer(codetiming.Timer):
    """
    Customized subclass of ``codetiming.Timer``
    """

    name: Optional[str] = None

    def __post_init__(self):
        if self.name is not None:
            self.text = f"'{self.name}' elapsed time: {{:.4f}} seconds"
