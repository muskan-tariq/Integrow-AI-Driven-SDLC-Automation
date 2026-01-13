import logging
import os
import json
from typing import List, Dict, Any, Optional
from services.llm_service import LLMService
from models.review import ReviewIssue, CodeReviewReport

logger = logging.getLogger(__name__)

class CodeReviewerAgent:
    """
    AI Agent responsible for reviewing code.
    Uses LLM to identify bugs, security flaws, and style issues.
    """

    def __init__(self):
        self.llm = LLMService()

    async def review_file(self, file_path: str, content: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a single file for potential issues.
        """
        logger.info(f"Reviewing file: {file_path}")
        
        # 1. Run local linters for extra context
        linter_output = await self._run_local_linter(file_path)
        
        # 2. Build prompt including linter findings
        prompt = self._build_review_prompt(file_path, content, context, linter_output)
        
        try:
            # Use LLM to perform the review
            # We use a higher max_tokens because review reports can be long
            response = await self.llm.complete(prompt, max_tokens=3000)
            
            raw_text = response["text"].strip()
            
            # Extract JSON from response
            review_data = self._extract_json(raw_text)
            
            if not review_data:
                logger.error(f"Failed to extract JSON review for {file_path}")
                return {
                    "score": 0,
                    "summary": "Failed to parse AI review output.",
                    "issues": []
                }
            
            return review_data

        except Exception as e:
            logger.error(f"Error during code review for {file_path}: {e}")
            return {
                "score": 0,
                "summary": f"Error during review: {str(e)}",
                "issues": []
            }

    async def _run_local_linter(self, file_path: str) -> str:
        """Runs a local linter and returns the output string."""
        import subprocess
        
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.py':
            cmd = ["pylint", "--output-format=text", file_path]
        elif ext in ['.js', '.ts', '.tsx']:
            cmd = ["eslint", file_path]
        else:
            return ""

        try:
            # Note: In a real desktop app, we'd need to ensure the linter is in the path
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            return f"{stdout}\n{stderr}"
        except Exception as e:
            return f"Linter error or not installed: {str(e)}"

    def _build_review_prompt(self, file_path: str, content: str, context: Optional[str], linter_output: str = "") -> str:
        extension = os.path.splitext(file_path)[1]
        language = "Python" if extension == ".py" else "JavaScript/TypeScript" if extension in [".js", ".ts", ".tsx"] else "Unknown"
        
        context_str = f"\nProject Context:\n{context}\n" if context else ""
        linter_str = f"\nLOCAL LINTER FINDINGS:\n{linter_output}\n" if linter_output else ""

        return f"""
You are an expert Senior Software Engineer and Security Researcher.
Your task is to perform a deep code review of the following {language} file: `{file_path}`.

{context_str}
{linter_str}

CODE TO REVIEW:
```{language.lower()}
{content}
```

INSTRUCTIONS:
1. Identify bugs, potential security vulnerabilities (SQLi, XSS, insecure defaults), performance bottlenecks, and violations of clean code principles.
2. For each issue, provide the line number, type, severity, a clear description, and a suggested fix.
3. Provide an overall quality score from 0 (terrible) to 100 (perfect).
4. Provide a brief summary of the file's health.

RESPONSE FORMAT:
You must return ONLY a JSON object with the following structure:
{{
  "score": 85,
  "summary": "Overall good structure but has some security concerns regarding input validation.",
  "issues": [
    {{
      "line_number": 12,
      "issue_type": "security",
      "severity": "high",
      "description": "Potential SQL injection vulnerability. User input is concatenated directly into the query.",
      "suggested_fix": "Use parameterized queries or an ORM."
    }},
    {{
      "line_number": 45,
      "issue_type": "style",
      "severity": "low",
      "description": "Variable name 'x' is not descriptive.",
      "suggested_fix": "Rename 'x' to something more meaningful like 'user_count'."
    }}
  ]
}}

Return ONLY the JSON. No markdown backticks, no explanation before or after.
"""

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        try:
            # Try to find JSON block
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            return json.loads(text)
        except Exception:
            return None
