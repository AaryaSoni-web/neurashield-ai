
import ast
import json
from typing import List, Dict
import tiktoken


class CodeChunker:
    def __init__(self, encoding_name: str = "cl100k_base"):
        self.encoding = tiktoken.get_encoding(encoding_name)

    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))

    def chunk_by_function(self, source_code: str, file_path: str, max_tokens: int = 500) -> List[Dict]:
        chunks = []

        try:
            tree = ast.parse(source_code)
            source_lines = source_code.splitlines()

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_lines = source_lines[node.lineno-1:node.end_lineno]
                    func_code = '\n'.join(func_lines)
                    token_count = self.count_tokens(func_code)

                    if token_count > max_tokens:
                        sub_chunks = self._split_large_chunk(
                            func_code, file_path, node.name, node.lineno, max_tokens, 'function'
                        )
                        chunks.extend(sub_chunks)
                    else:
                        chunks.append({
                            'code': func_code,
                            'type': 'function',
                            'name': node.name,
                            'file_path': file_path,
                            'line_start': node.lineno,
                            'line_end': node.end_lineno,
                            'token_count': token_count,
                            'is_async': isinstance(node, ast.AsyncFunctionDef),
                            'args': [arg.arg for arg in node.args.args]
                        })

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_lines = source_lines[node.lineno-1:node.end_lineno]
                    class_code = '\n'.join(class_lines)
                    token_count = self.count_tokens(class_code)

                    if token_count > max_tokens:
                        for method_node in node.body:
                            if isinstance(method_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                method_lines = source_lines[method_node.lineno-1:method_node.end_lineno]
                                method_code = '\n'.join(method_lines)
                                method_tokens = self.count_tokens(method_code)

                                chunks.append({
                                    'code': method_code,
                                    'type': 'method',
                                    'name': f"{node.name}.{method_node.name}",
                                    'class_name': node.name,
                                    'method_name': method_node.name,
                                    'file_path': file_path,
                                    'line_start': method_node.lineno,
                                    'line_end': method_node.end_lineno,
                                    'token_count': method_tokens
                                })
                    else:
                        chunks.append({
                            'code': class_code,
                            'type': 'class',
                            'name': node.name,
                            'file_path': file_path,
                            'line_start': node.lineno,
                            'line_end': node.end_lineno,
                            'token_count': token_count,
                            'methods': [
                                n.name for n in node.body 
                                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                            ]
                        })

            if not chunks:
                total_tokens = self.count_tokens(source_code)
                if total_tokens > max_tokens:
                    chunks = self._split_large_chunk(source_code, file_path, file_path, 1, max_tokens, 'module')
                else:
                    chunks.append({
                        'code': source_code,
                        'type': 'module',
                        'name': file_path,
                        'file_path': file_path,
                        'line_start': 1,
                        'line_end': len(source_lines),
                        'token_count': total_tokens
                    })

        except SyntaxError:
            return self._split_by_lines(source_code, file_path, max_tokens)

        return chunks

    def _split_large_chunk(self, code: str, file_path: str, name: str, line_start: int, 
                          max_tokens: int, chunk_type: str) -> List[Dict]:
        lines = code.splitlines()
        sub_chunks = []
        current_chunk = []
        current_tokens = 0
        part_num = 1

        for line in lines:
            line_tokens = self.count_tokens(line + '\n')

            if current_tokens + line_tokens > max_tokens and current_chunk:
                chunk_code = '\n'.join(current_chunk)
                sub_chunks.append({
                    'code': chunk_code,
                    'type': f'{chunk_type}_part',
                    'name': f"{name}_part_{part_num}",
                    'file_path': file_path,
                    'line_start': line_start,
                    'token_count': current_tokens,
                    'parent_name': name
                })
                part_num += 1
                current_chunk = [line]
                current_tokens = line_tokens
            else:
                current_chunk.append(line)
                current_tokens += line_tokens

        if current_chunk:
            chunk_code = '\n'.join(current_chunk)
            sub_chunks.append({
                'code': chunk_code,
                'type': f'{chunk_type}_part',
                'name': f"{name}_part_{part_num}",
                'file_path': file_path,
                'line_start': line_start,
                'token_count': self.count_tokens(chunk_code),
                'parent_name': name
            })

        return sub_chunks

    def _split_by_lines(self, source_code: str, file_path: str, max_tokens: int) -> List[Dict]:
        lines = source_code.splitlines()
        chunks = []
        current_chunk = []
        current_tokens = 0
        chunk_num = 1

        for line in lines:
            line_tokens = self.count_tokens(line + '\n')

            if current_tokens + line_tokens > max_tokens and current_chunk:
                chunk_code = '\n'.join(current_chunk)
                chunks.append({
                    'code': chunk_code,
                    'type': 'fallback',
                    'name': f"{file_path}_chunk_{chunk_num}",
                    'file_path': file_path,
                    'chunk_index': chunk_num - 1,
                    'token_count': current_tokens
                })
                chunk_num += 1
                current_chunk = [line]
                current_tokens = line_tokens
            else:
                current_chunk.append(line)
                current_tokens += line_tokens

        if current_chunk:
            chunk_code = '\n'.join(current_chunk)
            chunks.append({
                'code': chunk_code,
                'type': 'fallback',
                'name': f"{file_path}_chunk_{chunk_num}",
                'file_path': file_path,
                'chunk_index': chunk_num - 1,
                'token_count': self.count_tokens(chunk_code)
            })

        return chunks

    def chunk_preprocessed_files(self, preprocessed_file: str = 'preprocessed_code.json',
                                output_file: str = 'chunked_code.json',
                                max_tokens: int = 500, use_cleaned: bool = True):
        with open(preprocessed_file, 'r', encoding='utf-8') as f:
            files = json.load(f)

        all_chunks = []

        for file_data in files:
            code_to_chunk = file_data.get('cleaned_code' if use_cleaned else 'source_code', '')
            if not code_to_chunk:
                code_to_chunk = file_data.get('source_code', '')

            file_path = file_data['file_path']
            chunks = self.chunk_by_function(code_to_chunk, file_path, max_tokens)

            for chunk in chunks:
                chunk['file_metadata'] = {
                    'loc': file_data.get('loc', 0),
                    'functions': file_data.get('functions', []),
                    'classes': file_data.get('classes', []),
                    'imports': file_data.get('imports', []),
                    'complexity_score': file_data.get('complexity_score', 0)
                }

            all_chunks.extend(chunks)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_chunks, f, indent=2, ensure_ascii=False)

        avg_tokens = sum(c['token_count'] for c in all_chunks) / len(all_chunks) if all_chunks else 0
        print(f"Chunked {len(files)} files into {len(all_chunks)} chunks (avg {avg_tokens:.1f} tokens)")


if __name__ == "__main__":
    chunker = CodeChunker()
    chunker.chunk_preprocessed_files(
        preprocessed_file='phase_1/preprocessed_code.json',
        output_file='phase_1/chunked_code.json',
        max_tokens=500,
        use_cleaned=True
    )