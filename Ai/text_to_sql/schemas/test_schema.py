from typing import Dict, Any
from .base_schema import BaseSchema


class TestSchema(BaseSchema):
    """Test schema for e-commerce database"""
    
    def get_schema(self) -> Dict[str, Any]:
        """Return test schema for e-commerce database"""
        return {
            "database_name": "ecommerce_test",
            "tables": {
                "users": {
                    "columns": [
                        {"name": "id", "type": "INTEGER", "primary_key": True, "nullable": False},
                        {"name": "username", "type": "VARCHAR(50)", "nullable": False},
                        {"name": "email", "type": "VARCHAR(100)", "nullable": False},
                        {"name": "created_at", "type": "TIMESTAMP", "nullable": False},
                        {"name": "updated_at", "type": "TIMESTAMP", "nullable": True},
                        {"name": "status", "type": "VARCHAR(20)", "nullable": True, "default": "'active'"}
                    ],
                    "indexes": [
                        {"name": "idx_users_email", "columns": ["email"], "unique": True},
                        {"name": "idx_users_status", "columns": ["status"]}
                    ],
                    "description": "Stores user account information"
                },
                "orders": {
                    "columns": [
                        {"name": "id", "type": "INTEGER", "primary_key": True, "nullable": False},
                        {"name": "user_id", "type": "INTEGER", "foreign_key": "users.id", "nullable": False},
                        {"name": "product_id", "type": "INTEGER", "foreign_key": "products.id", "nullable": False},
                        {"name": "quantity", "type": "INTEGER", "nullable": False},
                        {"name": "unit_price", "type": "DECIMAL(10,2)", "nullable": False},
                        {"name": "total_price", "type": "DECIMAL(10,2)", "nullable": False},
                        {"name": "order_date", "type": "DATE", "nullable": False},
                        {"name": "status", "type": "VARCHAR(20)", "nullable": True, "default": "'pending'"},
                        {"name": "shipping_address", "type": "TEXT", "nullable": True}
                    ],
                    "indexes": [
                        {"name": "idx_orders_user_id", "columns": ["user_id"]},
                        {"name": "idx_orders_order_date", "columns": ["order_date"]},
                        {"name": "idx_orders_status", "columns": ["status"]}
                    ],
                    "description": "Stores customer orders"
                },
                "products": {
                    "columns": [
                        {"name": "id", "type": "INTEGER", "primary_key": True, "nullable": False},
                        {"name": "name", "type": "VARCHAR(100)", "nullable": False},
                        {"name": "description", "type": "TEXT", "nullable": True},
                        {"name": "category", "type": "VARCHAR(50)", "nullable": True},
                        {"name": "price", "type": "DECIMAL(10,2)", "nullable": False},
                        {"name": "stock_quantity", "type": "INTEGER", "nullable": False},
                        {"name": "created_at", "type": "TIMESTAMP", "nullable": False},
                        {"name": "is_active", "type": "BOOLEAN", "nullable": False, "default": "true"}
                    ],
                    "indexes": [
                        {"name": "idx_products_category", "columns": ["category"]},
                        {"name": "idx_products_price", "columns": ["price"]},
                        {"name": "idx_products_is_active", "columns": ["is_active"]}
                    ],
                    "description": "Stores product catalog information"
                },
                "categories": {
                    "columns": [
                        {"name": "id", "type": "INTEGER", "primary_key": True, "nullable": False},
                        {"name": "name", "type": "VARCHAR(50)", "nullable": False, "unique": True},
                        {"name": "description", "type": "TEXT", "nullable": True},
                        {"name": "parent_category_id", "type": "INTEGER", "foreign_key": "categories.id", "nullable": True}
                    ],
                    "description": "Product category hierarchy"
                },
                "reviews": {
                    "columns": [
                        {"name": "id", "type": "INTEGER", "primary_key": True, "nullable": False},
                        {"name": "product_id", "type": "INTEGER", "foreign_key": "products.id", "nullable": False},
                        {"name": "user_id", "type": "INTEGER", "foreign_key": "users.id", "nullable": False},
                        {"name": "rating", "type": "INTEGER", "nullable": False, "check": "rating BETWEEN 1 AND 5"},
                        {"name": "comment", "type": "TEXT", "nullable": True},
                        {"name": "created_at", "type": "TIMESTAMP", "nullable": False},
                        {"name": "is_verified", "type": "BOOLEAN", "nullable": False, "default": "false"}
                    ],
                    "indexes": [
                        {"name": "idx_reviews_product_id", "columns": ["product_id"]},
                        {"name": "idx_reviews_user_id", "columns": ["user_id"]},
                        {"name": "idx_reviews_rating", "columns": ["rating"]}
                    ],
                    "description": "Customer product reviews"
                }
            },
            "relationships": [
                {"from_table": "orders", "from_column": "user_id", "to_table": "users", "to_column": "id", "type": "many-to-one"},
                {"from_table": "orders", "from_column": "product_id", "to_table": "products", "to_column": "id", "type": "many-to-one"},
                {"from_table": "products", "from_column": "category", "to_table": "categories", "to_column": "name", "type": "many-to-one"},
                {"from_table": "reviews", "from_column": "product_id", "to_table": "products", "to_column": "id", "type": "many-to-one"},
                {"from_table": "reviews", "from_column": "user_id", "to_table": "users", "to_column": "id", "type": "many-to-one"},
                {"from_table": "categories", "from_column": "parent_category_id", "to_table": "categories", "to_column": "id", "type": "self-reference"}
            ],
            "metadata": {
                "version": "1.0",
                "description": "E-commerce test database schema",
                "created_date": "2024-01-01"
            }
        }
    
    def get_table_names(self) -> list:
        schema = self.get_schema()
        return list(schema["tables"].keys())
    
    def validate_query(self, query: str) -> bool:
        """Basic query validation against schema"""
        # This is a simplified validation
        schema = self.get_schema()
        tables = schema["tables"]
        
        # Check if mentioned tables exist
        query_lower = query.lower()
        for table in tables.keys():
            if table in query_lower:
                return True
        
        return False