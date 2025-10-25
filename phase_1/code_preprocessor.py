
import re
import json
from typing import Dict

class CodePreprocessor:
    @staticmethod
    def remove_comments(code: str) -> str:
        lines = []
        in_string = False
        string_char = None

        for line in code.splitlines():
            cleaned = []
            i = 0
            while i < len(line):
                char = line[i]
                if char in ('"', "'") and (i == 0 or line[i-1] != '\\'):
                    if not in_string:
                        in_string = True
                        string_char = char
                    elif char == string_char:
                        in_string = False
                        string_char = None
                if char == '#' and not in_string:
                    break
                cleaned.append(char)
                i += 1
            lines.append(''.join(cleaned))

        code = '\n'.join(lines)
        code = re.sub(r'^\s*""".*?"""\s*$', '', code, flags=re.MULTILINE|re.DOTALL)
        code = re.sub(r"^\s*'''.*?'''\s*$", '', code, flags=re.MULTILINE|re.DOTALL)
        return code

    @staticmethod
    def normalize_whitespace(code: str) -> str:
        lines = [ln.rstrip() for ln in code.splitlines()]
        cleaned, prev_blank = [], False
        for ln in lines:
            blank = not ln.strip()
            if blank and prev_blank:
                continue
            cleaned.append(ln)
            prev_blank = blank
        while cleaned and not cleaned[0].strip():
            cleaned.pop(0)
        while cleaned and not cleaned[-1].strip():
            cleaned.pop()
        return '\n'.join(cleaned)

    @staticmethod
    def calculate_complexity(code: str) -> int:
        complexity = 1
        for kw in ['if ', 'elif ', 'for ', 'while ', ' and ', ' or ', 'except']:
            complexity += code.count(kw)
        return complexity

    def preprocess(self, code: str, remove_comments: bool = False) -> Dict:
        orig_len = len(code)
        if remove_comments:
            code = self.remove_comments(code)
        code = self.normalize_whitespace(code)
        cleaned_len = len(code)
        reduction = ((orig_len - cleaned_len) / orig_len * 100) if orig_len else 0
        complexity = self.calculate_complexity(code)
        return {
            'cleaned_code': code,
            'original_length': orig_len,
            'cleaned_length': cleaned_len,
            'reduction_percentage': round(reduction, 2),
            'complexity_score': complexity
        }

    def preprocess_extracted(
        self,
        extracted_file: str = 'extracted_code.json',
        output_file: str = 'preprocessed_code.json',
        remove_comments: bool = False
    ):
        with open(extracted_file, 'r', encoding='utf-8') as f:
            files = json.load(f)

        for entry in files:
            src = entry.get('source_code', '')
            res = self.preprocess(src, remove_comments)
            entry['cleaned_code'] = res['cleaned_code']
            entry['reduction_percentage'] = res['reduction_percentage']
            entry['complexity_score'] = res['complexity_score']

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(files, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    pre = CodePreprocessor()
    pre.preprocess_extracted(
        extracted_file='phase_1/extracted_code.json',
        output_file='phase_1/preprocessed_code.json',
        remove_comments=True
    )
    print("Preprocessing complete")