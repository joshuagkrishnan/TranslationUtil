import argparse
import json
import os
from main.diff_checker import DiffChecker
from main.diff_merge import DiffMerge

if __name__ == '__main__':
    action = None
    arg_parser = argparse.ArgumentParser()
    sub_parser = arg_parser.add_subparsers(dest='command')
    diff_parser = sub_parser.add_parser('diff')
    merge_parser = sub_parser.add_parser('merge')
    arg_parser.add_argument('--dry_run', default=0, type=int, choices=(0, 1), required=False)
    arg_parser.add_argument('--clear_file_cache', default=0, type=int, choices=(0,1), required=False)
    merge_parser.add_argument('--overwrite', default=0, type=int, choices=(0,1))
    merge_parser.add_argument('--output', default='', required=False)
    merge_parser.add_argument('--file_list', default=[], nargs=1, required=False, )
    merge_parser.add_argument('--path_list', nargs='+', default=[], required=False)
    diff_parser.add_argument('--path_list', nargs='+', default=[], required=False)
    diff_parser.add_argument('--pri_lang', default='')
    diff_parser.add_argument('--sec_lang', default='')
    diff_parser.add_argument('--file_list', default=[], nargs=1, required=False, )
    diff_parser.add_argument('--output', default='', required=False)
    diff_parser.add_argument('--sanitize', default=0, type=int, choices=(0,1))
    args, _ = arg_parser.parse_known_args()
    os.environ['clear_file_cache'] = '1'
    action = args.command
    if action == 'diff':
        if not args.file_list:
            diff_parser.add_argument('--source', required=True)
            diff_parser.add_argument('--dest', required=True)
            diff_args, _ = diff_parser.parse_known_args()
            DiffChecker(
                diff_args.source, diff_args.dest, args.path_list, sanitize=args.sanitize
            ).get_line_diff(pri_lang=args.pri_lang, sec_lang=args.sec_lang)
        else:
            data = json.loads(args.file_list[0])
            for rec in data:
                DiffChecker(
                    rec['source'], rec['dest'],
                    args.path_list,
                    sanitize = args.sanitize
                ).get_line_diff(pri_lang=args.pri_lang, sec_lang=args.sec_lang)
    elif action == 'merge':
        kwargs = dict(
            overwrite=args.overwrite == 1,
            output_file=args.output,
            dry_run=args.dry_run,
            path_list=args.path_list
        )
        if not args.file_list:
            merge_parser.add_argument('--source', required=True)
            merge_parser.add_argument('--dest', required=True)
            merge_args, _ = merge_parser.parse_known_args()
            DiffMerge(merge_args.source, merge_args.dest, **kwargs).merge()
        else:
            data = json.loads(args.file_list[0])
            for rec in data:
                if args.dry_run: rec['dry_run'] = True
                if args.path_list: rec['path_list'] = args.path_list
                print('Merging file file {source} with {dest}'.format(**rec))
                DiffMerge(**rec).merge()
