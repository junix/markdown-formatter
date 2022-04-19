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
    def __init__(self, text: str, text_type: LineType = LineType.Text, has_new_line=False):
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
            seg = expect_code_end(line) or Line(line, LineType.Code)
        elif prev_type == LineType.Formulation:
            seg = expect_formula_end(line) or Line(line, LineType.Formulation)
        else:
            seg = expect_code(line) or \
                  expect_formula(line) or \
                  expect_title(line) or \
                  expect_blockquote(line) or \
                  expect_tag(line) or \
                  expect_html(line) or \
                  Line(text=line, text_type=LineType.Text)
        yield seg
        prev_type = seg.text_type


def expect_formula(line: str) -> Optional[Line]:
    if line.strip() == '$$':
        return Line(line, LineType.FormulationEnd)
    return None


def expect_formula_end(line: str) -> Optional[Line]:
    o = expect_formula(line)
    if o:
        o.text_type = LineType.FormulationEnd
    return o


_title_pattern = re.compile(r'^ *(#{1,6})\s*(.*)$')


def expect_title(line: str) -> Optional[Line]:
    match = _title_pattern.search(line)
    if not match:
        return None
    level = len(match.group(1))
    title = match.group(2).strip()
    suffix = ' ' + '#' * level
    if title.endswith(suffix):
        title = title[:-len(suffix)]
    # title = trim_internal_title_seq_no(title)
    l = Line(text='#' * level + ' ' + title, text_type=LineType.Title)
    setattr(l, 'level', level)
    setattr(l, 'title', title)
    return l


def expect_code(line: str) -> Optional[Line]:
    if _code_block.search(line) or _code_block_beg.search(line):
        return Line(line, LineType.Code)
    return None


def expect_code_end(line):
    if _code_block.search(line):
        return Line(line, LineType.CodeEnd)
    return None


def expect_blockquote(line: str) -> Optional[Line]:
    if not line.strip().startswith('>'):
        return None
    return Line(text=line, text_type=LineType.BlockQuote)


def expect_tag(line: str) -> Optional[Line]:
    tags = extract_tags(line)
    if not tags:
        return None
    l = Line(text=line, text_type=LineType.Tag)
    setattr(l, 'tags', tags)
    return l


def expect_html(line: str) -> Optional[Line]:
    if len(line.strip()) > 10 and len(strip_html_tags(line.strip())) < 2:
        return Line(text=line, text_type=LineType.Html)
    return None


_normalize_char = {
    '\t': ' ', '〈': '⟨', '〉': '⟩',
    '≤': '⩽', '≥': '⩾', "〞": "”", "〝": "“", '（': '(', '）': ')',
    '量': '量', '⾥': '里', '⾯': '面', '⽤': '用',
    '⼤': '大', '⽽': '而', '⼀': '一', '⽅': '方',
}


def regular_char(text):
    text = ''.join(_normalize_char.get(c, c) for c in text)
    return text


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
                line.remain = f"{'#' * level} {title}"
                continue

            seq_no = seq - 1
            if seq_no < len(level2seq[level]):
                line.remain = f"{'#' * level} {level2seq[level][seq_no]} {title.strip()}"
                continue

        line.remain = f"{'#' * level} {title.strip()}"


if __name__ == '__main__':
    # s = "![img](https://pic3.zhimg.com/80/v2-98fabeb9dd830221dc29b2f9e1ee1056_1440w.jpg)good"
    # r = parse_img(s)
    # print(r)
    # print(to_html_img(r["src"], r["alt"]))
    s = "##ok ## ##"
    print(expect_title(s))
