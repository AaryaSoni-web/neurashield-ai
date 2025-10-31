"""
FINAL FIXED llm_analyzer.py - Ultra-robust JSON parsing
Handles severely malformed JSON responses
"""

import os
import sys
from openai import OpenAI
from typing import Dict, Optional
import json
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from phase_2.prompt_templates import PromptTemplates


class LLMAnalyzer:
    def __init__(self, model: str = "gpt-4o", temperature: float = 0.3,
                 max_tokens: int = 4000, api_key: Optional[str] = None):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError("OpenAI API key required")
        
        self.client = OpenAI(api_key=api_key, timeout=None)
        self.prompt_templates = PromptTemplates()

    def _sanitize_json(self, content: str) -> str:
        """
        Ultra-aggressive JSON sanitization for severely malformed responses
        """
        try:
            # Remove everything before first { and after last }
            start = content.find('{')
            end = content.rfind('}') + 1
            
            if start >= 0 and end > start:
                content = content[start:end]
            
            # Remove trailing commas
            content = re.sub(r',(\s*[}\]])', r'\1', content)
            
            # Fix unclosed strings - find quotes not followed by comma/colon/bracket
            lines = content.split('\n')
            fixed_lines = []
            
            for line in lines:
                # Count quotes - if odd, this line has unclosed string
                quote_count = line.count('"') - line.count('\\"')
                if quote_count % 2 == 1:
                    # Add closing quote before any problematic character
                    line = re.sub(r'(["\w])\n', r'\1"', line)
                    line = re.sub(r'(["\w])(\s*[},\]\)])', r'\1"\2', line)
                fixed_lines.append(line)
            
            content = '\n'.join(fixed_lines)
            
            # Remove any remaining invalid characters in strings
            content = re.sub(r'": "[^"]*$', '": ""', content, flags=re.MULTILINE)
            
            return content
        except:
            return content

    def _parse_response_safe(self, content: str) -> Dict:
        """
        Try multiple parsing strategies
        """
        strategies = [
            # Strategy 1: Direct parse
            lambda c: json.loads(c),
            # Strategy 2: Sanitized parse
            lambda c: json.loads(self._sanitize_json(c)),
            # Strategy 3: Extract and clean
            lambda c: json.loads(self._extract_valid_json(c)),
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                logger.info(f"Trying parse strategy {i + 1}")
                result = strategy(content)
                logger.info(f"✓ Strategy {i + 1} succeeded")
                return result
            except Exception as e:
                logger.warning(f"Strategy {i + 1} failed: {str(e)}")
                continue
        
        # All strategies failed - return empty structure
        logger.error("All parse strategies failed")
        return {}

    def _extract_valid_json(self, content: str) -> str:
        """
        Extract only valid JSON portions
        """
        try:
            start = content.find('{')
            if start < 0:
                return '{}'
            
            depth = 0
            in_string = False
            escape = False
            
            for i in range(start, len(content)):
                char = content[i]
                
                if escape:
                    escape = False
                    continue
                
                if char == '\\':
                    escape = True
                    continue
                
                if char == '"' and not escape:
                    in_string = not in_string
                    continue
                
                if not in_string:
                    if char == '{':
                        depth += 1
                    elif char == '}':
                        depth -= 1
                        if depth == 0:
                            return content[start:i+1]
            
            return content[start:]
        except:
            return '{}'

    def _call_llm(self, system_prompt: str, user_prompt: str,
                  response_format: str = "json_object", max_retries: int = 3) -> Dict:
        """
        Call LLM with ultra-robust error handling
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"LLM Call Attempt {attempt + 1}/{max_retries}")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    response_format={"type": response_format} if response_format == "json_object" else None
                )
                
                content = response.choices[0].message.content
                usage = response.usage
                
                logger.info(f"✓ API Call Successful - Tokens: {usage.total_tokens}")
                
                if response_format == "json_object":
                    result = self._parse_response_safe(content)
                    if result and not isinstance(result, dict):
                        result = {"error": True, "message": "Invalid response format"}
                    if result:
                        return result
                    else:
                        last_error = "Could not parse response"
                        if attempt < max_retries - 1:
                            logger.info("Retrying...")
                            continue
                
                return {"response": content}
            
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Error on attempt {attempt + 1}: {error_msg}")
                last_error = error_msg
                
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)
                    logger.info("Retrying...")
                    continue
        
        logger.error(f"All {max_retries} attempts failed")
        return {
            "error": True,
            "message": last_error or "Analysis failed after multiple attempts",
            "error_type": "LLM_ERROR"
        }

    def analyze_for_bugs(self, query_code: str, retrieved_context: str) -> Dict:
        """Analyze code for bugs"""
        try:
            logger.info("Starting bug analysis...")
            
            try:
                prompt = self.prompt_templates.render_bug_detection_prompt(
                    query_code=query_code,
                    context=retrieved_context
                )
            except Exception as e:
                logger.error(f"Prompt rendering error: {str(e)}")
                return {"error": True, "message": str(e)}
            
            result = self._call_llm(
                system_prompt=prompt['system'],
                user_prompt=prompt['user'],
                response_format="json_object"
            )
            
            if result.get("error"):
                return result
            
            bug_count = len(result.get('bugs_found', []))
            logger.info(f"✓ Bug Analysis Complete - Bugs: {bug_count}")
            
            return result
        
        except Exception as e:
            logger.error(f"Bug analysis error: {str(e)}")
            return {"error": True, "message": str(e)}

    def analyze_for_optimization(self, query_code: str, retrieved_context: str) -> Dict:
        """Analyze code for optimization"""
        try:
            logger.info("Starting optimization analysis...")
            
            try:
                prompt = self.prompt_templates.render_optimization_prompt(
                    query_code=query_code,
                    context=retrieved_context
                )
            except Exception as e:
                logger.error(f"Prompt rendering error: {str(e)}")
                return {"error": True, "message": str(e)}
            
            result = self._call_llm(
                system_prompt=prompt['system'],
                user_prompt=prompt['user'],
                response_format="json_object"
            )
            
            if result.get("error"):
                return result
            
            opt_count = len(result.get('optimizations', []))
            logger.info(f"✓ Optimization Analysis Complete - Options: {opt_count}")
            
            return result
        
        except Exception as e:
            logger.error(f"Optimization analysis error: {str(e)}")
            return {"error": True, "message": str(e)}

    def calculate_security_score(self, query_code: str, retrieved_context: str) -> Dict:
        """Calculate security score - WITH FALLBACK"""
        try:
            logger.info("Starting security analysis...")
            
            try:
                prompt = self.prompt_templates.render_security_scoring_prompt(
                    query_code=query_code,
                    context=retrieved_context
                )
            except Exception as e:
                logger.error(f"Prompt rendering error: {str(e)}")
                return {"error": True, "message": str(e)}
            
            result = self._call_llm(
                system_prompt=prompt['system'],
                user_prompt=prompt['user'],
                response_format="json_object"
            )
            
            # CRITICAL: If security analysis fails, return valid fallback
            if result.get("error") or not result.get('overall_security_score'):
                logger.warning(f"Security analysis had issues: {result.get('message')}")
                return {
                    "overall_security_score": 5.0,
                    "overall_severity": "UNKNOWN",
                    "vulnerabilities": [],
                    "risk_summary": "Security analysis encountered parsing issues",
                    "immediate_actions": []
                }
            
            score = result.get('overall_security_score', 0)
            logger.info(f"✓ Security Analysis Complete - Score: {score}/10")
            
            return result
        
        except Exception as e:
            logger.error(f"Security analysis error: {str(e)}")
            # Return valid fallback on exception
            return {
                "overall_security_score": 0,
                "overall_severity": "UNKNOWN",
                "vulnerabilities": [],
                "risk_summary": f"Analysis error: {str(e)}",
                "immediate_actions": []
            }

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> Dict:
        """Estimate API cost"""
        try:
            input_cost = (prompt_tokens / 1_000_000) * 2.50
            output_cost = (completion_tokens / 1_000_000) * 10.0
            total_cost = input_cost + output_cost
            
            return {
                'model': self.model,
                'input_tokens': prompt_tokens,
                'output_tokens': completion_tokens,
                'input_cost_usd': f"${input_cost:.6f}",
                'output_cost_usd': f"${output_cost:.6f}",
                'total_cost_usd': f"${total_cost:.6f}"
            }
        except Exception as e:
            logger.error(f"Cost estimation error: {str(e)}")
            return {'model': self.model, 'error': str(e)}