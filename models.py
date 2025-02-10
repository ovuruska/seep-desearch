from enum import Enum
from typing import Self

from pydantic import BaseModel
class LlmModels(Enum):
    DEEPSEEK_R1 = "deepseek-ai/DeepSeek-R1"
    DEEPSEEK_R1_DISTILL_LLAMA_70B = "deepseek-ai/DeepSeek-R1-Distill-Llama-70B"
    DEEPSEEK_V3 = "deepseek-ai/DeepSeek-V3"

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str = ""
    content: str = ""

    @classmethod
    def from_google_result(cls, result: dict) -> Self:
        """
        Converts Google Custom Search API results into a list of SearchResult objects.
        """
        return cls(
            title=result.get("title", ""),
            url=result.get("link", ""),
            snippet=result.get("snippet", ""),
        )

    def set_content(self, content: str) -> Self:
        self.content = content
        return self