#!/usr/bin/env python3
"""
Simple CLI for Qwen-powered Query Agent (No rich dependency)
"""

import sys
import argparse
import json
import time
from typing import Optional, List, Dict, Any

from .intelligent_agent import IntelligentQueryAgent
from .schemas import SchemaManager


class SimpleQwenCLI:
    """Simple CLI without rich dependency"""
    
    def __init__(self, 
                 use_qwen: bool = True,
                 llm_type: str = "ollama",
                 model: str = "qwen3:14b",
                 base_url: str = None):
        self.agent: Optional[IntelligentQueryAgent] = None
        self.use_qwen = use_qwen
        self.llm_type = llm_type
        self.model = model
        self.base_url = base_url
    
    def print_header(self):
        """Print application header"""
        print("=" * 60)
        print("        QWEN QUERY AGENT v1.0 - Simple CLI")
        print("     Natural Language → SQL with Qwen3:14B")
        print("=" * 60)
        
        qwen_status = f"✓ QWEN ENABLED ({self.model})" if self.use_qwen else "⚡ RULES-BASED"
        print(f"\nMode: {qwen_status}")
        print("Type 'help' for commands or just start typing your query!\n")
    
    def print_help(self):
        """Print help information"""
        print("\n" + "=" * 60)
        print("HELP & COMMANDS")
        print("=" * 60)
        print("\n🎯 QUICK START:")
        print("Just type your query in natural language!")
        print("Examples:")
        print("  • 'get all active users'")
        print("  • 'show orders from yesterday'")
        print("  • 'find expensive products in electronics category'")
        
        print("\n📋 COMMANDS:")
        print("help          - Show this help")
        print("schema        - Show database schema")
        print("tables        - List all tables")
        print("examples      - Show more examples")
        print("mode          - Toggle Qwen/Rules mode")
        print("test          - Test Qwen connection")
        print("clear         - Clear screen")
        print("exit          - Exit application")
        
        print(f"\n⚙️ CURRENT SETTINGS:")
        print(f"• Model: {self.model}")
        print(f"• LLM Type: {self.llm_type}")
        print(f"• Qwen Enabled: {'Yes' if self.use_qwen else 'No'}")
        print("=" * 60)
    
    def print_examples(self):
        """Print example queries"""
        print("\n" + "=" * 60)
        print("EXAMPLE QUERIES FOR QWEN")
        print("=" * 60)
        
        examples = [
            "Get all users who registered this month",
            "Show me the top 10 most expensive products",
            "Find all pending orders with total over $100",
            "Count how many products are in each category",
            "Get user details along with their order history",
            "What are the average ratings for electronics products?",
            "Find users who haven't placed any orders",
            "Show products that are out of stock",
            "Get daily sales for the last 7 days",
            "Which users have the most orders?"
        ]
        
        for i, example in enumerate(examples, 1):
            print(f"{i:2}. {example}")
        
        print("\n🤖 Qwen can handle:")
        print("• Complex JOIN operations")
        print("• Nested subqueries")
        print("• Date/time functions")
        print("• Aggregate functions")
        print("• Window functions")
        print("• Complex WHERE conditions")
        print("• CTEs (Common Table Expressions)")
        print("=" * 60)
    
    def initialize_agent(self, schema_name: str = "test"):
        """Initialize the Qwen-powered agent"""
        print(f"\nInitializing {'Qwen' if self.use_qwen else 'rules-based'} agent...")
        
        try:
            self.agent = IntelligentQueryAgent(
                schema_name=schema_name,
                use_local_llm=self.use_qwen,
                llm_type=self.llm_type,
                model=self.model,
                base_url=self.base_url
            )
            
            print(f"✓ Agent ready! Schema: {schema_name}")
            
            if self.use_qwen:
                test_result = self.agent.test_qwen_connection()
                if test_result.get("connected"):
                    print(f"✓ Qwen connection test successful")
                else:
                    print(f"⚠ Qwen connection issue: {test_result.get('message', 'Unknown')}")
            
            return True
            
        except Exception as e:
            print(f"✗ Failed to initialize agent: {e}")
            return False
    
    def test_qwen_connection(self):
        """Test Qwen LLM connection"""
        if not self.agent:
            print("⚠ Agent not initialized")
            return
        
        print("\nTesting Qwen connection...")
        result = self.agent.test_qwen_connection()
        
        if result.get("connected"):
            print("=" * 60)
            print("🤖 QWEN CONNECTION TEST")
            print("=" * 60)
            print(f"Status: ✓ Connected")
            print(f"Model: {result.get('model', 'Unknown')}")
            print(f"Response: {result.get('response', 'No response')}")
            print(f"Message: {result.get('message', '')}")
            print("=" * 60)
        else:
            print("=" * 60)
            print("🤖 QWEN CONNECTION TEST")
            print("=" * 60)
            print(f"Status: ✗ Not Connected")
            print(f"Error: {result.get('error', 'Unknown error')}")
            print(f"Message: {result.get('message', '')}")
            print("\nTROUBLESHOOTING:")
            print(f"1. Make sure Ollama is running: ollama serve")
            print(f"2. Pull the model: ollama pull {self.model}")
            print(f"3. Check if {self.llm_type} server is accessible")
            print("=" * 60)
    
    def show_schema(self):
        """Show database schema information"""
        if not self.agent:
            print("⚠ Agent not initialized")
            return
        
        info = self.agent.get_schema_info()
        
        print("\n" + "=" * 60)
        print("SCHEMA OVERVIEW")
        print("=" * 60)
        print(f"Schema: {info['name']}")
        print(f"Tables: {len(info['tables'])}")
        print(f"Qwen Enabled: {'Yes' if info['qwen_enabled'] else 'No'}")
        
        print("\n📋 TABLES IN SCHEMA:")
        for table in info['tables']:
            print(f"  • {table}")
        print("=" * 60)
    
    def process_query(self, prompt: str):
        """Process a natural language query"""
        if not self.agent:
            print("Initializing agent...")
            if not self.initialize_agent():
                return
        
        print(f"\nProcessing: '{prompt}'")
        print("." * 40)
        
        start_time = time.time()
        
        if self.use_qwen:
            print("🤖 Qwen is thinking...", end="", flush=True)
            sys.stdout.flush()
        
        result = self.agent.extract_query(prompt)
        processing_time = time.time() - start_time
        
        if self.use_qwen:
            print(" Done!")
        
        self._display_result(result, processing_time)
    
    def _display_result(self, result: Dict[str, Any], processing_time: float):
        """Display query result"""
        print("\n" + "=" * 60)
        print("QUERY RESULT")
        print("=" * 60)
        
        if not result.get("success"):
            print(f"❌ ERROR: {result.get('error', 'Unknown error')}")
            print(f"\nGenerated SQL:\n{result.get('sql_query', '')}")
            return
        
        metadata = result.get("metadata", {})
        
        print(f"Prompt: {result.get('user_prompt', '')}")
        print(f"Time: {processing_time:.2f}s")
        print(f"Model: {metadata.get('model', 'rule-based')}")
        print(f"Schema: {metadata.get('schema_name', 'unknown')}")
        
        print("\n" + "-" * 60)
        print("GENERATED SQL:")
        print("-" * 60)
        print(result.get("sql_query", ""))
        
        print("\n" + "-" * 60)
        print("ANALYSIS:")
        print("-" * 60)
        
        analysis = result.get("analysis", {})
        
        if analysis.get("intent"):
            print(f"Intent: {analysis.get('intent')}")
        
        print(f"Operation: {analysis.get('operation', 'SELECT')}")
        
        tables = analysis.get("tables", [])
        if tables:
            print(f"Tables: {', '.join(tables)}")
        
        columns = analysis.get("columns", [])
        if columns:
            col_display = columns[:5]
            col_str = ', '.join(col_display)
            if len(columns) > 5:
                col_str += f" (+{len(columns)-5} more)"
            print(f"Columns: {col_str}")
        
        conditions = analysis.get("conditions", [])
        if conditions:
            print(f"Conditions: {len(conditions)} condition(s)")
            for i, cond in enumerate(conditions[:3], 1):
                col = cond.get("column", "")
                op = cond.get("operator", "")
                val = cond.get("value", "")
                print(f"  {i}. {col} {op} {val}")
            if len(conditions) > 3:
                print(f"  ... and {len(conditions)-3} more")
        
        joins = analysis.get("joins", [])
        if joins:
            print(f"Joins: {len(joins)} join(s)")
        
        aggregates = analysis.get("aggregates", [])
        if aggregates:
            print(f"Aggregates: {len(aggregates)} function(s)")
            for agg in aggregates:
                func = agg.get("function", "")
                col = agg.get("column", "")
                print(f"  • {func}({col})")
        
        # Show reasoning if available
        reasoning = analysis.get("reasoning", "")
        if reasoning:
            print(f"\nReasoning: {reasoning[:200]}...")
            if len(reasoning) > 200:
                print(f"  ({len(reasoning)} characters total)")
        
        # Confidence
        confidence = analysis.get("confidence", 0)
        conf_star = "★" * int(confidence * 5) + "☆" * (5 - int(confidence * 5))
        print(f"\nConfidence: {conf_star} ({confidence:.1%})")
        
        # Validation
        validation = result.get("validation", {})
        if validation.get("is_valid"):
            print("✓ SQL is valid and matches schema")
        else:
            print("⚠ SQL may need manual verification")
        
        print("=" * 60)
    
    def toggle_mode(self):
        """Toggle between Qwen and rules mode"""
        self.use_qwen = not self.use_qwen
        
        if self.use_qwen:
            print(f"\n✓ Switched to Qwen mode ({self.model})")
        else:
            print(f"\n⚡ Switched to rules-based mode")
        
        # Reinitialize agent if it exists
        if self.agent:
            schema_name = self.agent.schema_name
            self.initialize_agent(schema_name)
    
    def interactive_mode(self):
        """Run interactive CLI mode"""
        self.print_header()
        
        # Initialize agent
        if not self.initialize_agent():
            print("Failed to initialize. Exiting.")
            return
        
        # Main loop
        while True:
            try:
                # Get user input
                user_input = input("\n>> ").strip()
                
                if not user_input:
                    continue
                
                # Check for commands
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\nGoodbye! 👋")
                    break
                
                elif user_input.lower() in ['help', '?']:
                    self.print_help()
                
                elif user_input.lower() == 'clear':
                    import os
                    os.system('cls' if os.name == 'nt' else 'clear')
                    self.print_header()
                
                elif user_input.lower() == 'schema':
                    self.show_schema()
                
                elif user_input.lower() == 'tables':
                    if self.agent:
                        info = self.agent.get_schema_info()
                        print("\nAvailable tables:")
                        for table in info['tables']:
                            print(f"  • {table}")
                
                elif user_input.lower() in ['examples', 'example']:
                    self.print_examples()
                
                elif user_input.lower() == 'mode':
                    self.toggle_mode()
                
                elif user_input.lower() == 'test':
                    self.test_qwen_connection()
                
                else:
                    # Treat as query
                    self.process_query(user_input)
                    
            except KeyboardInterrupt:
                print("\n\nInterrupted. Type 'exit' to quit.")
            except EOFError:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
    
    def run_single_query(self, prompt: str):
        """Run a single query and exit"""
        if not self.initialize_agent():
            return
        
        print(f"\nProcessing: {prompt}")
        self.process_query(prompt)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Qwen-powered SQL Query Agent (Simple)")
    parser.add_argument("query", nargs="?", help="Natural language query to process")
    parser.add_argument("--no-qwen", action="store_true", help="Disable Qwen LLM mode")
    parser.add_argument("--llm-type", default="ollama", choices=["ollama", "vllm", "litellm"], 
                       help="LLM server type")
    parser.add_argument("--model", default="qwen3:14b", help="Model name")
    parser.add_argument("--base-url", help="Base URL for LLM server")
    parser.add_argument("--schema", default="test", help="Schema to use")
    parser.add_argument("--examples", action="store_true", help="Show examples")
    parser.add_argument("--test", action="store_true", help="Test Qwen connection")
    
    args = parser.parse_args()
    
    cli = SimpleQwenCLI(
        use_qwen=not args.no_qwen,
        llm_type=args.llm_type,
        model=args.model,
        base_url=args.base_url
    )
    
    if args.test:
        cli.initialize_agent(args.schema)
        cli.test_qwen_connection()
    elif args.examples:
        cli.print_examples()
    elif args.query:
        cli.run_single_query(args.query)
    else:
        cli.interactive_mode()


if __name__ == "__main__":
    main()