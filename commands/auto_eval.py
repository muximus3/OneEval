import os
import sys
import argparse
from oneapi import OneAPITool
sys.path.append(os.path.normpath(f"{os.path.dirname(os.path.abspath(__file__))}/.."))
from eval import eval_one_file, eval_one, EvalConfig 
import prompt_template
    
def add_shared_arguments(parser):
    parser.add_argument("-c", "--config_file", type=str, help="config file path", required=True)
    parser.add_argument("-tp", "--template_path", type=str, default=None, help="eval prompt template path", required=False)
    parser.add_argument("-v", "--verbose", type=bool, default=True, help="print every prompt and response detail", required=False)
    parser.add_argument("-m", "--model", type=str, default="", help="evaluate model name, e.g., gpt-35-turbo, gpt-4", required=False)
    parser.add_argument("-te", "--temperature", type=float, default=0.1, help="0-1, higher temperature more random result", required=False)
    parser.add_argument("-mnt", "--max_new_tokens", type=int, default=2048, help="max output token length", required=False)


def main():
    parser = argparse.ArgumentParser(description="auto-eval <command> [<args>]")
    subparsers = parser.add_subparsers(dest="command")

    # auto-eval line
    line_parser = subparsers.add_parser("line", help="auto-eval line [<args>]")
    add_shared_arguments(line_parser)
    line_parser.add_argument("-p", "--prompt", type=str, help="question", required=True)
    line_parser.add_argument("-a", "--answers", nargs='+', help="candidate answers", required=True)
    line_parser.add_argument("-ta", "--target", type=str, default="", help="standard answer", required=False)

    # auto-eval file
    file_parser = subparsers.add_parser("file", help="auto-eval file [<args>]")
    add_shared_arguments(file_parser)
    file_parser.add_argument("-edp", "--eval_data_path", type=str, help="", required=True)
    file_parser.add_argument("-op", "--output_path", type=str, default="", help="", required=False)
    file_parser.add_argument("-ec", "--eval_categories", default=None, nargs="+", help="only evaluate chosen categories", required=False)
    file_parser.add_argument("-sn", "--sample_num", type=int, default=0, help="", required=False)
    file_parser.add_argument("-i", "--interval", type=int, default=1, help="request interval, gpt-4 need longer interval, e.g.,10s", required=False)
    file_parser.add_argument("-r", "--retry", type=bool, default=True, help="", required=False)

    args = parser.parse_args()
    if not args.template_path:
        template_path =  os.path.join(os.path.dirname(prompt_template.__file__), 'eval_prompt_template.json')
    else:
        template_path = args.template_path
    eval_prompter = prompt_template.EvalPrompt.from_config(template_path, verbose=args.verbose)

    if args.command == "line":
        tool = OneAPITool.from_config_file(args.config_file)
        score, raw_response = eval_one(
            eval_prompter=eval_prompter,
            question=args.prompt, 
            candidate_answers=args.answers, 
            target=args.target,
            api_tool=tool,
            model=args.model,
            temperature=args.temperature,
            max_new_tokens=args.max_new_tokens,
            )
        print(f'\nSCORE:\n{score}')

    elif args.command == "file":
        eval_one_file(
            EvalConfig(
            eval_prompter=eval_prompter,
            api_config_file=args.config_file, 
            eval_data_path=args.eval_data_path, 
            output_path=args.output_path, 
            model=args.model,
            eval_categories=args.eval_categories,
            sample_num=args.sample_num, 
            request_interval=args.interval,
            retry=args.retry,
            temperature=args.temperature,
            max_new_tokens=args.max_new_tokens,
            ))

if __name__ == "__main__":
    main()