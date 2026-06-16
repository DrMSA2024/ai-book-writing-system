"""LaTeX error correction agent."""

import re
from typing import Tuple, List
from loguru import logger

from src.agents.base_agent import BaseAgent
from src.api.deepseek_client import DeepSeekClient
from src.memory.memory_manager import MemoryManager


class LaTeXErrorAgent(BaseAgent):
    """Detects and corrects LaTeX compilation errors."""

    def __init__(
        self,
        api_client: DeepSeekClient,
        memory_manager: MemoryManager,
    ):
        """Initialize LaTeX error agent.

        Args:
            api_client: DeepSeek API client
            memory_manager: Memory manager
        """
        super().__init__(
            name="LaTeXErrorAgent",
            description="Detects and corrects LaTeX errors",
            api_client=api_client,
            memory_manager=memory_manager,
        )

    async def execute(
        self,
        latex_code: str,
        error_log: str = "",
    ) -> Tuple[str, List[str]]:
        """Correct LaTeX errors.

        Args:
            latex_code: LaTeX code to fix
            error_log: Compilation error log

        Returns:
            Tuple of (corrected_code, corrections_made)
        """
        self.log_info("Analyzing LaTeX for errors")

        corrections = []

        try:
            # Apply automatic fixes
            corrected_code = latex_code
            corrected_code, auto_fixes = await self._apply_automatic_fixes(
                corrected_code
            )
            corrections.extend(auto_fixes)

            # If error log provided, use AI to fix remaining issues
            if error_log:
                corrected_code, ai_fixes = await self._fix_compilation_errors(
                    corrected_code, error_log
                )
                corrections.extend(ai_fixes)

            self.log_info(f"Applied {len(corrections)} corrections")
            return corrected_code, corrections

        except Exception as e:
            self.log_error(f"Error correction failed: {e}")
            return latex_code, []

    async def _apply_automatic_fixes(
        self, latex_code: str
    ) -> Tuple[str, List[str]]:
        """Apply automatic common fixes.

        Args:
            latex_code: LaTeX code

        Returns:
            Tuple of (fixed_code, fixes_applied)
        """
        fixes = []
        code = latex_code

        # Fix 1: Missing closing braces
        if code.count("{") > code.count("}"):
            code += "}" * (code.count("{") - code.count("}"))
            fixes.append("Added missing closing braces")

        # Fix 2: Unmatched \begin and \end
        begin_count = len(re.findall(r"\\begin", code))
        end_count = len(re.findall(r"\\end", code))
        if begin_count > end_count:
            # Add missing \end statements
            for _ in range(begin_count - end_count):
                code += "\n\\end{document}"
            fixes.append("Closed unclosed environments")

        # Fix 3: Invalid package declarations
        code = re.sub(
            r"\\usepackage\{(\w+)\\}",
            r"\\usepackage{\1}",
            code,
        )
        if code != latex_code:
            fixes.append("Fixed package declarations")

        # Fix 4: Missing \documentclass
        if not re.search(r"\\documentclass", code):
            code = "\\documentclass{book}\n\n" + code
            fixes.append("Added missing documentclass")

        # Fix 5: Missing \begin{document}
        if not re.search(r"\\begin\{document\}", code):
            # Insert before content
            lines = code.split("\n")
            insert_pos = len(lines)
            for i, line in enumerate(lines):
                if re.search(r"\\(chapter|section|maketitle)", line):
                    insert_pos = i
                    break
            lines.insert(insert_pos, "\\begin{document}")
            code = "\n".join(lines)
            fixes.append("Added missing begin{document}")

        # Fix 6: Escape special characters in text
        # (Be careful not to escape in math mode)
        code = re.sub(r"([^\\])(%[^a-zA-Z])", r"\1\\\2", code)
        if code != latex_code:
            fixes.append("Escaped special characters")

        # Fix 7: Fix unclosed equations
        if code.count("$") % 2 != 0:
            code += " $"
            fixes.append("Closed unclosed inline math")

        return code, fixes

    async def _fix_compilation_errors(
        self,
        latex_code: str,
        error_log: str,
    ) -> Tuple[str, List[str]]:
        """Fix errors detected in compilation log.

        Args:
            latex_code: LaTeX code
            error_log: Error log from compilation

        Returns:
            Tuple of (fixed_code, fixes_applied)
        """
        self.log_info("Analyzing compilation errors with AI")

        # Extract key errors from log
        errors = self._extract_errors_from_log(error_log)

        if not errors:
            return latex_code, []

        prompt = f"""
Fix the following LaTeX compilation errors. Return the corrected code.

Errors:
{error_log[:1000]}

LaTeX Code:
{latex_code[:2000]}

Provide the corrected LaTeX code:
"""

        try:
            corrected = await self.api_client.generate_text(
                prompt,
                system_prompt="You are a LaTeX expert. Fix compilation errors while preserving all content.",
                temperature=0.3,
                max_tokens=2500,
            )

            fixes = [f"AI fix: {error[:50]}" for error in errors[:3]]
            return corrected or latex_code, fixes

        except Exception as e:
            self.log_error(f"AI error correction failed: {e}")
            return latex_code, []

    def _extract_errors_from_log(self, error_log: str) -> List[str]:
        """Extract error messages from LaTeX log.

        Args:
            error_log: Error log

        Returns:
            List of errors
        """
        errors = []

        # Find lines with "Error:"
        for line in error_log.split("\n"):
            if "Error" in line or "error" in line or "!" in line:
                errors.append(line.strip())

        return errors[:10]  # Limit to 10 errors

    async def validate_latex(self, latex_code: str) -> bool:
        """Validate basic LaTeX structure.

        Args:
            latex_code: LaTeX code to validate

        Returns:
            True if structure is valid
        """
        checks = [
            (r"\\documentclass", "documentclass found"),
            (r"\\begin\{document\}", "begin{document} found"),
            (r"\\end\{document\}", "end{document} found"),
        ]

        for pattern, desc in checks:
            if not re.search(pattern, latex_code):
                self.log_error(f"Validation failed: {desc}")
                return False

        # Check brace balance
        if latex_code.count("{") != latex_code.count("}"):
            self.log_error("Validation failed: Unbalanced braces")
            return False

        return True
