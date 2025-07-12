from docling.document_converter import DocumentConverter 
from typing import Dict
from .model import DocumentExtractor


class DoclingExtractor(DocumentExtractor):

    def generate_chunk(self, text: str, metadata: Dict):
        buffer = "== metadata =="
        buffer += "\n"
        for k in metadata:
            buffer += f"{k} : {metadata[k]}"
            buffer += "\n"
        buffer += "\n"
        buffer += "== text =="
        buffer += "\n"
        buffer += text
        return buffer

    def extract(self, filepath: str, metadata: Dict):
        """
        Simple extractor. Buffers up texts into chunks for embedding.
        Note the metadata derivation is not accurate if the chunk spans multiple pages, 
        for now we are ignoring this problem.
        """
        converter = DocumentConverter()
        result = converter.convert(filepath)
        result_dict = result.document.export_to_dict()

        has_title = False
        meta = {}

        formatted_texts = []
        buffer = ""
        for t in result_dict["texts"]:
            prov = t["prov"][0]
            page = prov["page_no"]
            label = t["label"]
            text = t["text"]

            meta["page"] = page

            if has_title == False and label == "section_header":
                has_title = True
                meta["title"] = text

            buffer += f"{text}\n"

            if len(buffer) > 1000 and label != "list_item":
                formatted_texts.append(self.generate_chunk(buffer, meta))
                buffer = ""

        if len(buffer) > 0:
            formatted_texts.append(self.generate_chunk(buffer, meta))

        return formatted_texts

 

if __name__ == "__main__":
    pdf_extractor = DoclingExtractor()
    texts = pdf_extractor.extract("/Users/dchang/health-messenger/pdfs/jmir-2022-8-e38015.pdf", None)
    for text in texts:
        print(text)
        print("===============")

