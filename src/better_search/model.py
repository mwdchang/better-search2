from pydantic import BaseModel
from typing import List, Dict


class DocumentExtractor(BaseModel):
    def extract(self, filepath: str, metadata: Dict):
        pass
