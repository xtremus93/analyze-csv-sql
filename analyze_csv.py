import sys
import os
import re
import pandas as pd

DATE_PATTERN = re.compile(r'^(0?[1-9]|1[0-2])/(0?[1-9]|[12]\d|3[01])/\d{4}$')
INT_PATTERN = re.compile(r'^-?\d+$')
FLOAT_PATTERN = re.compile(r'^-?\d+\.\d+$')


def normalize_column_name(name):
    name = name.strip()
    name = re.sub(r'[^a-zA-Z0-9]+', '_', name)
    name = re.sub(r'_+', '_', name)
    name = name.strip('_')
    return name.lower()


def deduplicate_names(names):
    seen = {}
    result = []
    for name in names:
        if name not in seen:
            seen[name] = 1
            result.append(name)
        else:
            new_name = f'{name}_{seen[name]}'
            seen[name] += 1
            seen[new_name] = 1
            result.append(new_name)
    return result


def round_up_to_50(n):
    if n <= 50:
        return 50
    return ((n + 49) // 50) * 50


def is_int(v):
    return bool(INT_PATTERN.match(str(v).strip()))


def is_float(v):
    return bool(FLOAT_PATTERN.match(str(v).strip()))


def is_numeric(v):
    return is_int(v) or is_float(v)


def resolve_type(series):
    non_null = series.dropna()
    non_null = non_null[non_null != '']

    if non_null.empty:
        return 'VARCHAR(50)', None

    if non_null.apply(lambda v: bool(DATE_PATTERN.match(str(v).strip()))).all():
        return 'DATE', None

    if non_null.apply(is_int).all():
        return 'INT', None

    if non_null.apply(is_numeric).all():
        return 'FLOAT', None

    max_len = series.fillna('').astype(str).map(len).max()
    varchar_size = round_up_to_50(int(max_len))
    return f'VARCHAR({varchar_size})', int(max_len)


def is_nullable(series):
    return series.isnull().any() or (series == '').any()


def main():
    if len(sys.argv) < 2:
        sys.exit('Usage: python analyze_csv.py <csv_file>')

    csv_path = sys.argv[1]
    table_name = normalize_column_name(os.path.splitext(os.path.basename(csv_path))[0])

    df = pd.read_csv(csv_path, dtype=str, keep_default_na=True, encoding='utf-8-sig')

    zero_rows = len(df) == 0

    normalized_names = deduplicate_names([normalize_column_name(col) for col in df.columns])

    column_defs = []
    summary_lines = []

    for col, normalized in zip(df.columns, normalized_names):
        if zero_rows:
            sql_type = 'VARCHAR(50)'
            max_len_display = 'N/A'
            nullable = False
        else:
            sql_type, raw_max = resolve_type(df[col])
            nullable = is_nullable(df[col])
            max_len_display = str(raw_max) if raw_max is not None else 'N/A'

        null_str = 'NULL' if nullable else 'NOT NULL'
        nullable_display = 'Yes' if nullable else 'No'

        summary_lines.append(
            f'Column: {col!r} -> [{normalized}] | Type: {sql_type} | Nullable: {nullable_display} | Max Length: {max_len_display}'
        )
        column_defs.append(f'    [{normalized}] {sql_type} {null_str}')

    for line in summary_lines:
        print(line)

    print()
    print('-- SQL Server CREATE TABLE:')
    print(f'CREATE TABLE [{table_name}] (')
    print(',\n'.join(column_defs))
    print(');')


if __name__ == '__main__':
    main()
