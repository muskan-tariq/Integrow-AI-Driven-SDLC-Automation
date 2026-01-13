"""
Technical Debt Analyzer Agent
Analyzes codebases for technical debt including complexity, duplication, and code smells.
"""
import os
import ast
import logging
import re
import hashlib
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
from collections import defaultdict
from services.llm_service import LLMService

logger = logging.getLogger(__name__)


class TechnicalDebtAnalyzer:
    """Analyzes code for technical debt issues."""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.exclude_dirs = {'.git', 'venv', '__pycache__', 'node_modules', '.next', 'dist', 'build', 'coverage'}
        self.code_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.cpp', '.c', '.cs', '.go', '.rb', '.php'}
        self.file_contents = {}  # Cache for duplication detection
    
    async def analyze_project(self, project_path: str, include_tests: bool = True, max_depth: int = 10, specific_files: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze entire project or specific files for technical debt.
        
        Args:
            project_path: Root path of project
            include_tests: Whether to include test files
            max_depth: Maximum directory depth
            specific_files: Optional list of specific file paths to analyze
        
        Returns:
            Dict with overall_score, issues, and category scores
        """
        logger.info(f"Starting technical debt analysis for: {project_path}")
        
        all_issues = []
        files_analyzed = 0
        self.file_contents = {}
        
        # Collect files to analyze
        if specific_files:
            code_files = [os.path.join(project_path, f) for f in specific_files if os.path.exists(os.path.join(project_path, f))]
        else:
            code_files = self._collect_code_files(project_path, include_tests, max_depth)
        
        # First pass: Load all file contents for duplication detection
        for file_path in code_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                rel_path = os.path.relpath(file_path, project_path).replace("\\", "/")
                self.file_contents[rel_path] = content
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
        
        # Second pass: Analyze each file
        for file_path in code_files:
            try:
                rel_path = os.path.relpath(file_path, project_path).replace("\\", "/")
                content = self.file_contents.get(rel_path, "")
                
                # 1. Analyze complexity
                complexity_issues = self._analyze_complexity(content, rel_path, file_path)
                all_issues.extend(complexity_issues)
                
                # 2. Detect code smells (long methods, dead code)
                smell_issues = self._detect_code_smells(content, rel_path, file_path)
                all_issues.extend(smell_issues)
                
                files_analyzed += 1
                
            except Exception as e:
                logger.error(f"Error analyzing {file_path}: {e}")
                continue
        
        # 3. Detect duplication across all files
        duplication_issues = self._detect_duplication(project_path)
        all_issues.extend(duplication_issues)
        
        # 4. Analyze dependencies
        dependency_issues = self._analyze_dependencies(project_path)
        all_issues.extend(dependency_issues)
        
        # Calculate scores
        scores = self._calculate_scores(all_issues, files_analyzed)
        
        return {
            "overall_score": scores["overall"],
            "complexity_score": scores["complexity"],
            "duplication_score": scores["duplication"],
            "dependency_score": scores["dependency"],
            "total_issues": len(all_issues),
            "critical_issues": sum(1 for i in all_issues if i["severity"] == "critical"),
            "estimated_hours": sum(i.get("estimated_hours", 0) for i in all_issues),
            "issues": all_issues,
            "files_analyzed": files_analyzed
        }
    
    def _collect_code_files(self, project_path: str, include_tests: bool, max_depth: int) -> List[str]:
        """Collect all code files to analyze."""
        code_files = []
        
        for root, dirs, files in os.walk(project_path):
            depth = root[len(project_path):].count(os.sep)
            if depth >= max_depth:
                dirs[:] = []
                continue
            
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            if not include_tests:
                dirs[:] = [d for d in dirs if 'test' not in d.lower() and 'spec' not in d.lower()]
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in self.code_extensions:
                    if not include_tests and ('test' in file.lower() or 'spec' in file.lower()):
                        continue
                    code_files.append(os.path.join(root, file))
        
        return code_files
    
    def _analyze_complexity(self, content: str, rel_path: str, abs_path: str) -> List[Dict[str, Any]]:
        """Analyze code complexity for Python and JavaScript/TypeScript."""
        issues = []
        
        if abs_path.endswith('.py'):
            issues.extend(self._analyze_python_complexity(content, rel_path))
        elif abs_path.endswith(('.js', '.ts', '.tsx', '.jsx')):
            issues.extend(self._analyze_js_complexity(content, rel_path))
        
        return issues
    
    def _analyze_python_complexity(self, content: str, rel_path: str) -> List[Dict[str, Any]]:
        """Analyze Python code complexity."""
        issues = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    complexity = self._calculate_cyclomatic_complexity(node)
                    
                    if complexity > 15:
                        severity = "critical" if complexity > 25 else "high" if complexity > 20 else "medium"
                        estimated_hours = (complexity - 15) * 0.5
                        
                        issues.append({
                            "file_path": rel_path,
                            "issue_type": "complexity",
                            "category": "High Cyclomatic Complexity",
                            "severity": severity,
                            "title": f"Function '{node.name}' has high complexity ({complexity})",
                            "description": f"The function '{node.name}' has a cyclomatic complexity of {complexity}, which exceeds the recommended threshold of 15. High complexity makes code harder to understand, test, and maintain.",
                            "line_start": node.lineno,
                            "line_end": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                            "suggested_fix": "Consider breaking this function into smaller, more focused functions. Extract complex conditional logic into separate helper functions.",
                            "estimated_hours": round(estimated_hours, 1)
                        })
                
                elif isinstance(node, ast.ClassDef):
                    method_count = sum(1 for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
                    
                    if method_count > 20:
                        issues.append({
                            "file_path": rel_path,
                            "issue_type": "architecture",
                            "category": "God Object",
                            "severity": "high",
                            "title": f"Class '{node.name}' has too many methods ({method_count})",
                            "description": f"The class '{node.name}' has {method_count} methods, indicating it may have too many responsibilities. This violates the Single Responsibility Principle.",
                            "line_start": node.lineno,
                            "line_end": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                            "suggested_fix": "Consider splitting this class into multiple smaller classes, each with a single, well-defined responsibility.",
                            "estimated_hours": method_count * 0.3
                        })
        
        except SyntaxError:
            pass
        except Exception as e:
            logger.error(f"Error analyzing Python complexity for {rel_path}: {e}")
        
        return issues
    
    def _analyze_js_complexity(self, content: str, rel_path: str) -> List[Dict[str, Any]]:
        """Analyze JavaScript/TypeScript complexity using regex patterns."""
        issues = []
        
        # Simple regex-based complexity for JS/TS
        functions = re.finditer(r'(?:function|const|let|var)\s+(\w+)\s*[=\(].*?{', content)
        
        for match in functions:
            func_name = match.group(1)
            start_pos = match.start()
            
            # Find function body (simplified)
            brace_count = 0
            func_start = content.find('{', start_pos)
            if func_start == -1:
                continue
            
            func_end = func_start
            for i in range(func_start, len(content)):
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        func_end = i
                        break
            
            func_body = content[func_start:func_end]
            
            # Count decision points
            complexity = 1
            complexity += len(re.findall(r'\bif\b', func_body))
            complexity += len(re.findall(r'\bfor\b', func_body))
            complexity += len(re.findall(r'\bwhile\b', func_body))
            complexity += len(re.findall(r'\bcase\b', func_body))
            complexity += len(re.findall(r'\bcatch\b', func_body))
            complexity += len(re.findall(r'&&|\|\|', func_body))
            
            if complexity > 15:
                severity = "critical" if complexity > 25 else "high" if complexity > 20 else "medium"
                line_num = content[:start_pos].count('\n') + 1
                
                issues.append({
                    "file_path": rel_path,
                    "issue_type": "complexity",
                    "category": "High Cyclomatic Complexity",
                    "severity": severity,
                    "title": f"Function '{func_name}' has high complexity ({complexity})",
                    "description": f"This function has a cyclomatic complexity of {complexity}, which exceeds the recommended threshold of 15.",
                    "line_start": line_num,
                    "suggested_fix": "Break down this function into smaller, more focused functions.",
                    "estimated_hours": round((complexity - 15) * 0.5, 1)
                })
        
        return issues
    
    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a Python function."""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _detect_code_smells(self, content: str, rel_path: str, abs_path: str) -> List[Dict[str, Any]]:
        """Detect code smells: long methods, dead code, unused variables."""
        issues = []
        
        lines = content.split('\n')
        
        # Detect long functions/methods
        if abs_path.endswith('.py'):
            issues.extend(self._detect_long_python_functions(content, rel_path))
            issues.extend(self._detect_unused_python_variables(content, rel_path))
        elif abs_path.endswith(('.js', '.ts', '.tsx', '.jsx')):
            issues.extend(self._detect_long_js_functions(content, rel_path))
        
        return issues
    
    def _detect_long_python_functions(self, content: str, rel_path: str) -> List[Dict[str, Any]]:
        """Detect long Python functions (>50 lines)."""
        issues = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if hasattr(node, 'end_lineno'):
                        func_length = node.end_lineno - node.lineno
                        
                        if func_length > 50:
                            severity = "high" if func_length > 100 else "medium"
                            
                            issues.append({
                                "file_path": rel_path,
                                "issue_type": "smell",
                                "category": "Long Method",
                                "severity": severity,
                                "title": f"Function '{node.name}' is too long ({func_length} lines)",
                                "description": f"This function has {func_length} lines of code, which exceeds the recommended maximum of 50 lines. Long functions are harder to understand and maintain.",
                                "line_start": node.lineno,
                                "line_end": node.end_lineno,
                                "suggested_fix": "Break this function into smaller, focused functions with clear responsibilities.",
                                "estimated_hours": round((func_length - 50) * 0.05, 1)
                            })
        except:
            pass
        
        return issues
    
    def _detect_long_js_functions(self, content: str, rel_path: str) -> List[Dict[str, Any]]:
        """Detect long JavaScript/TypeScript functions."""
        issues = []
        lines = content.split('\n')
        
        func_pattern = re.finditer(r'(?:function|const|let)\s+(\w+)\s*[=\(].*?{', content)
        
        for match in func_pattern:
            func_name = match.group(1)
            start_pos = match.start()
            start_line = content[:start_pos].count('\n') + 1
            
            # Find function end
            brace_count = 0
            func_start = content.find('{', start_pos)
            if func_start == -1:
                continue
            
            func_end_pos = func_start
            for i in range(func_start, len(content)):
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        func_end_pos = i
                        break
            
            end_line = content[:func_end_pos].count('\n') + 1
            func_length = end_line - start_line
            
            if func_length > 50:
                severity = "high" if func_length > 100 else "medium"
                
                issues.append({
                    "file_path": rel_path,
                    "issue_type": "smell",
                    "category": "Long Method",
                    "severity": severity,
                    "title": f"Function '{func_name}' is too long ({func_length} lines)",
                    "description": f"This function has {func_length} lines of code, which exceeds the recommended maximum of 50 lines.",
                    "line_start": start_line,
                    "line_end": end_line,
                    "suggested_fix": "Break this function into smaller, focused functions.",
                    "estimated_hours": round((func_length - 50) * 0.05, 1)
                })
        
        return issues
    
    def _detect_unused_python_variables(self, content: str, rel_path: str) -> List[Dict[str, Any]]:
        """Detect unused variables in Python code."""
        issues = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Get all assigned variables
                    assigned_vars = set()
                    used_vars = set()
                    
                    for child in ast.walk(node):
                        if isinstance(child, ast.Name):
                            if isinstance(child.ctx, ast.Store):
                                assigned_vars.add(child.id)
                            elif isinstance(child.ctx, ast.Load):
                                used_vars.add(child.id)
                    
                    # Find unused (excluding common prefixes like _ or __)
                    unused = assigned_vars - used_vars
                    unused = {v for v in unused if not v.startswith('_')}
                    
                    if unused:
                        issues.append({
                            "file_path": rel_path,
                            "issue_type": "smell",
                            "category": "Unused Variable",
                            "severity": "low",
                            "title": f"Function '{node.name}' has unused variables: {', '.join(list(unused)[:3])}",
                            "description": f"Found {len(unused)} unused variable(s): {', '.join(list(unused))}. Remove unused variables to improve code clarity.",
                            "line_start": node.lineno,
                            "suggested_fix": "Remove the unused variables or prefix them with underscore if intentionally unused.",
                            "estimated_hours": 0.1
                        })
        except:
            pass
        
        return issues
    
    def _detect_duplication(self, project_path: str) -> List[Dict[str, Any]]:
        """Detect code duplication across files."""
        issues = []
        
        # Simple hash-based duplication detection
        code_block_hashes = defaultdict(list)
        min_block_size = 5  # Minimum lines to consider
        
        for rel_path, content in self.file_contents.items():
            lines = content.split('\n')
            
            # Create sliding window of code blocks
            for i in range(len(lines) - min_block_size + 1):
                block = '\n'.join(lines[i:i + min_block_size])
                # Normalize whitespace
                normalized = re.sub(r'\s+', ' ', block.strip())
                
                if len(normalized) > 50:  # Ignore very short blocks
                    block_hash = hashlib.md5(normalized.encode()).hexdigest()
                    code_block_hashes[block_hash].append((rel_path, i + 1))
        
        # Find duplicates
        reported_hashes = set()
        for block_hash, occurrences in code_block_hashes.items():
            if len(occurrences) > 1 and block_hash not in reported_hashes:
                reported_hashes.add(block_hash)
                
                # Report duplication
                files_affected = ', '.join(set(f[0] for f in occurrences[:3]))
                
                issues.append({
                    "file_path": occurrences[0][0],
                    "issue_type": "duplication",
                    "category": "Code Duplication",
                    "severity": "medium" if len(occurrences) > 3 else "low",
                    "title": f"Duplicate code block found in {len(occurrences)} locations",
                    "description": f"This code block appears in {len(occurrences)} different locations: {files_affected}. Consider extracting to a shared function.",
                    "line_start": occurrences[0][1],
                    "line_end": occurrences[0][1] + min_block_size,
                    "suggested_fix": "Extract this duplicated code into a reusable function or module.",
                    "estimated_hours": 0.5 * len(occurrences)
                })
        
        return issues
    
    def _analyze_dependencies(self, project_path: str) -> List[Dict[str, Any]]:
        """Analyze project dependencies for outdated packages."""
        issues = []
        
        # Check Python requirements
        requirements_file = os.path.join(project_path, 'requirements.txt')
        if os.path.exists(requirements_file):
            try:
                with open(requirements_file, 'r') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Simple check: flag any pinned old versions
                        if '==' in line:
                            package_name = line.split('==')[0].strip()
                            version = line.split('==')[1].strip()
                            
                            # Flag as potential outdated (simplified)
                            if any(old in version for old in ['0.', '1.', '2.']) and package_name not in ['python']:
                                issues.append({
                                    "file_path": "requirements.txt",
                                    "issue_type": "dependency",
                                    "category": "Potentially Outdated Dependency",
                                    "severity": "low",
                                    "title": f"Package '{package_name}' may be outdated (v{version})",
                                    "description": f"The package '{package_name}' is pinned to version {version}. Consider checking for updates.",
                                    "line_start": line_num,
                                    "suggested_fix": f"Run 'pip list --outdated' to check for newer versions of {package_name}.",
                                    "estimated_hours": 0.2
                                })
            except Exception as e:
                logger.error(f"Error analyzing requirements.txt: {e}")
        
        # Check Node.js package.json
        package_json = os.path.join(project_path, 'package.json')
        if os.path.exists(package_json):
            try:
                import json
                with open(package_json, 'r') as f:
                    data = json.load(f)
                
                deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                
                for pkg, version in deps.items():
                    # Flag versions with caret/tilde as potential maintenance needed
                    if version.startswith(('^', '~')):
                        issues.append({
                            "file_path": "package.json",
                            "issue_type": "dependency",
                            "category": "Flexible Dependency Version",
                            "severity": "low",
                            "title": f"Package '{pkg}' uses flexible versioning ({version})",
                            "description": f"Consider pinning exact versions for production stability.",
                            "suggested_fix": f"Run 'npm outdated' to check for updates.",
                            "estimated_hours": 0.1
                        })
            except Exception as e:
                logger.error(f"Error analyzing package.json: {e}")
        
        return issues
    
    def _calculate_scores(self, issues: List[Dict], files_analyzed: int) -> Dict[str, int]:
        """Calculate technical debt scores (0-100, higher is better)."""
        if files_analyzed == 0:
            return {"overall": 100, "complexity": 100, "duplication": 100, "dependency": 100}
        
        complexity_issues = [i for i in issues if i["issue_type"] == "complexity"]
        duplication_issues = [i for i in issues if i["issue_type"] == "duplication"]
        dependency_issues = [i for i in issues if i["issue_type"] == "dependency"]
        smell_issues = [i for i in issues if i["issue_type"] == "smell"]
        architecture_issues = [i for i in issues if i["issue_type"] == "architecture"]
        
        def calc_category_score(category_issues):
            if not category_issues:
                return 100
            
            penalty = 0
            for issue in category_issues:
                if issue["severity"] == "critical":
                    penalty += 15
                elif issue["severity"] == "high":
                    penalty += 10
                elif issue["severity"] == "medium":
                    penalty += 5
                else:
                    penalty += 2
            
            penalty_per_file = penalty / max(files_analyzed, 1)
            score = max(0, 100 - int(penalty_per_file * 10))
            return score
        
        # Combine smells and architecture into complexity score
        all_complexity = complexity_issues + smell_issues + architecture_issues
        
        complexity_score = calc_category_score(all_complexity)
        duplication_score = calc_category_score(duplication_issues)
        dependency_score = calc_category_score(dependency_issues)
        
        overall_score = int((complexity_score * 0.4 + duplication_score * 0.3 + dependency_score * 0.3))
        
        return {
            "overall": overall_score,
            "complexity": complexity_score,
            "duplication": duplication_score,
            "dependency": dependency_score
        }
