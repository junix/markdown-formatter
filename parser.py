from typing import Iterable


class Rule:
    def execute(self, seq) -> Iterable[str]:
        ...


class Text(Rule):
    def __init__(self, text: str):
        assert isinstance(text, str)
        self.text = text

    def execute(self, seq) -> Iterable[str]:
        if seq.startswith(self.text):
            yield self.text

    def __repr__(self):
        return self.text


def _to_rule(rule):
    if isinstance(rule, Rule):
        return rule
    if isinstance(rule, str):
        return Text(rule)
    raise TypeError(f"un-support rule type:{type(rule)}")


def _to_rules(*rules):
    return tuple(_to_rule(r) for r in rules)


class Or(Rule):
    def __init__(self, *rules):
        self.rules = _to_rules(*rules)

    def execute(self, seq) -> Iterable[str]:
        if not self.rules:
            yield ""
        else:
            for r in self.rules:
                yield from r.execute(seq)

    def __repr__(self):
        return f"Or({','.join(str(r) for r in self.rules)})"


class Maybe(Rule):
    def __init__(self, rule):
        self.rule = _to_rule(rule)

    def execute(self, seq) -> Iterable[str]:
        yield ""
        yield from self.rule.execute(seq)

    def __repr__(self):
        return f"Maybe({self.rule})"


class OneOrMore(Rule):
    def __init__(self, rule):
        self.rule = _to_rule(rule)

    def execute(self, seq) -> Iterable[str]:
        for m in self.rule.execute(seq):
            yield m
            if not m:
                continue
            yield from OneOrMore(self.rule).execute(seq[len(m):])

    def __repr__(self):
        return f"OneOrMore({self.rule})"

class Seq(Rule):
    def __init__(self, *rules):
        self.rules = _to_rules(*rules)

    def execute(self, seq) -> Iterable[str]:
        if not self.rules:
            yield ""
        else:
            head = self.rules[0]
            remain = self.rules[1:]
            for m in head.execute(seq):
                print(f"{head} match>", m)
                for r in Seq(*remain).execute(seq[len(m):]):
                    yield m + r

    def __repr__(self):
        return f"Seq({','.join(str(r) for r in self.rules)})"


s = "abc"
rule = Seq(OneOrMore(Or('a', 'b', 'c')), 'b')
for s in rule.execute(s):
    print(s)
