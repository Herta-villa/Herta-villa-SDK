from __future__ import annotations

import abc
from contextvars import ContextVar
from dataclasses import dataclass
import re

from hertavilla.message.chain import MessageChain

current_match_result: ContextVar[MatchResult] = ContextVar(
    "currect_match_result",
)


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
        match = re.match(self.pattern, chain.plaintext)
        if match is not None:
            current_match_result.set(RegexResult(match=self, re_match=match))
            return True
        return False


class Startswith(Match):
    def __init__(self, prefix: str) -> None:
        self.prefix = prefix

    def check(self, chain: MessageChain) -> bool:
        plain = chain.plaintext
        if plain.startswith(self.prefix):
            current_match_result.set(
                StartswithResult(match=self, text=plain[len(self.prefix) :]),
            )
            return True
        return False

    def __repr__(self) -> str:
        return f"<Match:Startswith prefix={self.prefix!r}>"


class Endswith(Match):
    def __init__(self, suffix: str) -> None:
        self.suffix = suffix

    def check(self, chain: MessageChain) -> bool:
        plain = chain.plaintext
        if plain.endswith(self.suffix):
            current_match_result.set(
                EndswithResult(match=self, text=plain[: len(self.suffix)]),
            )
            return True
        return False

    def __repr__(self) -> str:
        return f"<Match:Endswith suffix={self.suffix!r}>"


class Keywords(Regex):
    def __init__(self, *keywords: str) -> None:
        self.keywords = keywords
        self.pattern = re.compile("|".join(keywords))

    def __repr__(self) -> str:
        return f"<Match:Keywords words={self.keywords!r}>"

    def check(self, chain: MessageChain) -> bool:
        match = re.match(self.pattern, chain.plaintext)
        if match is not None:
            matches = re.findall(self.pattern, chain.plaintext)
            current_match_result.set(
                KeywordsResult(match=self, matched_keywords=set(matches)),
            )
            return True
        return False


@dataclass
class MatchResult:
    match: Match


@dataclass
class RegexResult(MatchResult):
    match: Regex
    re_match: re.Match

    @property
    def pattern(self) -> re.Pattern:
        return self.match.pattern


@dataclass
class StartswithResult(MatchResult):
    match: Startswith
    text: str

    @property
    def prefix(self) -> str:
        return self.match.prefix


@dataclass
class EndswithResult(MatchResult):
    match: Endswith
    text: str

    @property
    def suffix(self) -> str:
        return self.match.suffix


@dataclass
class KeywordsResult(MatchResult):
    match: Keywords
    matched_keywords: set[str]

    @property
    def keywords(self) -> tuple[str]:
        return self.match.keywords
