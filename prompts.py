"""
Prompt Engineering and Reference Dataset Module.
Handles system instructions, few-shot examples, and auto-repair prompts.
"""

SYSTEM_INSTRUCTION = """You are an expert Python software engineer specializing in translating natural language feature requirements into clean, production-ready, executable Python code snippets.

Strict Guidelines:
1. Output ONLY executable Python code within a standard markdown code block: ```python ... ```.
2. Do NOT provide conversational fluff or intro/outro explanations.
3. Every snippet MUST include:
   - Necessary imports at the top.
   - A well-named function or class with PEP-484 type annotations and a clear docstring.
   - Comprehensive error handling (try/except) where appropriate.
   - A runnable demonstration block under `if __name__ == '__main__':` that prints output to test the function.
4. The generated code MUST be 100% syntactically valid and executable with standard Python 3.10+.
"""

# Curated reference pairs (Few-Shot dataset) as specified in requirements
FEW_SHOT_REFERENCES = [
    {
        "requirement": "Write a function to read a CSV file and return only records where age is greater than 25.",
        "code": '''import csv
from typing import List, Dict, Any

def filter_users_by_age(csv_filepath: str, min_age: int = 25) -> List[Dict[str, Any]]:
    """Reads a CSV file and filters rows where age exceeds min_age."""
    filtered_records: List[Dict[str, Any]] = []
    try:
        with open(csv_filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if int(row.get('age', 0)) > min_age:
                    filtered_records.append(row)
    except FileNotFoundError:
        print(f"Error: {csv_filepath} not found.")
    except Exception as e:
        print(f"Error processing CSV: {e}")
    return filtered_records

if __name__ == "__main__":
    # Example usage test
    print("Filter function initialized successfully.")
'''
    },
    {
        "requirement": "Create a utility to extract and validate all email addresses from an unstructured text string using regex.",
        "code": '''import re
from typing import List

def extract_valid_emails(text: str) -> List[str]:
    """Extracts valid email addresses from raw text using regular expressions."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}'
    if not text or not isinstance(text, str):
        return []
    return re.findall(email_pattern, text)

if __name__ == "__main__":
    sample = "Contact us at support@example.com or sales.dept@company.org."
    print("Extracted emails:", extract_valid_emails(sample))
'''
    },
    {
        "requirement": "Calculate summary statistics (mean, median, standard deviation) for a list of numeric values without external dependencies.",
        "code": '''import math
from typing import List, Dict, Union

def calculate_summary_stats(numbers: List[Union[int, float]]) -> Dict[str, float]:
    """Computes mean, median, and sample standard deviation for a list of numbers."""
    if not numbers:
        raise ValueError("List cannot be empty.")
    
    n = len(numbers)
    mean_val = sum(numbers) / n
    sorted_nums = sorted(numbers)
    
    if n % 2 == 1:
        median_val = float(sorted_nums[n // 2])
    else:
        median_val = (sorted_nums[(n // 2) - 1] + sorted_nums[n // 2]) / 2.0
        
    variance = sum((x - mean_val) ** 2 for x in numbers) / (n - 1) if n > 1 else 0.0
    std_dev = math.sqrt(variance)
    
    return {
        "count": float(n),
        "mean": round(mean_val, 4),
        "median": round(median_val, 4),
        "std_dev": round(std_dev, 4)
    }

if __name__ == "__main__":
    data = [12, 15, 23, 29, 34, 45, 50]
    print("Statistics:", calculate_summary_stats(data))
'''
    }
]

def build_prompt(requirement: str, include_examples: bool = True) -> str:
    """Builds a contextualized prompt with few-shot demonstration examples."""
    prompt_parts = []
    
    if include_examples:
        prompt_parts.append("### Reference Examples:")
        for idx, ex in enumerate(FEW_SHOT_REFERENCES, 1):
            prompt_parts.append(f"Example {idx} Requirement: {ex['requirement']}")
            prompt_parts.append(f"Example {idx} Code:\n```python\n{ex['code']}\n```\n")
    
    prompt_parts.append(f"### Target Requirement:\n{requirement}")
    prompt_parts.append("\nGenerate the complete, executable Python code snippet fulfilling the target requirement:")
    return "\n".join(prompt_parts)

def build_repair_prompt(original_code: str, error_message: str) -> str:
    """Creates a targeted prompt to auto-fix code that failed AST syntax validation."""
    return f"""The following generated Python code failed syntax validation with the error:
{error_message}

Broken Code:
```python
{original_code}
```

Fix all syntax errors and return ONLY the corrected, executable Python code in ```python ... ``` fences.
"""
