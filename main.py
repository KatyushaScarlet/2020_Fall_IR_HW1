import sys
import os
import time
import re
import multiprocessing
import random
import string
import gc
import shutil

from stemming.porter2 import stem

from warc.parser import Parser
from html.parser import HTMLParser
from indexing.partial_index import PartialIndex
from indexing.index import Index


class WarcHTMLParser(HTMLParser):
    lineCount = []
    index = PartialIndex()
    pre_offset = 0
    case_folding = False
    stopword_remove = False
    stemming = False
    position = 0
    stopwords = ['a', 'about', 'above', 'across', 'after', 'again', 'against', 'all', 'almost', 'alone', 'along',
                 'already',
                 'also', 'although', 'always', 'among', 'an', 'and', 'another', 'any', 'anybody', 'anyone', 'anything',
                 'anywhere', 'are', 'area', 'areas', 'around', 'as', 'ask', 'asked', 'asking', 'asks', 'at', 'away',
                 'b',
                 'back', 'backed', 'backing', 'backs', 'be', 'became', 'because', 'become', 'becomes', 'been', 'before',
                 'began', 'behind', 'being', 'beings', 'best', 'better', 'between', 'big', 'both', 'but', 'by', 'c',
                 'came',
                 'can', 'cannot', 'case', 'cases', 'certain', 'certainly', 'clear', 'clearly', 'come', 'could', 'd',
                 'did',
                 'differ', 'different', 'differently', 'do', 'does', 'done', 'down', 'down', 'downed', 'downing',
                 'downs',
                 'during', 'e', 'each', 'early', 'either', 'end', 'ended', 'ending', 'ends', 'enough', 'even', 'evenly',
                 'ever', 'every', 'everybody', 'everyone', 'everything', 'everywhere', 'f', 'face', 'faces', 'fact',
                 'facts',
                 'far', 'felt', 'few', 'find', 'finds', 'first', 'for', 'four', 'from', 'full', 'fully', 'further',
                 'furthered', 'furthering', 'furthers', 'g', 'gave', 'general', 'generally', 'get', 'gets', 'give',
                 'given',
                 'gives', 'go', 'going', 'good', 'goods', 'got', 'great', 'greater', 'greatest', 'group', 'grouped',
                 'grouping', 'groups', 'h', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'herself', 'high',
                 'high',
                 'high', 'higher', 'highest', 'him', 'himself', 'his', 'how', 'however', 'i', 'if', 'important', 'in',
                 'interest', 'interested', 'interesting', 'interests', 'into', 'is', 'it', 'its', 'itself', 'j', 'just',
                 'k',
                 'keep', 'keeps', 'kind', 'knew', 'know', 'known', 'knows', 'l', 'large', 'largely', 'last', 'later',
                 'latest', 'least', 'less', 'let', 'lets', 'like', 'likely', 'long', 'longer', 'longest', 'm', 'made',
                 'make', 'making', 'man', 'many', 'may', 'me', 'member', 'members', 'men', 'might', 'more', 'most',
                 'mostly',
                 'mr', 'mrs', 'much', 'must', 'my', 'myself', 'n', 'necessary', 'need', 'needed', 'needing', 'needs',
                 'never', 'new', 'new', 'newer', 'newest', 'next', 'no', 'nobody', 'non', 'noone', 'not', 'nothing',
                 'now',
                 'nowhere', 'number', 'numbers', 'o', 'of', 'off', 'often', 'old', 'older', 'oldest', 'on', 'once',
                 'one',
                 'only', 'open', 'opened', 'opening', 'opens', 'or', 'order', 'ordered', 'ordering', 'orders', 'other',
                 'others', 'our', 'out', 'over', 'p', 'part', 'parted', 'parting', 'parts', 'per', 'perhaps', 'place',
                 'places', 'point', 'pointed', 'pointing', 'points', 'possible', 'present', 'presented', 'presenting',
                 'presents', 'problem', 'problems', 'put', 'puts', 'q', 'quite', 'r', 'rather', 'really', 'right',
                 'right',
                 'room', 'rooms', 's', 'said', 'same', 'saw', 'say', 'says', 'second', 'seconds', 'see', 'seem',
                 'seemed',
                 'seeming', 'seems', 'sees', 'several', 'shall', 'she', 'should', 'show', 'showed', 'showing', 'shows',
                 'side', 'sides', 'since', 'small', 'smaller', 'smallest', 'so', 'some', 'somebody', 'someone',
                 'something',
                 'somewhere', 'state', 'states', 'still', 'still', 'such', 'sure', 't', 'take', 'taken', 'than', 'that',
                 'the', 'their', 'them', 'then', 'there', 'therefore', 'these', 'they', 'thing', 'things', 'think',
                 'thinks',
                 'this', 'those', 'though', 'thought', 'thoughts', 'three', 'through', 'thus', 'to', 'today',
                 'together',
                 'too', 'took', 'toward', 'turn', 'turned', 'turning', 'turns', 'two', 'u', 'under', 'until', 'up',
                 'upon',
                 'us', 'use', 'used', 'uses', 'v', 'very', 'w', 'want', 'wanted', 'wanting', 'wants', 'was', 'way',
                 'ways',
                 'we', 'well', 'wells', 'went', 'were', 'what', 'when', 'where', 'whether', 'which', 'while', 'who',
                 'whole',
                 'whose', 'why', 'will', 'with', 'within', 'without', 'work', 'worked', 'working', 'works', 'would',
                 'x',
                 'y', 'year', 'years', 'yet', 'you', 'young', 'younger', 'youngest', 'your', 'yours', 'z']

    def __init__(self):
        HTMLParser.__init__(self)
        self.index = PartialIndex()
        self.lineCount = []

    def calc_lineno_offset_to_offset(self, lineno, offset):
        return self.lineCount[lineno - 1] + offset

    def feed(self, data):
        lines = data.split('\n')
        c = 1
        self.lineCount.append(0)
        for line in lines:
            self.lineCount.append(self.lineCount[c - 1] + len(line) + 1)
            c += 1
        HTMLParser.feed(self, data)

    def handle_data(self, data):
        if self.lasttag not in ['script', 'style']:
            offset = self.calc_lineno_offset_to_offset(self.getpos()[0], self.getpos()[1]) + self.pre_offset
            word = re.compile('[A-Za-z]+')
            words = word.finditer(data)
            for w in words:
                if WarcHTMLParser.stopword_remove:
                    if w.group(0).lower() in self.stopwords:
                        continue
                if WarcHTMLParser.case_folding:
                    if WarcHTMLParser.stemming:
                        # self.index.push(stem(w.group(0).lower()), w.start() + offset)
                        self.index.push(stem(w.group(0).lower()), self.position)
                    else:
                        # self.index.push(w.group(0).lower(), w.start() + offset)
                        self.index.push(w.group(0).lower(), self.position)
                else:
                    if WarcHTMLParser.stemming:
                        self.index.push(stem(w.group(0)), w.start() + offset)
                        self.index.push(stem(w.group(0)), self.position)
                    else:
                        # self.index.push(w.group(0), w.start() + offset)
                        self.index.push(w.group(0), self.position)
                self.position += 1


def processing(_content: str, offset: int) -> PartialIndex:
    ph = WarcHTMLParser()
    ph.pre_offset = offset
    ph.feed(_content)
    return ph.index


def processing_async(idx: int, _content: str):
    c = re.compile("Content-Length: (\d+)\n\n")
    html_start = c.search(_content)
    html = _content[html_start.span()[1]:]
    return idx, processing(html, html_start.span()[1])


def get_temp_dir_name():
    """
    random dir name in 20 letters
    :return: String
    """
    random.seed()
    return ''.join(random.choice(string.ascii_letters) for x in range(20))


def start_parse(_parser: Parser) -> int:
    multiprocessing.freeze_support()
    pool = multiprocessing.Pool()
    count = 0
    result = []

    start_time = time.time()

    temp_dir_name = "temp"
    if os.path.exists(temp_dir_name):
        shutil.rmtree(temp_dir_name)
    os.mkdir(temp_dir_name)

    while True:
        d = _parser.fetch()
        count += 1
        if d is not None:
            result.append(pool.apply_async(processing_async, (count, d.content,)))

            if count % 1000 == 0:
                print("waiting...", int(count / 1000))
                pool.close()
                pool.join()
                for r in result:
                    cnt, idx = r.get()
                    idx.dump(temp_dir_name + "/" + str(cnt))
                pool = multiprocessing.Pool()
                result = []
        else:
            pool.close()
            pool.join()
            for r in result:
                cnt, idx = r.get()
                idx.dump(temp_dir_name + "/" + str(cnt))
            break
    print("----------------------------------------------------------")
    print("Analysis document:")
    end_time = time.time()
    print(end_time - start_time, "s")
    print("Average:", (end_time - start_time) * 1000 / count, "ms")
    print("Document process per second:", count / (end_time - start_time), "ps")
    print("----------------------------------------------------------")
    print("build full index ......")
    start_time = time.time()
    idx = Index()
    for i in range(1, count):
        if count % 500 == 0:
            gc.collect()
        idx.read_partial_index(i, PartialIndex.read(temp_dir_name + "/" + str(i)))
        os.remove(temp_dir_name + "/" + str(i))
    try:
        os.rmdir(temp_dir_name)
    except Exception:
        pass
    print("----------------------------------------------------------")
    print("Build full index:")
    end_time = time.time()
    print(end_time - start_time, "s")
    print("Average:", (end_time - start_time) * 1000 / count, "ms")
    print("DPS:", count / (end_time - start_time), "ps")
    print("----------------------------------------------------------")
    return count, idx


def main():
    input_file = sys.argv[1]

    if "-cf" in sys.argv:
        WarcHTMLParser.case_folding = True
    if "-sw" in sys.argv:
        WarcHTMLParser.stopword_remove = True
    if "-st" in sys.argv:
        WarcHTMLParser.stemming = True

    parser = Parser(input_file)
    # skip header record
    parser.fetch()

    starttime = time.time()

    print("Start......")
    count, index = start_parse(parser)

    print("dump index from memory to file")
    dump_start_time = time.time()
    index.dump(input_file + ".index")
    dump_end_time = time.time()
    print("----------------------------------------------------------")
    print("dump index:")
    print(dump_end_time - dump_start_time, "s")
    print("----------------------------------------------------------")
    print("finish")
    print("----------------------------------------------------------")
    print("Total time analysis:")
    print(time.time() - starttime, "s")
    print("Average", (time.time() - starttime) * 1000 / count, "ms")
    print("DPS", count / (time.time() - starttime), "ps")


if __name__ == "__main__":
    main()
