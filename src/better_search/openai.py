from openai import OpenAI
from typing import Dict, List

class AIClient:
    def __init__(self, base_url: str, token: str):
        self.client = OpenAI(
            base_url=base_url,
            api_key=token,
        )

    def get_embeddings(self, texts:List[str]):
        model_name = "openai/text-embedding-3-small"
        response = self.client.embeddings.create(
            input = texts,
            model=model_name,
        )
        return list(map(lambda x: x.embedding, response.data))

    
    def get_expansion(self, query_text: str):
        model_name = "gpt-4o-mini"
        prompt = f"Expand the following query with relevant keywords and alternative phrasings to improve information retrieval, provide up to 4 alternatives in a json-array: {query_text}"
        response = self.client.chat.completions.create(
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant with expertise in a large array of topics with expertize in information retrieval", 
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature = 1.0,
            top_p = 1.0,
            max_tokens = 1000,
            model = model_name
        )
        answer = response.choices[0].message.content
        return answer



    def get_completion(self, prompt: str):
        model_name = "gpt-4o-mini"
        response = self.client.chat.completions.create(
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant with expertise in a large array of topics with expertize in information retrieval", 
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature = 1.0,
            top_p = 1.0,
            max_tokens = 1000,
            model = model_name
        )
        answer = response.choices[0].message.content
        return answer


