from typing import Iterable
import re
from strs import *
from img import *


class Segment:
    def __init__(self, text):
        self.text = text

    def format(self):
        pass


formula_pattern = re.compile(r'^([$]*)(.*?)([$]*)$')


class FormulaSeg(Segment):
    def __init__(self, text):
        super().__init__(text)

    def __repr__(self):
        return f'FormulaSeg({self.text})'

    @classmethod
    def expect(cls, text):
        if text[:1] != '$':
            return None
        seg = seek_pair(text, '$')
        if not seg:
            return None
        return FormulaSeg(seg), text[len(seg):]

    def format(self):
        from tex import regularize_formula
        if not self.text or self.text.strip() == '$$':
            return

        m = formula_pattern.search(self.text)
        body = m.group(2)
        body = regularize_formula(body)
        self.text = m.group(1) + body + m.group(3)


class CodeSeg(Segment):
    def __init__(self, text):
        super().__init__(text)

    def __repr__(self):
        return f'CodeSeg({self.text})'

    @classmethod
    def expect(cls, text):
        if text[:1] != '`':
            return None
        seg = seek_pair(text, '`')
        if not seg:
            return None
        return CodeSeg(seg), text[len(seg):]


class TextSeg(Segment):
    def __init__(self, text):
        super().__init__(text)

    def __repr__(self):
        return f'TextSeg({self.text})'


class TagSeg(Segment):
    def __init__(self, text):
        super().__init__(text)

    def __repr__(self):
        return f'TagSeg({self.text})'

    @classmethod
    def expect(cls, text):
        from htmls import seek_html_tag
        # img -> zoom html mark
        rs = parse_img(text)
        if rs:
            src = rs['src']
            ratio = calc_zoom_ratio(src, max_height=200)
            return TagSeg(to_html_img(src, rs['alt'], ratio)), rs['remain']

        if text[:1] != '<':
            return None
        seg = seek_html_tag(text)
        if not seg:
            return None
        return TagSeg(seg), text[len(seg):]


def parse_to_segs(line: str) -> Iterable[Segment]:
    text = []
    while line:
        rs = FormulaSeg.expect(line) or CodeSeg.expect(line) or TagSeg.expect(line)
        if rs is not None:
            if text:
                yield TextSeg(''.join(text))
                text = []
            seg, line = rs
            yield seg
        else:
            n_step = 2 if line[0] == '\\' else 1
            text.append(line[:n_step])
            line = line[n_step:]
    if text:
        yield TextSeg(''.join(text))


def parse_img(s):
    if len(s) < 5:
        return None
    if s[:2] != '![':
        return None
    s = s[2:]
    alt = seek_util(s, ']')
    if alt is None:
        return None
    s = s[len(alt):]
    alt = alt[:-1]
    if s[:1] != '(':
        return None
    s = s[1:]
    url = seek_util(s, ')')
    if url is None:
        return None
    s = s[len(url):]
    url = url[:-1]
    return {
        'alt': alt,
        'src': url,
        'remain': s
    }


def to_html_img(src, alt, zoom=100):
    return f'<img src="{src}" alt="{alt}" style="zoom:{int(zoom)}%;"/>'


def join_segs(*segs):
    texts = [s.text.rstrip() if index == 0 else s.text.strip() for index, s in enumerate(segs)]
    return ''.join(texts)


def expect_italic_mark(s):
    if len(s) <= 2:
        return None
    if s[0] != '*'
    ...

if __name__ == '__main__':
    # s = "v\\$ok$f(x)$k`\\'o`k"
    s = "  假设  $f(x)$  具有二阶连![img](http://a.b.c)续偏导数，若第$k$ 次迭代值为$x^{(k)}$, 则可将$f(x)$ 在$x^{(k)}$ 附近进行二阶<ok>泰勒展开:"
    segs = list(parse_to_segs(s))
    print(s)
    for s in segs:
        print(s)
    # s = "![img](http://a.b.c)续偏导数，若第$k$ "
    # v = parse_img(s)
    # print(v)
    # for s in segs:
    #     print(s)
    # print(join_segs(*segs))
    # s = "$ok,\\mathbb{E}   ,$"
    # s = FormulaSeg(s)
    # s.format()
    # print(s.text)
