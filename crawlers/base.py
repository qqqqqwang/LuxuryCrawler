from abc import ABC, abstractmethod
from typing import List, Dict

class Crawler(ABC):
    @abstractmethod
    def get_new_items(self) -> List[Dict]:
        """
        Returns a list of dictionaries with keys:
        - id: str (unique identifier)
        - title: str
        - price: str
        - link: str
        - source: str (Scanner name)
        """
        pass
