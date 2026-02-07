"""
Intelligent SQL Query Agent with Qwen3:14B support
"""

from typing import Dict, Any, Generator
from dataclasses import asdict
from datetime import datetime

from .schemas import SchemaManager
from .utils.logger import setup_logger
from .utils.llm_handler import Qwen3LLMHandler, QueryAnalysis


class IntelligentQueryAgent:
    """
    Intelligent agent that uses Qwen3:14B for SQL generation
    """
    
    def __init__(self, 
                 schema_name: str = "test",
                 use_local_llm: bool = True,
                 llm_type: str = "ollama",
                 model: str = "qwen3:14b",
                 base_url: str = None):
        """
        Initialize intelligent query agent with Qwen support
        
        Args:
            schema_name: Name of schema to use
            use_local_llm: Whether to use local LLM
            llm_type: Type of LLM (ollama, vllm, litellm)
            model: Model name (e.g., qwen2.5:14b)
            base_url: Base URL for LLM server
        """
        self.logger = setup_logger(__name__)
        self.use_local_llm = use_local_llm
        
        # Initialize schema
        self.schema_manager = SchemaManager()
        self.schema_name = schema_name
        self.schema_obj = self.schema_manager.get_schema(schema_name)
        
        if not self.schema_obj:
            available = self.schema_manager.list_schemas()
            raise ValueError(f"Schema '{schema_name}' not found. Available: {available}")
        
        self.schema = self.schema_obj.get_schema()
        
        # Initialize Qwen LLM handler
        self.qwen_handler = None
        if use_local_llm:
            try:
                self.qwen_handler = Qwen3LLMHandler(
                    llm_type=llm_type,
                    model=model,
                    base_url=base_url
                )
                
                if not self.qwen_handler.is_available():
                    self.logger.warning("Qwen LLM not available. Using rule-based fallback.")
                    self.use_local_llm = False
                else:
                    self.logger.info(f"✓ Qwen LLM initialized: {model} via {llm_type}")
                    
            except Exception as e:
                self.logger.error(f"Failed to initialize Qwen LLM: {e}")
                self.use_local_llm = False
        
        self.logger.info(f"Initialized agent with schema: {schema_name}")
        self.logger.info(f"Qwen LLM: {'Enabled' if self.use_local_llm else 'Disabled'}")
    
    def extract_query(self, user_prompt: str) -> Dict[str, Any]:
        """
        Extract SQL query from natural language prompt using Qwen
        
        Args:
            user_prompt: Natural language query
            
        Returns:
            Dictionary with query and analysis
        """
        self.logger.info(f"Processing: '{user_prompt}'")
        
        try:
            # Step 1: Analyze prompt with Qwen
            analysis = self._analyze_prompt(user_prompt)
            
            # Step 2: Generate SQL with Qwen
            sql_query = self._generate_sql(analysis)
            
            # Step 3: Validate against schema
            is_valid = self._validate_query(sql_query)
            
            # Step 4: Prepare response
            response = self._prepare_response(
                user_prompt=user_prompt,
                sql_query=sql_query,
                analysis=analysis,
                is_valid=is_valid
            )
            
            self.logger.info(f"Query generated successfully")
            return response
            
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return self._error_response(user_prompt, str(e))
    
    def extract_query_stream(self, user_prompt: str) -> Generator[Dict[str, Any], None, None]:
        """
        Stream SQL query generation
        
        Args:
            user_prompt: Natural language query
            
        Yields:
            Dictionary with partial results
        """
        self.logger.info(f"Stream processing: '{user_prompt}'")
        
        try:
            # Step 1: Analyze prompt
            analysis = self._analyze_prompt(user_prompt)
            
            # Yield analysis
            yield {
                "type": "analysis",
                "analysis": asdict(analysis)
            }
            
            # Step 2: Stream SQL generation
            sql_parts = []
            
            if self.use_local_llm and self.qwen_handler:
                # Stream from Qwen
                for chunk in self.qwen_handler.stream_generate_sql(analysis, self._get_schema_for_llm()):
                    sql_parts.append(chunk)
                    
                    yield {
                        "type": "sql_chunk",
                        "chunk": chunk,
                        "sql_so_far": "".join(sql_parts)
                    }
                
                sql_query = "".join(sql_parts)
            else:
                # Generate normally
                sql_query = self._generate_sql(analysis)
                yield {
                    "type": "sql_complete",
                    "sql_query": sql_query
                }
            
            # Step 3: Validate
            is_valid = self._validate_query(sql_query)
            
            # Step 4: Final response
            response = self._prepare_response(
                user_prompt=user_prompt,
                sql_query=sql_query,
                analysis=analysis,
                is_valid=is_valid
            )
            
            yield {
                "type": "complete",
                "response": response
            }
            
        except Exception as e:
            self.logger.error(f"Stream error: {e}")
            yield {
                "type": "error",
                "error": str(e)
            }
    
    def _analyze_prompt(self, prompt: str) -> QueryAnalysis:
        """Analyze user prompt using Qwen"""
        if self.use_local_llm and self.qwen_handler:
            # Use Qwen for analysis
            return self.qwen_handler.analyze_prompt(prompt, self._get_schema_for_llm())
        else:
            # Use enhanced rule-based analysis
            return self._rule_based_analysis(prompt)
    
    def _generate_sql(self, analysis: QueryAnalysis) -> str:
        """Generate SQL query using Qwen"""
        if self.use_local_llm and self.qwen_handler:
            # Use Qwen for SQL generation
            return self.qwen_handler.generate_sql(analysis, self._get_schema_for_llm())
        else:
            # Use rule-based SQL generation
            return self._rule_based_sql_generation(analysis)
    
    def _rule_based_analysis(self, prompt: str) -> QueryAnalysis:
        """Enhanced rule-based prompt analysis (fallback)"""
        # (Keep the existing rule-based analysis implementation)
        # ... [same as before] ...
    
    def _rule_based_sql_generation(self, analysis: QueryAnalysis) -> str:
        """Rule-based SQL generation (fallback)"""
        # (Keep the existing rule-based generation implementation)
        # ... [same as before] ...
    
    def _validate_query(self, sql: str) -> bool:
        """Validate SQL query"""
        # Basic validation
        sql_lower = sql.lower().strip()
        
        # Must contain SQL keyword
        if not any(keyword in sql_lower for keyword in ['select', 'insert', 'update', 'delete']):
            return False
        
        # SELECT must have FROM
        if 'select' in sql_lower and 'from' not in sql_lower:
            return False
        
        # Check if tables exist in schema
        all_tables = list(self.schema.get("tables", {}).keys())
        for table in all_tables:
            if table in sql_lower:
                return True
        
        # Allow queries with no explicit table if using asterisk (might be an error)
        if '*' in sql_lower:
            return True
        
        return False
    
    def _get_schema_for_llm(self) -> Dict[str, Any]:
        """Prepare schema for LLM consumption"""
        # Create simplified schema
        simplified = {
            "database": self.schema.get("database_name", "unknown"),
            "tables": {}
        }
        
        for table_name, table_info in self.schema.get("tables", {}).items():
            columns = []
            for col in table_info.get("columns", []):
                column_desc = {
                    "name": col.get("name"),
                    "type": col.get("type"),
                    "nullable": col.get("nullable", True)
                }
                
                # Add constraints
                if col.get("primary_key"):
                    column_desc["constraint"] = "PRIMARY KEY"
                elif col.get("foreign_key"):
                    column_desc["constraint"] = f"FOREIGN KEY REFERENCES {col['foreign_key']}"
                
                columns.append(column_desc)
            
            simplified["tables"][table_name] = {
                "columns": columns,
                "description": table_info.get("description", "")
            }
        
        # Add relationships
        simplified["relationships"] = self.schema.get("relationships", [])
        
        return simplified
    
    def _prepare_response(self, user_prompt: str, sql_query: str, 
                         analysis: QueryAnalysis, is_valid: bool) -> Dict[str, Any]:
        """Prepare response dictionary"""
        return {
            "success": True,
            "user_prompt": user_prompt,
            "sql_query": sql_query,
            "analysis": asdict(analysis),
            "validation": {
                "is_valid": is_valid,
                "schema_matched": is_valid,
                "tables_involved": analysis.tables
            },
            "metadata": {
                "schema_name": self.schema_name,
                "qwen_used": self.use_local_llm and self.qwen_handler and self.qwen_handler.is_available(),
                "model": getattr(self.qwen_handler, 'model', 'rule-based') if self.qwen_handler else 'rule-based',
                "timestamp": datetime.now().isoformat(),
                "tables_available": list(self.schema.get("tables", {}).keys())
            }
        }
    
    def _error_response(self, user_prompt: str, error: str) -> Dict[str, Any]:
        """Prepare error response"""
        return {
            "success": False,
            "user_prompt": user_prompt,
            "sql_query": f"-- Error: {error}",
            "error": error,
            "metadata": {
                "schema_name": self.schema_name,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get information about the current schema"""
        return {
            "name": self.schema_name,
            "tables": list(self.schema.get("tables", {}).keys()),
            "table_count": len(self.schema.get("tables", {})),
            "qwen_enabled": self.use_local_llm and self.qwen_handler and self.qwen_handler.is_available()
        }
    
    def test_qwen_connection(self) -> Dict[str, Any]:
        """Test Qwen LLM connection"""
        if not self.qwen_handler or not self.qwen_handler.is_available():
            return {
                "connected": False,
                "message": "Qwen LLM not available"
            }
        
        try:
            # Simple test query
            test_prompt = "Say 'Hello' in JSON format: {\"message\": \"Hello\"}"
            response = self.qwen_handler.llm.generate(test_prompt, max_tokens=20)
            
            return {
                "connected": True,
                "model": getattr(self.qwen_handler, 'model', 'unknown'),
                "response": response[:100] + "..." if len(response) > 100 else response,
                "message": "Qwen LLM is connected and responding"
            }
            
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "message": "Failed to connect to Qwen LLM"
            }