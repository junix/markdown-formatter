import re
from typing import Optional, Tuple


class Reg:
    def __init__(self, pattern):
        self.pattern = pattern

    def __repr__(self):
        return f"Reg({self.pattern})"


class Matcher:
    def __init__(self, text):
        self.remain = text
        self.captured = None

    def match(self, *patterns) -> Optional[Tuple[str, str]]:
        res = self.peek(*patterns)
        if res is None:
            return None
        cap, self.remain = res
        self.acc_captured(cap)
        return res

    def acc_captured(self, cap):
        if cap is None:
            return

        if self.captured is None:
            self.captured = cap
        else:
            self.captured += cap

    def match_util(self, delim) -> Optional[Tuple[str, str]]:
        try:
            matcher = Matcher(self.remain)
            while True:
                c, text = matcher.match(delim, Reg(r'\\?.'))
                if c == delim:
                    self.remain = matcher.remain
                    self.acc_captured(matcher.captured)
                    return matcher.captured, matcher.remain
        except:
            return None

    def match_pair(self, delim):
        try:
            m = Matcher(self.remain)
            if m.match(delim) and m.match_util(delim):
                self.remain = m.remain
                self.acc_captured(m.captured)
                return m.captured, m.remain
        except:
            return None

    def __bool__(self):
        return self.captured is not None

    def peek(self, *patterns):
        return self.try_match(*patterns)

    def _try_match_re(self, *regexps):
        if not regexps:
            raise ValueError("nil regexps")
        for r in regexps:
            if isinstance(r, str):
                if not r.startswith('^') and not r.endswith('$'):
                    r = '^' + r
                r = re.compile(r)
            assert isinstance(r, re.Pattern)
            m = r.search(self.remain)
            if not m:
                return None
            return m.group(0), self.remain[len(m.group(0)):]
        return None

    def _try_match_str(self, *starts):
        if not starts:
            raise ValueError("nil starts")
        for s in starts:
            if self.remain.startswith(s):
                return s, self.remain[len(s):]
        return None

    def try_match(self, *patterns):
        if not patterns:
            raise ValueError("nil patterns")

        for p in patterns:
            if isinstance(p, str):
                m = self._try_match_str(p)
            elif isinstance(p, Reg):
                m = self._try_match_re(p.pattern)
            elif isinstance(p, re.Pattern):
                m = self._try_match_re(p)
            else:
                raise TypeError(f"unknown-pattern:{p}")

            if m is not None:
                return m
        return None

    def __repr__(self):
        return f"Matcher(captured={self.captured}, remain={self.remain})"


if __name__ == '__main__':
    from re import compile as c

    # matcher = Matcher(r'$as\o\]\\*\$df\\$')
    m = Matcher(r'code block\``')
    print(m.match_util('`'))
    s = "ba\\**$"
    m = Matcher("asdf")
    if m:
        print(m)
    m.match('a')
    if m:
        print(m)
    if m.match(""):
        print("matched")
    # print(match(s, c(r'^[ab]+')))
    # while s:
    #     m, s = expect(s, seq=r'\*') or expect(s, regex='.')
    #     print(m)
