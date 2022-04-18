import re


def seek_util(text: str, delim: str):
    acc = []
    while text:
        if text[0] == delim:
            acc.append(text[0])
            return ''.join(acc)
        n_step = 2 if text[0] == '\\' else 1
        acc.append(text[:n_step])
        text = text[n_step:]
    return None


def seek_pair(text: str, delim: str):
    if not text or not text.startswith(delim):
        return None
    text = text[len(delim):]
    remain = seek_util(text, delim)
    return delim + remain if remain else None


def match_re(text, *regexps):
    if not regexps:
        raise ValueError("regexps at least set one value")
    for r in regexps:
        if isinstance(r, str):
            if not r.startswith('^') and not r.endswith('$'):
                r = '^' + r
            r = re.compile(r)
        assert isinstance(r, re.Pattern)
        m = r.search(text)
        if not m:
            return None
        return m.group(0), text[len(m.group(0)):]
    return None


def match_str(text, *starts):
    if not starts:
        raise ValueError("starts at least set one value")
    for s in starts:
        if text.startswith(s):
            return s, text[len(s):]
    return None


if __name__ == '__main__':
    s = "ba\\**"
    # print(seek_util(s, '$'))
    print(match_re(s, 'a'))
    # while s:
    #     m, s = expect(s, seq=r'\*') or expect(s, regex='.')
    #     print(m)
