import json
import os
from typing import Dict, Optional
from .base_schema import BaseSchema
from .test_schema import TestSchema


class SchemaManager:
    """Manages multiple database schemas"""
    
    def __init__(self):
        self.schemas: Dict[str, BaseSchema] = {}
        self._load_builtin_schemas()
    
    def _load_builtin_schemas(self):
        """Load built-in schemas"""
        self.register_schema("test", TestSchema())
    
    def register_schema(self, name: str, schema: BaseSchema):
        """Register a new schema"""
        self.schemas[name] = schema
    
    def load_schema_from_file(self, name: str, filepath: str):
        """Load schema from JSON file"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                schema_data = json.load(f)
            
            class DynamicSchema(BaseSchema):
                def get_schema(self):
                    return schema_data
                
                def get_table_names(self):
                    return list(schema_data.get("tables", {}).keys())
                
                def validate_query(self, query: str) -> bool:
                    query_lower = query.lower()
                    tables = schema_data.get("tables", {})
                    for table in tables.keys():
                        if table in query_lower:
                            return True
                    return False
            
            self.register_schema(name, DynamicSchema())
    
    def get_schema(self, name: str) -> Optional[BaseSchema]:
        """Get schema by name"""
        return self.schemas.get(name)
    
    def list_schemas(self) -> list:
        """List all available schemas"""
        return list(self.schemas.keys())
    
    def get_schema_names(self) -> list:
        """Get list of schema names"""
        return list(self.schemas.keys())