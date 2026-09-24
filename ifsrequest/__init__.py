"""Top‑level package for **ifsrequest**.

The public API consists of the :class:`~ifsrequest.ifsrequest.IfsRequest`
client class and the accompanying :class:`~ifsrequest.ifsrequest.IfsRequestError`
exception.  Exporting them via ``__all__`` makes ``from ifsrequest import *``
behave predictably and signals to static‑analysis tools which names are
intended for external use.
"""

from .ifsrequest import IfsRequest, IfsRequestError

# Define the symbols that are part of the public interface of the package.
__all__ = ["IfsRequest", "IfsRequestError"]