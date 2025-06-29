from abc import ABC, abstractmethod
from typing import List, Dict


class BaseScraper(ABC):
    @abstractmethod
    def fetch_questions(self, company: str, limit: int = 10) -> List[Dict[str, str]]:
        pass