import os
import gzip
from .record import WARCRecord


def get_file_size(_fn):
    return os.stat(_fn).st_size


class Parser:
    encoding = "ISO-8859-1"
    offset_seek = 0
    has_idx = False
    idx = []

    def __init__(self, input_file):
        self.warc_file = input_file
        self.warc_file_size = get_file_size(self.warc_file)

        if ".warc.gz" in input_file:
            self.f = gzip.open(self.warc_file, "rb")
        else:
            self.f = open(self.warc_file, "rb")


        idx_file_name = input_file + ".idx"
        if os.path.isfile(idx_file_name):
            self.has_idx = True
            idx_file_size = get_file_size(idx_file_name)
            idxf = gzip.open(idx_file_name)
            idxs = idxf.readlines()
            idxf.close()
            for idx in idxs:
                c = idx.decode(self.encoding)[:-1].split(' ')
                self.idx.append((c[0], int(c[1])))


    def seek(self, offset):
        self.f.seek(offset)

    def goto(self, num: int):
        if self.has_idx and (num > 0) and (num < len(self.idx)):
            self.seek(self.idx[num][1])

    def fetch(self):
        while True:
            self.offset_seek = self.f.tell()
            if self.f.tell() == self.warc_file_size:
                return None
            line = self.f.readline().decode(self.encoding)
            
            if line == "":
                return
            if line[0] == 'W':
                break
                
        warc_record = WARCRecord()
        warc_record.offset_seek = self.offset_seek
        warc_record.warc_version = line[:-1]
        while True:
            line = self.f.readline().decode(self.encoding)[:-1].split(":", 1)

            if line[0] == 'Content-Length':
                warc_record.content_length = int(line[1].strip())
                content = self.f.read(warc_record.content_length).decode(self.encoding)
                warc_record.content = content
                break
            else:
                warc_record.warc_header[line[0].strip()] = line[1].strip()
        return warc_record
