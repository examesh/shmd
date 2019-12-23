#!/usr/bin/env python3

# pylint:disable=C0111,C0103

from sys import argv as sys_argv, exit as sys_exit, stderr as sys_stderr
from os import environ as os_environ
from re import match as re_match
from pathlib import Path
from glob import glob


class Err(Exception):
    pass


def usage():
    stderr('')
    stderr('{} <src_dir> <dst_file> [<black_files>]'.format(sys_argv[0]))
    stderr('')
    stderr('  src_dir     = Source directory with shell files')
    stderr('  dst_file    = Destination (markdown) file')
    stderr('  black_files = Skip these comma separated src files')
    stderr('')
    stderr('  export $SHMD_PAT to match other source files than *.sh')
    stderr('')
    stderr('  Examples:')
    stderr('    {} ~/foo ~/api.md'.format(sys_argv[0]))
    stderr('    {} ~/foo ~/api.md cfg.sh,main.sh'.format(sys_argv[0]))
    stderr('    SHMD_PAT=\'*_*.sh\' {} ~/foo ~/api.md'.format(sys_argv[0]))
    stderr('')
    sys_exit(2)


def stderr(msg):
    print(msg, file=sys_stderr)


def get_arg(ix, optional=False):
    if len(sys_argv) < (ix + 1):
        if optional:
            return None
        usage()
    return sys_argv[ix]


def get_file_paths(dp, pat, blackFns):
    fps = []
    for fp in glob('{}/{}'.format(dp, pat)):
        fp = Path(fp)
        if fp.name not in blackFns:
            fps.append(fp)
    return sorted(fps)


def read_file(fp):
    fp = Path(fp)
    try:
        with open(fp, 'rt', encoding='utf-8') as f:
            return f.read().split('\n')
    except (OSError, IOError, PermissionError, FileNotFoundError) as e:
        raise Err('Reading {} failed: {}'.format(fp, e))


def write_file(fp, data):
    fp = Path(fp)
    try:
        with open(fp, 'wt', encoding='utf-8') as f:
            f.write(data)
    except (OSError, IOError, PermissionError, FileNotFoundError) as e:
        raise Err('Writing {} failed: {}'.format(fp, e))


def san(d, mode='full'):
    if mode == 'full':
        d = ' '.join(d.split()).strip()
    d.lstrip()
    d.rstrip()
    return d


def extract(fp):
    fcs = {}
    name = None
    for line in read_file(fp):
        if re_match(r'^\s*#', line) and not re_match(r'^\s*##[ACDE]\s+', line):
            continue
        if name:
            if re_match(r'^\s*}\s*$', line):
                fcs[name]['C'] = san(fcs[name].get('C', name))
                name = None
                continue
            mtch = re_match(r'^\s*##C\s+(.+)$', line)
            if mtch:
                fcs[name]['C'] = '{} {}'.format(name, mtch.group(1))
                continue
            mtch = re_match(r'^\s*##(A|D|E)\s+(.+)$', line)
            if mtch:
                typ = mtch.group(1)
                msg = mtch.group(2)
                if typ == 'A':
                    mtch = re_match(r'^(.+?)=(.+)$', msg)
                    arg = san(mtch.group(1))
                    msg = san(mtch.group(2))
                    fcs[name].setdefault(typ, {})[arg] = msg
                elif typ == 'D':
                    fcs[name].setdefault(typ, []).append(san(msg))
                else:  # E
                    fcs[name].setdefault(typ, []).append(san(msg, 'simple'))
                continue
        else:
            mtch = re_match(r'^(\w+)\(\)\s+{\s*$', line)
            if mtch:
                name = mtch.group(1)
                fcs[name] = {}
    return fcs


def write_markdown(fcs, fp):
    lines = []
    for name in sorted(fcs):
        lines.append(f'- [`{name}`](#{name})')
    lines.append('\n***\n')
    for name in sorted(fcs):
        fc = fcs[name]
        lines.append('#### `{}`\n'.format(name))
        if fc.get('D'):
            lines.append('{}\n'.format(san(' '.join(fc['D']))))
        lines.append('**Usage**\n')
        lines.append('```shell\n{}\n```\n'.format(fc['C']))
        if fc.get('A'):
            lines.append('**Arguments**\n')
            for arg in fc['A']:
                lines.append('- {}\n    - {}'.format(arg, fc['A'][arg]))
            lines.append('')
        if fc.get('E'):
            lines.append('**Examples**\n')
            lines.append('```shell\n{}\n```\n'.format('\n'.join(fc['E'])))
    write_file(fp, '\n'.join(lines))


def main():
    srcDp = Path(get_arg(1))
    srcPat = os_environ.get('SHMD_PAT', '*.sh')
    dstFp = Path(get_arg(2))
    blackFns = get_arg(3, True)
    blackFns = blackFns.split(',') if blackFns else []
    fps = get_file_paths(srcDp, srcPat, blackFns)
    if not fps:
        raise Err('No "{}" files found in {}'.format(srcPat, srcDp))
    fcs = {}
    for fp in fps:
        stderr('Processing {}'.format(fp))
        fcs_ = extract(fp)
        stderr('{} functions found'.format(len(fcs_)))
        fcs.update(fcs_)
    stderr('Writing {} with {} functions'.format(dstFp, len(fcs)))
    write_markdown(fcs, dstFp)


try:
    main()
except Err as e:
    stderr('ERROR: {}'.format(e))
    sys_exit(1)
