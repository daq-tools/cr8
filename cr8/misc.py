
from collections import defaultdict


def parse_table(fq_table):
    """ parses a tablename and returns a (<schema>, <table>) tuple

    schema defaults to doc if the table name doesn't contain a schema

    >>> parse_table('x.users')
    ('x', 'users')

    >>> parse_table('users')
    ('doc', 'users')
    """

    parts = fq_table.split('.')
    if len(parts) == 1:
        return 'doc', parts[0]
    elif len(parts) == 2:
        return parts[0], parts[1]
    else:
        raise ValueError


def as_bulk_queries(queries, bulk_size):
    """ groups a iterable of (stmt, args) by stmt into (stmt, bulk_args)

    bulk_args will be a list of the args grouped by stmt.

    len(bulk_args) will be <= bulk_size
    """
    stmt_dict = defaultdict(list)
    for stmt, args in queries:
        bulk_args = stmt_dict[stmt]
        bulk_args.append(args)
        if len(bulk_args) == bulk_size:
            yield stmt, bulk_args
            del stmt_dict[stmt]
    for stmt, bulk_args in stmt_dict.items():
        yield stmt, bulk_args


def get_lines(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            yield line


def as_statements(lines):
    """ generator expression that transforms lines into strings of sql statements

    statements within the lines must end with ";"

    >>> list(as_statements(['select * from', '-- comments are filtered', 't;']))
    ['select * from t']

    >>> list(as_statements(['a;', 'b', 'c;', 'd']))
    ['a', 'b c']
    """
    lines = (l.strip() for l in lines if l)
    lines = (l for l in lines if not l.startswith('--'))
    parts = []
    for line in lines:
        parts.append(line.rstrip(';'))
        if line.endswith(';'):
            yield ' '.join(parts)
            parts.clear()
