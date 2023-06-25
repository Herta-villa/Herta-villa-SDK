from __future__ import annotations

import sys

# Because of pydantic's exception
# Herta SDK provides this `TypedDict`
# Import it by this:
# from hertavilla.typing import TypedDict

# Pydantic exception:
#   TypeError: You should use `typing_extensions.TypedDict`
#   instead of `typing.TypedDict` with Python < 3.9.2.
#   Without it, there is no way to differentiate
#   required and optional fields when subclassed.

if sys.version_info >= (3, 9, 2):
    from typing import TypedDict as TypedDict
else:
    from typing_extensions import TypedDict as TypedDict
