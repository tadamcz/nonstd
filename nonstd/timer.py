from dataclasses import dataclass

import codetiming


@dataclass
class Timer(codetiming.Timer):
    """
    Customized subclass of ``codetiming.Timer``
    """

    def __post_init__(self):
        if self.name is not None:
            self.text = f"'{self.name}' elapsed time: {{:.4f}} seconds"
