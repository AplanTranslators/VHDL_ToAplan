import argparse

from tool.tool import VHDL2AplanTool


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This program is a translation examples test.\nAuthors:  \n1. Vlad Dubina (https://github.com/vladyslav-dubina)"
    )

    parser.add_argument(
        "-e_path",
        metavar="",
        help="Path to system verilog examples list file",
        nargs="?",
    )

    args = parser.parse_args()
    tool = VHDL2AplanTool()

    tool.tests_start(args.e_path)
