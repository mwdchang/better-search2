import os
import copy
from docling.document_converter import DocumentConverter 
from typing import Dict
import hashlib


def hash_text(text: str):
    hash_object = hashlib.sha256(text.encode())
    hash_hex = hash_object.hexdigest()
    return str(hash_hex)


class DocumentExtractor:

    def generate_chunk(self, text: str, metadata: Dict):
        """
        Prepend a metadata section to a text chunk
        """
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
        _, extension = os.path.splitext(filepath)
        if extension.lower() == ".pdf":
            print("Extracting PDF...this may take a minute or two")
            return self.extract_pdf(filepath, metadata)
        else:
            print("Extracting text")
            return self.extract_plain(filepath, metadata)


    def extract_plain(self, filepath: str, metadata: Dict):
        lines = []
        with open(filepath, "r", encoding="utf-8") as file:
            lines = file.read().splitlines()

        result_chunks = []
        result_metadatas = []
        result_ids = []
        buffer = ""
        for line in lines:
            buffer += line

            if len(buffer) > 1000:
                text_chunk = self.generate_chunk(buffer, metadata)
                result_chunks.append(text_chunk)
                metadata["text"] = buffer
                result_metadatas.append(metadata)
                result_ids.append(hash_text(text_chunk))
                buffer = ""

        if len(buffer) > 0:
            text_chunk = self.generate_chunk(buffer, metadata)
            result_chunks.append(text_chunk)
            metadata["text"] = buffer
            result_metadatas.append(metadata)
            result_ids.append(hash_text(text_chunk))

        return result_chunks, result_metadatas, result_ids


    def extract_pdf(self, filepath: str, metadata: Dict):
        """
        Simple extractor. Buffers up texts into chunks for embedding.
        Note the metadata derivation is not accurate if the chunk spans multiple pages, 
        for now we are ignoring this problem.
        """
        converter = DocumentConverter()
        result = converter.convert(filepath)
        result_dict = result.document.export_to_dict()

        has_title = False
        meta = metadata

        result_chunks = []
        result_metadatas = []
        result_ids = []

        buffer = ""
        for t in result_dict["texts"]:
            prov = t["prov"][0]
            page = prov["page_no"]
            label = t["label"]
            text = t["text"]

            if "page" not in meta:
                meta["page"] = page

            if has_title == False and label == "section_header":
                has_title = True
                if "title" not in meta:
                    meta["title"] = text

            buffer += f"{text}\n"

            if len(buffer) > 1000 and label != "list_item":
                text_chunk = self.generate_chunk(buffer, meta)
                result_chunks.append(text_chunk)
                metadata["text"] = buffer
                result_metadatas.append(copy.deepcopy(meta))
                result_ids.append(hash_text(text_chunk))
                buffer = ""

        if len(buffer) > 0:
            text_chunk = self.generate_chunk(buffer, meta)
            result_chunks.append(text_chunk)
            metadata["text"] = buffer
            result_metadatas.append(copy.deepcopy(meta))
            result_ids.append(hash_text(text_chunk))

        return result_chunks, result_metadatas, result_ids


if __name__ == "__main__":
    extractor = DocumentExtractor()
    chunks, metadatas, chunk_ids = extractor.extract("/Users/dchang/workspace/better-search2/2406.02030v2.pdf", {})
    for metadata in metadatas:
        print(metadata)
        print("===============")

