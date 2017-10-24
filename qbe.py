# -*- coding: utf-8 -*-
import io
from IPython import embed
import pdftotext
import docx

def _handle_upload(file_upload):
    with io.BytesIO() as tmp:
        file_upload.save(tmp)
        tmp.seek(0)
        print(file_upload.filename)
        if file_upload.content_type == "text/plain":
            return tmp.read().decode()
        elif file_upload.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return '\n'.join((p.text for p in docx.Document(tmp).paragraphs))
        elif file_upload.content_type == "application/pdf":
            return ''.join(pdftotext.PDF(tmp))


# def get_pdf_text(request_files):
#     with io.BytesIO() as inf, io.StringIO() as outstring:
#         request_files.save(inf)
#         inf.seek(0)
#         rscrmgr = PDFResourceManager(caching=True)
#         laparams = LAParams()
#         device = TextConverter(rscrmgr, outstring, laparams=laparams)
#         process_pdf(rscrmgr, device, inf, set(), 0, caching=True,
#                     check_extractable=True)
#         return outstring.getvalue()


def get_pdf_text_simple(request_files):
    return '\n\n'.join((_handle_upload(f) for f in request_files))
