#!/usr/bin/env python3
"""Evaluate this model's SCAD parameter expressions, not its CSG geometry.

No dependencies. This is a limited expression evaluator for this source;
OpenSCAD rendering and physical fit checks remain separate requirements.
"""
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'p1-roof-mount.scad'


def split_top(text, separator):
    depth = 0
    quote = False
    pieces, start = [], 0
    for i, char in enumerate(text):
        if char == '"' and (i == 0 or text[i-1] != '\\'):
            quote = not quote
        if quote:
            continue
        if char in '([':
            depth += 1
        elif char in ')]':
            depth -= 1
        elif depth == 0 and char == separator:
            pieces.append(text[start:i])
            start = i + 1
    return pieces + [text[start:]]


def convert(text):
    text = text.strip()
    args = split_top(text, ',')
    if len(args) > 1:
        return ','.join(convert(arg) for arg in args)
    conditional = split_top(text, '?')
    if len(conditional) > 1:
        condition = conditional[0]
        rest = '?'.join(conditional[1:])
        # All conditionals in the parameter block have unnested true branches.
        branches = split_top(rest, ':')
        return f'({convert(branches[0])} if {convert(condition)} else {convert(":".join(branches[1:]))})'
    result, i = '', 0
    while i < len(text):
        char = text[i]
        if char in '([':
            closer = ')' if char == '(' else ']'
            depth, j = 1, i + 1
            while depth:
                if text[j] == char:
                    depth += 1
                elif text[j] == closer:
                    depth -= 1
                j += 1
            result += char + convert(text[i+1:j-1]) + closer
            i = j
        else:
            result += char
            i += 1
    result = result.replace('&&', ' and ').replace('||', ' or ')
    return re.sub(r'!(?!=)', ' not ', result).strip()


class Parameters(dict):
    def __init__(self, definitions, overrides=None, local=None):
        super().__init__(true=True, false=False, min=min, max=max, abs=abs,
                         pow=pow, sqrt=math.sqrt, ceil=math.ceil, len=len,
                         cos=lambda a: math.cos(math.radians(a)),
                         sin=lambda a: math.sin(math.radians(a)),
                         tan=lambda a: math.tan(math.radians(a)))
        self.definitions = definitions
        self.update(overrides or {})
        self.update(local or {})
        self.pending = set()

    def __missing__(self, name):
        if name not in self.definitions or name in self.pending:
            raise KeyError(name)
        self.pending.add(name)
        try:
            expression = self.definitions[name]
            function = re.fullmatch(r'function\((\w+)\)\s*(.*)', expression, re.S)
            if function:
                arg, body = function.groups()
                def call(value):
                    child = Parameters(self.definitions, dict(self), {arg: value})
                    return evaluate(body, child)
                value = call
            else:
                value = evaluate(expression, self)
            self[name] = value
            return value
        finally:
            self.pending.remove(name)


def evaluate(expression, params):
    return eval('(' + convert(expression) + ')', {'__builtins__': {}}, params)


def load(antenna='alfa', source=SOURCE):
    text = Path(source).read_text()
    clean = re.sub(r'/\*.*?\*/|//[^\n]*', '', text, flags=re.S)
    header = clean.split('function under_box', 1)[0]
    definitions = dict(re.findall(r'^\s*(\w+)\s*=\s*(.*?);', header, re.M | re.S))
    return Parameters(definitions, {'antenna': antenna}), clean


def main(source=SOURCE):
    print(f'Parameter source: {Path(source).resolve()}')
    for antenna in ('alfa', 'stock'):
        params, clean = load(antenna, source)
        count = 0
        for match in re.finditer(r'^assert\(', clean, re.M):
            start = match.end()
            depth, end = 1, start
            while depth:
                if clean[end] == '(':
                    depth += 1
                elif clean[end] == ')':
                    depth -= 1
                end += 1
            expression = split_top(clean[start:end-1], ',')[0]
            if '[for' in expression:
                continue  # Geometry-specific under-box assertion requires OpenSCAD.
            if not evaluate(expression, params):
                raise AssertionError(f'{antenna}: {expression}')
            count += 1
        print(f'{antenna}: {count} parameter assertions pass; conservative bounds '
              f'{params["width"]:.2f} x {params["length"]:.2f} mm; '
              f'foot web {params["floor_t"]-params["recess"]:.2f} mm; '
              f'stud protrusion {params["stud_protrusion"]:.2f} mm')
        if antenna == 'alfa':
            print(f'  bore {params["sma_d"]:.3f}; roof {params["fin_wall"]:.2f} mm')
    # Delimiter sanity only: does not claim OpenSCAD syntax/CSG validation.
    for path in (Path(source), Path(source).parent / 'p1-node-model.scad'):
        text = re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"', '', path.read_text(), flags=re.S)
        stack = []
        for char in text:
            if char in '([{':
                stack.append(char)
            elif char in ')]}':
                assert stack and stack.pop() == {')':'(', ']':'[', '}':'{'}[char], path
        assert not stack, path
    print('Source delimiters balanced. CSG, supports and physical fit are NOT validated.')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=SOURCE)
    main(parser.parse_args().source)
