from html.parser import HTMLParser


class MyHTMLParser(HTMLParser):

    def __init__(self):
        super(MyHTMLParser, self).__init__()
        self.segs = []

    def handle_starttag(self, tag, attrs):
        self.segs.append(("starttag", tag))
        # print("Encountered a start tag:", tag)

    def handle_endtag(self, tag):
        self.segs.append(("endtag", tag))
        # print("Encountered an end tag :", tag)

    def handle_data(self, data):
        self.segs.append(("data", data))
        # print("Encountered some data  :", data)

    def handle_startendtag(self, tag, attrs):
        self.segs.append(("startendtag", tag))
        # print("Encountered startendtag :", tag)

    def handle_comment(self, data):
        self.segs.append(("comment", data))
        # print("Encountered comment :", data)


# parser.feed('<html><head><title>Test</title></head>'
#             '<body><h1>Parse me!</h1><img src = "" />'
#             '<!-- comment --></body></html>')
s = """
在后面的课程中可以看到，这个表达式描述了一个含输入**x**和权重**w**的2维的"<ok/>"神经元，该神经元使用了sigmoid激活函数。但是现在只是看做是一个简单的输入为$x$和$w$，输出为一个数字的函数。这个函数是由多个门组成的。除了上文介绍的加法门，乘法门，取最大值门，还有下面这4种：
"""


def seek_tag(s):
    parser = MyHTMLParser()
    acc = ""
    for c in s:
        acc += c
        parser.feed(c)
        if parser.segs:
            if parser.segs[0][0] != 'data':
                return acc
            else:
                return None

    if not parser.segs or parser.segs[0][0] == 'data':
        return None
    return acc

print(seek_tag('</ok>good'))
