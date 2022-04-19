from typing import Iterable
from matcher import *


class Segment:
    def __init__(self, text):
        self.text = text

    def format(self):
        pass

    def __repr__(self):
        return f"{type(self).__name__}({self.text})"


formula_pattern = re.compile(r'^([$]*)(.*?)([$]*)$')


class FormulaSeg(Segment):
    def __init__(self, text):
        super().__init__(text)

    @classmethod
    def expect(cls, text):
        matcher = Matcher(text)
        if not matcher.match_pair('$'):
            return None
        return FormulaSeg(matcher.captured), matcher.remain

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

    @classmethod
    def expect(cls, text):
        matcher = Matcher(text)
        if not matcher.match_pair('`'):
            return None
        return CodeSeg(matcher.captured), matcher.remain


class TitleSeg(Segment):
    def __init__(self, text):
        super().__init__(text)


class TextSeg(Segment):
    def __init__(self, text):
        super().__init__(text)


class RefSeg(Segment):
    def __init__(self, text, caption=None, link=None):
        super().__init__(text)
        self.caption = caption
        self.link = link

    @classmethod
    def expect(cls, code):
        matcher = Matcher(code)
        if not matcher.match('['):
            return None

        m = matcher.match_util(']')
        if not m:
            return None
        caption = m[0][:-1]
        if not matcher.match('('):
            return None
        m = matcher.match_util(')')
        if not m:
            return None
        link = m[0][:-1]
        ref = RefSeg(matcher.captured, caption=caption, link=link)
        return ref, matcher.remain


class TagSeg(Segment):
    def __init__(self, text):
        super().__init__(text)

    @classmethod
    def expect(cls, text):
        from htmls import seek_html_tag
        if text[:1] != '<':
            return None
        seg = seek_html_tag(text)
        if not seg:
            return None
        return TagSeg(seg), text[len(seg):]


class ImgSeg(Segment):
    def __init__(self, text, caption=None, link=None):
        super().__init__(text)
        self.caption = caption
        self.link = link

    def to_html_tag_seg(self):
        return TagSeg(f'<img src="{self.link}" alt="{self.caption}" style="zoom:{100}%;"/>')

    @classmethod
    def expect(cls, code):
        matcher = Matcher(code)
        if not matcher.match('!'):
            return None
        ref, remain = RefSeg.expect(matcher.remain)
        ref = ImgSeg('!' + ref.text, caption=ref.caption, link=ref.link)
        return ref, remain


def parse_to_segs(line: str) -> Iterable[Segment]:
    text = []
    while line:
        rs = FormulaSeg.expect(line) or CodeSeg.expect(line) or ImgSeg.expect(line) or TagSeg.expect(
            line) or RefSeg.expect(line)
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


def join_segs(*segs):
    texts = [s.text.rstrip() if index == 0 else s.text.strip() for index, s in enumerate(segs)]
    return ''.join(texts)


def extract_bold_italic(code):
    if code[:1] != '*' or code[1:2] in ' *':
        return None

    # print(m)


if __name__ == '__main__':
    # s = "v\\$ok$f(x)$k`\\'o`k"
    # s = "  假设  $f(x)$  具有二阶连![img](http://a.b.c)续偏导数，若第$k$ 次迭代值为$x^{(k)}$, 则可将$f(x)$ 在$x^{(k)}$ 附近进行二阶<ok>泰勒展开:"
    # segs = list(parse_to_segs(s))
    # print(s)
    # for s in segs:
    #     print(s)
    s = "![img](http://a.b.c)续偏导数，若第$k$ "
    v, code = ImgSeg.expect(s)
    print(v)
    print(code)
    print(v.to_html_tag_seg())
    # print(v)
    # for s in segs:
    #     print(s)
    # print(join_segs(*segs))
    # s = "$ok,\\mathbb{E}   ,$"
    # s = FormulaSeg(s)
    # s.format()
    # print(s.text)

    # s = "*ok*"
    # print(extract_bold_italic(s))
    #
    # print(CodeSeg("code"))

    # s = "[asdf](https://blog.tsingjyujing.com/ml/recsys/ranknet) ok"
    s = "[随想： BPR Loss与Hinger Loss](https://zhuanlan.zhihu.com/p/166432329)"
    print(RefSeg.expect(s))
