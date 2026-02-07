from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseSchema(ABC):
    """Abstract base class for all database schemas"""
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Return the schema definition"""
        pass
    
    @abstractmethod
    def get_table_names(self) -> list:
        """Return list of table names"""
        pass
    
    @abstractmethod
    def validate_query(self, query: str) -> bool:
        """Validate if query matches schema"""
        pass