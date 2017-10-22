# -*- coding: utf-8 -*-
from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
import io

def get_pdf_text(request_files):
    with io.BytesIO() as inf, io.StringIO() as outstring:
        request_files.save(inf)
        inf.seek(0)
        rscrmgr = PDFResourceManager(caching=True)
        laparams = LAParams()
        device = TextConverter(rscrmgr, outstring, laparams=laparams)
        process_pdf(rscrmgr, device, inf, set(), 0, caching=True, check_extractable=True)
        return outstring.getvalue()

