from __future__ import annotations

import abc
import re

from hertavilla.message.chain import MessageChain


class Match(abc.ABC):
    @abc.abstractmethod
    def check(self, chain: MessageChain) -> bool:
        raise NotImplementedError


class Regex(Match):
    def __init__(self, pattern: str | re.Pattern) -> None:
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        self.pattern = pattern

    def __repr__(self) -> str:
        return f"<Match:Regex pattern={self.pattern!r}>"

    def check(self, chain: MessageChain) -> bool:
        return re.match(self.pattern, chain.plaintext) is not None


class Startswith(Match):
    def __init__(self, prefix: str) -> None:
        self.prefix = prefix

    def check(self, chain: MessageChain) -> bool:
        return chain.plaintext.startswith(self.prefix)

    def __repr__(self) -> str:
        return f"<Match:Startswith prefix={self.prefix!r}>"


class Endswith(Match):
    def __init__(self, suffix: str) -> None:
        self.suffix = suffix

    def check(self, chain: MessageChain) -> bool:
        return chain.plaintext.endswith(self.suffix)

    def __repr__(self) -> str:
        return f"<Match:Endswith suffix={self.suffix!r}>"


class Keywords(Regex):
    def __init__(self, *keywords: str) -> None:
        self.keywords = keywords
        self.pattern = re.compile("|".join(keywords))

    def __repr__(self) -> str:
        return f"<Match:Keywords words={self.keywords!r}>"
