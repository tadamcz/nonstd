import numpy as np
import pytest


@pytest.fixture(
    params=[
        100329066,
        998566290,
        271744546,
        159245994,
        267638719,
    ],
    ids=lambda p: f"seed={p}",
)
def random_seed(request):
    np.random.seed(request.param)
