from abc import ABC
from io import StringIO
from html.parser import HTMLParser


class MLStripper(HTMLParser, ABC):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_html_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


class TagParser(HTMLParser, ABC):
    def __init__(self):
        super(TagParser, self).__init__()
        self.segments = []

    def handle_starttag(self, tag, attrs):
        self.segments.append(("tag", tag))

    def handle_endtag(self, tag):
        self.segments.append(("tag", tag))

    def handle_data(self, data):
        self.segments.append(("data", data))

    def handle_startendtag(self, tag, attrs):
        self.segments.append(("tag", tag))

    def handle_comment(self, data):
        self.segments.append(("comment", data))


def seek_html_tag(text: str):
    parser = TagParser()
    segments = parser.segments
    for index, c in enumerate(text):
        parser.feed(c)
        if not segments:
            continue
        return None if segments[0][0] == 'data' else text[:index + 1]

    return None


import re

_ruby_pattern = re.compile(r"(?:\\ruby|☃)([\u4e00-\u9fa5·]+)\(([^)]+)\)")


def conv_to_ruby(line):
    return _ruby_pattern.sub(r'<ruby>\1<rt>\2</rt></ruby>', line)


if __name__ == '__main__':
    # s = '<span style="border-bottom:2px red double"> ok </span>'
    s = '<img src="https://pic1.zhimg.com/80/0799b3d6e5e92245ee937db3c26d1b80_1440w.png" alt="img" style="zoom:33%;" /> ok'
    # s = "</ok>"
    print(seek_html_tag(s))
