import xlwt
import os
from io import BytesIO
from datetime import datetime, date


class ExcelHelper:
    """
    header is the first line of the excel file,
    content is a list that contains each line's elements.
    """

    def __init__(self, header, content, table_name="infomation"):
        self.table_name = table_name
        self.wb = xlwt.Workbook()
        self.fp = BytesIO()
        self.ws = self.wb.add_sheet(table_name)
        self.current_line = self.cl = 0
        self.fill_header(header)
        self.fill_content(content)

    def fill_header(self, header):
        for i in range(len(header)):
            self.ws.write(self.cl, i, header[i])
        self.cl += 1

    def fill_content(self, content):
        for c in content:
            for i, v in enumerate(c):
                self.ws.write(self.cl, i, v)
            self.cl += 1

    def to_file(self, name, location="."):
        self.wb.save(os.path.join(location, name))

    def to_bytes(self):
        self.wb.save(self.fp)
        self.fp.seek(0)
        return self.fp.getvalue()

    def __enter__(self):
        return self

    def __exit__(self, type, value, trace):
        self.fp.close()


def start_end(d):
    start = datetime(year=d.year, month=d.month, day=d.day, hour=8)
    end = datetime(year=d.year, month=d.month, day=d.day, hour=22)
    return start, end
