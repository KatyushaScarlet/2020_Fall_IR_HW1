


class WARCRecord:
    warc_version = ""
    warc_header = {}
    offset_seek = 0
    content_length = 0
    content = ""

    def __str__(self):
        return "Offset: " + str(self.offset_seek) + "\nWARC Version: " + self.warc_version + "\nWARC Header: " + str(
            self.warc_header) + "\nContent Length: " + str(self.content_length)