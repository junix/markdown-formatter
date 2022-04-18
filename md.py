import os
import re
from urllib.parse import unquote
from typing import Iterable
from itertools import takewhile, dropwhile
from collections import defaultdict
from enum import Enum
from seg import *
from conv import *
from htmls import strip_html_tags


class LineType(Enum):
    Title = 1
    Formulation = 2
    FormulationEnd = 3
    BlockQuote = 4
    Code = 5
    CodeEnd = 6
    Text = 7
    Html = 8
    Tag = 9
    Img = 10


class Line:
    def __init__(self, text, text_type=LineType.Text, has_new_line=False):
        self.text = text
        self.text_type = text_type
        self.has_new_line = has_new_line

    def raw_text(self):
        return self.text + '\n' if self.has_new_line else self.text

    def to_segments(self):
        if self.text_type == LineType.Title:
            return [TitleSeg(self.text)]
        if self.text_type in (LineType.Code, LineType.CodeEnd):
            return [CodeSeg(self.text)]
        if self.text_type in (LineType.Formulation, LineType.FormulationEnd):
            return [FormulaSeg(self.text)]
        if self.text_type in (LineType.Tag, LineType.Html, LineType.Img):
            return [TagSeg(self.text)]
        return list(parse_to_segs(self.text))

    def __repr__(self):
        return f"type={self.text_type}:{self.text}"


_code_block = re.compile(r'^ *```')
_code_block_beg = re.compile(r'^ *```(?:python|text|java|bash|shell|matlab)')

_tags_pattern = re.compile(r'^[>$]?\s*(?:tags|标签)[：:](.*)[$]?$')
_tags_delim = re.compile(r'[,，;；、]+')

_title_pattern = re.compile(r'^ *(#{1,6})\s+(.*)$')


def strip_md_tags(text):
    ...


def _is_block_formula_mark(line):
    return line.strip() == '$$'


def extract_tags(line):
    t = line.lower()
    if 'tags' not in t and '标签' not in t:
        return None
    t = strip_html_tags(t)
    t = re.sub(r'[*$}]', '', t).strip()
    t = re.sub(r'\\text{', '', t).strip()
    t = re.sub(r'\\texttt{', '', t).strip()
    m = _tags_pattern.search(t)
    if not m:
        return None

    tags = m.group(1).strip()
    return [t.strip().lower() for t in _tags_delim.split(tags)]


def parse_to_lines(text: str) -> Iterable[Line]:
    prev_type = LineType.Text

    lines = re.split(r'[\r\n]', regular_char(text))
    lines = '\n'.join([convert_to_latex_formula(x, False, False) for x in lines])
    lines = re.split(r'[\r\n]', lines)
    for line in lines:
        if prev_type == LineType.Code:
            if _code_block.search(line):
                yield Line(line, LineType.CodeEnd)
                prev_type = LineType.CodeEnd
            else:
                yield Line(line, LineType.Code)
        elif prev_type == LineType.Formulation:
            if line.strip() == '$$':
                yield Line(line, LineType.FormulationEnd)
                prev_type = LineType.FormulationEnd
            else:
                yield Line(line, LineType.Formulation)
        elif _code_block.search(line) or _code_block_beg.search(line):
            yield Line(line, LineType.Code)
            prev_type = LineType.Code
        elif line.strip() == '$$':
            yield Line(text=line, text_type=LineType.Formulation)
            prev_type = LineType.Formulation
        else:
            match = _title_pattern.search(line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                suffix = ' ' + '#' * level
                if title.endswith(suffix):
                    title = title[:-len(suffix)]
                # title = trim_internal_title_seq_no(title)
                l = Line(text='#' * level + ' ' + title, text_type=LineType.Title)
                setattr(l, 'level', level)
                setattr(l, 'title', title)
                yield l
                prev_type = LineType.Title
                continue

            if line.strip().startswith('>'):
                l = Line(text=line, text_type=LineType.BlockQuote)
                yield l
                prev_type = LineType.BlockQuote
                continue

            tags = extract_tags(line)
            if tags:
                l = Line(text=line, text_type=LineType.Tag)
                setattr(l, 'tags', tags)
                yield l
                prev_type = LineType.Tag
                continue

            if len(line.strip()) > 10 and len(strip_html_tags(line.strip())) < 2:
                l = Line(text=line, text_type=LineType.Html)
                yield l
                prev_type = LineType.Html
                continue

            l = Line(line, LineType.Text)
            yield l
            prev_type = LineType.Text


def parse_to_segments(text: str) -> Iterable[Line]:
    prev_type = LineType.Text

    lines = re.split(r'[\r\n]', regular_char(text))
    lines = '\n'.join([convert_to_latex_formula(x, False, False) for x in lines])
    lines = re.split(r'[\r\n]', lines)
    for line in lines:
        if prev_type == LineType.Code:
            if _code_block.search(line):
                yield Line(line, LineType.CodeEnd)
                prev_type = LineType.CodeEnd
            else:
                yield Line(line, LineType.Code)
        elif prev_type == LineType.Formulation:
            if line.strip() == '$$':
                yield Line(line, LineType.FormulationEnd)
                prev_type = LineType.FormulationEnd
            else:
                yield Line(line, LineType.Formulation)
        elif _code_block.search(line) or _code_block_beg.search(line):
            yield Line(line, LineType.Code)
            prev_type = LineType.Code
        elif line.strip() == '$$':
            yield Line(text=line, text_type=LineType.Formulation)
            prev_type = LineType.Formulation
        else:
            match = _title_pattern.search(line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                # title = trim_internal_title_seq_no(title)
                l = Line(text=line, text_type=LineType.Title)
                setattr(l, 'level', level)
                setattr(l, 'title', title)
                yield l
                prev_type = LineType.Title
                continue

            if line.strip().startswith('>'):
                l = Line(text=line, text_type=LineType.BlockQuote)
                yield l
                prev_type = LineType.BlockQuote
                continue

            tags = extract_tags(line)
            if tags:
                l = Line(text=line, text_type=LineType.Tag)
                setattr(l, 'tags', tags)
                yield l
                prev_type = LineType.Tag
                continue

            if len(line.strip()) > 10 and len(strip_html_tags(line.strip())) < 2:
                l = Line(text=line, text_type=LineType.Html)
                yield l
                prev_type = LineType.Html
                continue

            l = Line(line, LineType.Text)
            yield l
            prev_type = LineType.Text


def is_title(line):
    return _title_pattern.search(line)


_normalize_char = {
    '\t': ' ', '〈': '⟨', '〉': '⟩',
    '≤': '⩽', '≥': '⩾', "〞": "”", "〝": "“", '（': '(', '）': ')',
    '量': '量', '⾥': '里', '⾯': '面', '⽤': '用',
    '⼤': '大', '⽽': '而', '⼀': '一', '⽅': '方',
}


def regular_char(text):
    text = ''.join(_normalize_char.get(c, c) for c in text)
    return text


def zoom_img(line, ratio=33):
    acc = []
    while line:
        m = re.search(r"(.*?)!\[img]\((https://pic[0-9]\.zhimg\.com/80/v2-[a-z0-9]{4,40}_1440w\.jpg)\)", line)
        if not m:
            acc.append(line)
            break

        acc.append(m.group(1))
        acc.append(f'<img src="{m.group(2)}" alt="img" style="zoom:{ratio}%;" />\n\n')
        line = line[len(m.group(0)):]

    return "".join(acc)


def remove_zhihu_redirect_url(line):
    from urllib.parse import unquote
    p = r'(^.*]\()https://link.zhihu.com/\?target=([^)]+)(\).*)$'
    while True:
        m = re.search(p, line)
        if not m:
            return line
        line = m.group(1) + unquote(m.group(2)) + m.group(3)


def remove_space(text):
    text = re.sub(r'(?<=[\u3400-\u4DBF\u4E00-\u9FFF]) (?=[a-zA-Z0-9])', '', text)
    text = re.sub(r'(?<=[a-zA-Z0-9]) (?=[\u3400-\u4DBF\u4E00-\u9FFF])', '', text)
    text = re.sub(r'(?<=[\u3400-\u4DBF\u4E00-\u9FFF]) (?=[\u3400-\u4DBF\u4E00-\u9FFF])', '', text)
    text = re.sub(r'(?<=[，。()])\s+', '', text)
    text = re.sub(r' (?=[，。（）()])', '', text)
    return text


def regular_quote(text):
    text = re.sub(r'(?<=[\u3400-\u4DBF\u4E00-\u9FFF]),', r'，', text)
    # text = re.sub(rf'(?<=[$])(?=[\u4E00-\u9FFF])', r' ', text)
    # text = re.sub(rf'(?<=[\u4e00-\u9fff])(?=[$])', r' ', text)

    # 删除汉字之间的空格
    text = re.sub(rf'(?<=[\u4e00-\u9fa5，。]) (?=[\u4e00-\u9fa5，。])', r'', text)
    text = re.sub(r',(?=[\u4e00-\u9fa5])', r'，', text)
    text = re.sub(r'(?<=[\u4e00-\u9fa5]);', r'；', text)
    text = re.sub(r';(?=[\u4e00-\u9fa5])', r'；', text)
    text = re.sub(r'，\s+', r'，', text)
    text = re.sub(r'\$([A-Z])\$', r'\1', text)
    text = re.sub(r'- - ', r'\t- ', text)
    text = re.sub(r'^\\(\d)\. ', r'\1. ', text)

    return text


_internal_title_seq_no_pattern = re.compile(r'^([⓿❶-❿⓫-⓴①-⑳⓵-⓾ⓐ-ⓩ㊀-㊉]|\d(\.\d)+|(\d\.)+|[一二三四五六七八九十\d]+[、])')


def trim_internal_title_seq_no(text):
    while True:
        orig = text
        text = _internal_title_seq_no_pattern.sub('', text).strip()
        if orig == text:
            return text


_max_level = 6


def remark_title_seq_no(lines):
    level2seq = {
        2: '❶❷❸❹❺❻❼❽❾❿⓫⓬⓭⓮⓯⓰⓱⓲⓳⓴',
        3: '①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳',
        4: '⓵⓶⓷⓸⓹⓺⓻⓼⓽⓾',
        # 5: 'ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ',
        5: '㊀㊁㊂㊃㊄㊅㊆㊇㊈㊉',
    }
    leveled_seq_no = defaultdict(int)

    for line in lines:
        if line.text_type != LineType.Title:
            continue

        level = getattr(line, 'level', None)
        title = getattr(line, 'title', None)
        if not level or not title:
            continue

        level = int(level)
        leveled_seq_no[level] += 1
        for i in range(level + 1, _max_level + 1):
            leveled_seq_no[i] = 0

        if level in (2, 3, 4, 5):
            seq = leveled_seq_no[level]
            if title in ("参考文献", "参考", "前言", "继续阅读", "习题", "本章概要"):
                line.text = f"{'#' * level} {title}"
                continue

            seq_no = seq - 1
            if seq_no < len(level2seq[level]):
                line.text = f"{'#' * level} {level2seq[level][seq_no]} {title.strip()}"
                continue

        line.text = f"{'#' * level} {title.strip()}"


def expect_title(line):
    try:
        level, remain = expect('^#{1,6}', line)
        c0, remain = expect('[^#]', remain)
        while expect(f' {level}$', remain):
            remain = remain[:-len(level)-1]
        return level + c0 + remain, ""
    except:
        return None


if __name__ == '__main__':
    # s = "![img](https://pic3.zhimg.com/80/v2-98fabeb9dd830221dc29b2f9e1ee1056_1440w.jpg)good"
    # r = parse_img(s)
    # print(r)
    # print(to_html_img(r["src"], r["alt"]))
    s = "##ok ## ##"
    print(expect_title(s))
