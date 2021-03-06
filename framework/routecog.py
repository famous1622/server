# Stdlib
import inspect

# Sayonika Internals
from framework.objects import logger
from framework.route import Route
from framework.sayonika import Sayonika

__all__ = ("RouteCog",)


class RouteCog:
    """
    Similar to a discord.py cog, this holds several routes with unified concept
    """

    def __init__(self, core: Sayonika):
        self.core = core
        self.logger = logger

    def register(self):
        for _, member in inspect.getmembers(self):
            if isinstance(member, Route):
                member.set_parent(self)
                member.register(self.core)
