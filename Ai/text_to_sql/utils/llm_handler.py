"""
LLM Handler optimized for Qwen3:14b
"""
import json
import re
from typing import Dict, Any, List, Optional, Generator
from dataclasses import dataclass, asdict

from .local_llm import BaseLLM, LocalLLMFactory


@dataclass
class QueryAnalysis:
    """Analysis of user prompt for SQL generation optimized for Qwen3"""
    intent: str
    operation: str  # SELECT, INSERT, UPDATE, DELETE, etc.
    tables: List[str]
    columns: List[str]
    conditions: List[Dict[str, Any]]
    joins: List[Dict[str, Any]]
    order_by: Optional[List[Dict[str, Any]]] = None
    group_by: Optional[List[str]] = None
    limit: Optional[int] = None
    aggregates: Optional[List[Dict[str, Any]]] = None
    description: str = ""
    confidence: float = 0.0
    reasoning: str = ""
    suggested_sql_pattern: str = ""  # Added for Qwen3 guidance


class Qwen3LLMHandler:
    """Handler optimized for Qwen3:14b SQL generation"""
    
    def __init__(self, 
                 llm_type: str = "ollama",
                 model: str = "qwen3:14b",
                 base_url: str = None):
        """
        Initialize Qwen3 LLM handler
        
        Args:
            llm_type: Type of LLM (ollama, vllm, litellm)
            model: Model name (default: qwen3:14b)
            base_url: Base URL for the LLM server
        """
        self.llm: Optional[BaseLLM] = None
        self.llm_type = llm_type
        self.model = model
        
        print(f"\nInitializing Qwen3 handler...")
        print(f"  LLM Type: {llm_type}")
        print(f"  Model: {model}")
        
        # Create LLM instance
        kwargs = {"model": model}
        if base_url:
            kwargs["base_url"] = base_url
        
        try:
            self.llm = LocalLLMFactory.create_llm(llm_type, **kwargs)
            
            # Test connection
            if llm_type == "ollama" and hasattr(self.llm, 'test_connection'):
                if self.llm.test_connection():
                    print(f"  ✓ Connected to Ollama with {model}")
                else:
                    print(f"  ✗ Ollama connection failed")
                    self.llm = None
            else:
                # For other types, try a simple test
                test_response = self.llm.generate("test", max_tokens=5)
                if "not available" not in test_response.lower():
                    print(f"  ✓ Connected to {llm_type} with {model}")
                else:
                    print(f"  ✗ {llm_type} connection failed")
                    self.llm = None
                    
        except Exception as e:
            print(f"  ✗ Failed to initialize {llm_type}: {e}")
            self.llm = None
    
    def is_available(self) -> bool:
        """Check if Qwen3 LLM is available"""
        return self.llm is not None
    
    def analyze_prompt(self, prompt: str, schema_info: Dict[str, Any]) -> QueryAnalysis:
        """
        Analyze user prompt using Qwen3
        
        Args:
            prompt: User's natural language query
            schema_info: Database schema information
            
        Returns:
            QueryAnalysis object
        """
        if self.llm:
            return self._analyze_with_qwen3(prompt, schema_info)
        else:
            return self._analyze_with_rules(prompt, schema_info)
    
    def _analyze_with_qwen3(self, prompt: str, schema_info: Dict[str, Any]) -> QueryAnalysis:
        """Use Qwen3 to analyze prompt with optimized prompts"""
        try:
            # Prepare system prompt optimized for Qwen3's SQL capabilities
            system_prompt = f"""You are a SQL expert specialized in analyzing natural language queries. 
Your task is to extract SQL components from user queries.

DATABASE SCHEMA:
{json.dumps(schema_info, indent=2)}

TASK:
1. Understand the user's intent clearly
2. Identify the SQL operation (SELECT, INSERT, UPDATE, DELETE)
3. Determine required tables from the schema
4. Identify needed columns
5. Extract all conditions/filters (WHERE clause)
6. Identify JOINs if multiple tables needed
7. Detect ORDER BY requirements
8. Identify GROUP BY if aggregation needed
9. Extract LIMIT if specified
10. Identify aggregate functions (COUNT, SUM, AVG, MAX, MIN)

OUTPUT FORMAT (JSON ONLY):
{{
    "intent": "clear description",
    "operation": "SELECT|INSERT|UPDATE|DELETE",
    "tables": ["table1", "table2"],
    "columns": ["col1", "table.col2"],
    "conditions": [
        {{"column": "col_name", "operator": "=", "value": "value"}}
    ],
    "joins": [
        {{"type": "INNER|LEFT|RIGHT", "left_table": "t1", "left_column": "id", "right_table": "t2", "right_column": "t1_id"}}
    ],
    "order_by": [
        {{"column": "col_name", "direction": "ASC|DESC"}}
    ],
    "group_by": ["column1"],
    "limit": 10,
    "aggregates": [
        {{"function": "COUNT|SUM|AVG|MAX|MIN", "column": "col_name", "alias": "alias_name"}}
    ],
    "description": "brief explanation",
    "confidence": 0.95,
    "reasoning": "step-by-step reasoning",
    "suggested_sql_pattern": "SELECT pattern suggestion"
}}

RULES:
- Use ONLY tables/columns from the schema
- For string values, use single quotes: 'value'
- For conditions: use operators: =, !=, >, <, >=, <=, LIKE, IN, BETWEEN
- Return ONLY valid JSON, no additional text"""
            
            user_prompt = f"Query: {prompt}\n\nAnalyze this natural language query and extract SQL components."
            
            response = self.llm.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.1,
                max_tokens=2000
            )
            
            # Extract JSON from response
            json_str = self._extract_json(response)
            
            if json_str:
                try:
                    data = json.loads(json_str)
                    
                    # Validate and clean the data
                    data = self._validate_analysis(data, schema_info)
                    
                    return QueryAnalysis(**data)
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    print(f"Response: {response[:500]}")
                    
            # Fallback if JSON extraction fails
            return self._analyze_with_rules(prompt, schema_info)
                
        except Exception as e:
            print(f"Qwen3 analysis failed: {e}")
            return self._analyze_with_rules(prompt, schema_info)
    
    def generate_sql(self, analysis: QueryAnalysis, schema_info: Dict[str, Any]) -> str:
        """
        Generate SQL query from analysis using Qwen3
        
        Args:
            analysis: QueryAnalysis object
            schema_info: Database schema
            
        Returns:
            SQL query string
        """
        if self.llm:
            return self._generate_with_qwen3(analysis, schema_info)
        else:
            return self._generate_with_rules(analysis, schema_info)
    
    def _generate_with_qwen3(self, analysis: QueryAnalysis, schema_info: Dict[str, Any]) -> str:
        """Use Qwen3 to generate SQL with optimized prompts"""
        try:
            # Prepare detailed prompt for Qwen3
            system_prompt = f"""You are a SQL expert. Generate syntactically correct SQL queries.

DATABASE SCHEMA:
{json.dumps(schema_info, indent=2)}

QUERY REQUIREMENTS:
{json.dumps(asdict(analysis), indent=2)}

INSTRUCTIONS:
1. Generate valid SQL that works with the given schema
2. Use proper SQL syntax and formatting
3. Include all components from the analysis
4. Format for readability with appropriate indentation
5. Add comments for complex logic if helpful
6. Use table aliases for readability when needed
7. Ensure all column references are valid

OUTPUT: Generate ONLY the SQL query. No explanations, no markdown, just SQL."""
            
            user_prompt = "Generate the SQL query based on the requirements above."
            
            response = self.llm.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.1,
                max_tokens=2000
            )
            
            # Clean up the response
            sql = self._clean_sql_response(response)
            
            # Basic validation
            if not self._is_valid_sql(sql):
                print("SQL validation failed, using rule-based generation")
                return self._generate_with_rules(analysis, schema_info)
            
            return sql
            
        except Exception as e:
            print(f"Qwen3 SQL generation failed: {e}")
            return self._generate_with_rules(analysis, schema_info)
    
    def stream_generate_sql(self, analysis: QueryAnalysis, schema_info: Dict[str, Any]) -> Generator[str, None, None]:
        """Stream SQL generation using Qwen3"""
        if not self.llm:
            yield self._generate_with_rules(analysis, schema_info)
            return
        
        try:
            system_prompt = f"""You are a SQL expert. Generate a SQL query.

DATABASE SCHEMA:
{json.dumps(schema_info, indent=2)}

QUERY REQUIREMENTS:
{json.dumps(asdict(analysis), indent=2)}

Generate ONLY the SQL query, no other text."""
            
            user_prompt = "Generate the SQL query."
            
            full_response = ""
            for chunk in self.llm.stream_generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.1,
                max_tokens=2000
            ):
                full_response += chunk
                yield chunk
            
            # Post-process if needed
            sql = self._clean_sql_response(full_response)
            
        except Exception as e:
            print(f"Streaming SQL generation failed: {e}")
            yield self._generate_with_rules(analysis, schema_info)
    
    def _extract_json(self, text: str) -> Optional[str]:
        """Extract JSON from Qwen3 response"""
        # Try to find JSON block
        text = text.strip()
        
        # Remove markdown code blocks if present
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Find JSON object
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            
            # Try to fix common JSON issues
            try:
                # Try to parse directly
                json.loads(json_str)
                return json_str
            except json.JSONDecodeError:
                # Try common fixes
                # Fix 1: Remove trailing commas
                json_str = re.sub(r',\s*}', '}', json_str)
                json_str = re.sub(r',\s*]', ']', json_str)
                
                # Fix 2: Ensure property names are quoted
                json_str = re.sub(r'(\w+):', r'"\1":', json_str)
                
                # Fix 3: Handle single quotes in values
                json_str = re.sub(r":\s*'([^']*)'", r': "\1"', json_str)
                
                try:
                    json.loads(json_str)
                    return json_str
                except json.JSONDecodeError:
                    pass
        
        return None
    
    def _validate_analysis(self, analysis: Dict[str, Any], schema_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean analysis data from Qwen3"""
        # Ensure required fields
        required_fields = ["intent", "operation", "tables", "columns", "conditions", 
                          "joins", "description", "confidence"]
        
        for field in required_fields:
            if field not in analysis:
                if field == "tables":
                    analysis[field] = []
                elif field == "columns":
                    analysis[field] = []
                elif field == "conditions":
                    analysis[field] = []
                elif field == "joins":
                    analysis[field] = []
                elif field == "confidence":
                    analysis[field] = 0.7
                else:
                    analysis[field] = ""
        
        # Ensure lists are lists
        for field in ["tables", "columns", "conditions", "joins"]:
            if not isinstance(analysis.get(field), list):
                analysis[field] = []
        
        # Validate tables exist in schema
        schema_tables = schema_info.get("tables", {}).keys()
        valid_tables = []
        
        for table in analysis["tables"]:
            if table in schema_tables:
                valid_tables.append(table)
            else:
                # Try case-insensitive match
                for schema_table in schema_tables:
                    if table.lower() == schema_table.lower():
                        valid_tables.append(schema_table)
                        break
        
        analysis["tables"] = valid_tables
        
        # If no valid tables, use first table from schema
        if not valid_tables and schema_tables:
            analysis["tables"] = [list(schema_tables)[0]]
        
        return analysis
    
    def _clean_sql_response(self, response: str) -> str:
        """Clean SQL response from Qwen3"""
        # Remove markdown code blocks
        sql = re.sub(r'```sql\s*', '', response)
        sql = re.sub(r'```\s*', '', sql)
        
        # Remove leading/trailing whitespace
        sql = sql.strip()
        
        # Remove any non-SQL text before the SQL
        lines = sql.split('\n')
        sql_lines = []
        in_sql = False
        
        for line in lines:
            line_stripped = line.strip()
            line_lower = line_stripped.lower()
            
            # Check if this line starts SQL
            if any(line_lower.startswith(keyword) for keyword in 
                  ['select', 'insert', 'update', 'delete', 'with']):
                in_sql = True
            
            if in_sql:
                sql_lines.append(line)
            
            # Stop if we see end of SQL
            if line_stripped.endswith(';'):
                break
        
        sql = '\n'.join(sql_lines).strip()
        
        # Ensure semicolon at end
        if not sql.endswith(';'):
            sql += ';'
        
        return sql
    
    def _is_valid_sql(self, sql: str) -> bool:
        """Basic SQL validation"""
        sql_lower = sql.lower()
        
        # Must contain SQL keyword
        if not any(keyword in sql_lower for keyword in ['select', 'insert', 'update', 'delete', 'with']):
            return False
        
        # SELECT must have FROM (unless it's a CTE)
        if 'select' in sql_lower and 'from' not in sql_lower and 'with' not in sql_lower:
            return False
        
        # Should end with semicolon
        if not sql.strip().endswith(';'):
            return False
        
        return True
    
    def _analyze_with_rules(self, prompt: str, schema_info: Dict[str, Any]) -> QueryAnalysis:
        """Fallback rule-based analysis when Qwen3 is unavailable"""
        prompt_lower = prompt.lower()
        
        # Determine operation
        operation = "SELECT"
        if any(word in prompt_lower for word in ['insert', 'add', 'create']):
            operation = "INSERT"
        elif any(word in prompt_lower for word in ['update', 'modify']):
            operation = "UPDATE"
        elif any(word in prompt_lower for word in ['delete', 'remove']):
            operation = "DELETE"
        
        # Extract tables
        tables = []
        schema_tables = list(schema_info.get("tables", {}).keys())
        
        for table in schema_tables:
            if table in prompt_lower:
                tables.append(table)
            elif table[:-1] in prompt_lower and table.endswith('s'):
                tables.append(table)
        
        if not tables and schema_tables:
            tables.append(schema_tables[0])
        
        # Simple intent extraction
        intent = f"Query: {prompt}"
        if "active" in prompt_lower:
            intent = "Get active records"
        elif "count" in prompt_lower or "how many" in prompt_lower:
            intent = "Count records"
        elif "total" in prompt_lower or "sum" in prompt_lower:
            intent = "Calculate total"
        
        return QueryAnalysis(
            intent=intent,
            operation=operation,
            tables=tables,
            columns=["*"],
            conditions=[],
            joins=[],
            description="Rule-based analysis (Qwen3 not available)",
            confidence=0.5,
            reasoning="Using rule-based fallback",
            suggested_sql_pattern="SELECT * FROM {table}"
        )
    
    def _generate_with_rules(self, analysis: QueryAnalysis, schema_info: Dict[str, Any]) -> str:
        """Fallback rule-based SQL generation"""
        if analysis.operation == "SELECT":
            # Simple SELECT generation
            tables = analysis.tables
            if not tables:
                tables = list(schema_info.get("tables", {}).keys())[:1]
            
            table_str = tables[0]
            
            # Build columns
            columns = analysis.columns
            if not columns or columns == ["*"]:
                column_str = "*"
            else:
                column_str = ", ".join(columns[:5])  # Limit to 5 columns
            
            # Start building query
            query = f"SELECT {column_str} FROM {table_str}"
            
            # Add WHERE clause if conditions exist
            if analysis.conditions:
                conditions = []
                for cond in analysis.conditions[:3]:  # Limit to 3 conditions
                    col = cond.get("column", "")
                    op = cond.get("operator", "=")
                    val = cond.get("value", "")
                    conditions.append(f"{col} {op} {val}")
                
                if conditions:
                    query += f" WHERE {' AND '.join(conditions)}"
            
            # Add ORDER BY
            if analysis.order_by:
                orders = []
                for order in analysis.order_by:
                    col = order.get("column", "")
                    dir = order.get("direction", "ASC")
                    orders.append(f"{col} {dir}")
                
                if orders:
                    query += f" ORDER BY {', '.join(orders)}"
            
            # Add LIMIT
            if analysis.limit:
                query += f" LIMIT {analysis.limit}"
            
            return query + ";"
        
        else:
            # For non-SELECT operations, return a template
            return f"-- {analysis.operation} query for: {analysis.intent}"