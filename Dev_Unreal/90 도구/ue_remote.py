# -*- coding: utf-8 -*-
"""Runs Python or console commands inside an editor that is already open.

The editor has to have remote execution on. The project turns it on in
Config/DefaultEngine.ini, so any editor started after that listens.

    python ue_remote.py --cmd "r.ScreenPercentage 100"
    python ue_remote.py --py "print(unreal.SystemLibrary.get_project_directory())"
    python ue_remote.py --file some_script.py
    python ue_remote.py --list
"""

import argparse
import sys
import time

ENGINE_PYTHON = r"C:\Program Files\Epic Games\UE_5.7\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python"
PROJECT_NAME = "RollBall"

sys.path.insert(0, ENGINE_PYTHON)
import remote_execution as rex


def connect(wait_seconds):
    remote = rex.RemoteExecution(rex.RemoteExecutionConfig())
    remote.start()

    node = None
    deadline = time.time() + wait_seconds
    while time.time() < deadline and node is None:
        for candidate in remote.remote_nodes:
            if candidate.get("project_name") == PROJECT_NAME:
                node = candidate
                break
        time.sleep(0.2)

    return remote, node


def run(remote, node, code, as_statement):
    remote.open_command_connection(node["node_id"])
    try:
        mode = rex.MODE_EXEC_STATEMENT if as_statement else rex.MODE_EXEC_FILE
        result = remote.run_command(code, unattended=True, exec_mode=mode)
    finally:
        remote.close_command_connection()
    return result


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--cmd", help="console command")
    group.add_argument("--py", help="python statement")
    group.add_argument("--file", help="python file to run")
    group.add_argument("--list", action="store_true", help="list editors that answer")
    parser.add_argument("--wait", type=float, default=4.0)
    args = parser.parse_args()

    remote, node = connect(args.wait)

    try:
        if args.list:
            for candidate in remote.remote_nodes:
                print(candidate.get("project_name"), candidate.get("node_id"))
            return 0

        if node is None:
            print("켜진 에디터를 못 찾았다. 원격 실행이 켜진 채로 열렸는지 본다.")
            return 1

        if args.cmd is not None:
            code = "import unreal\nunreal.SystemLibrary.execute_console_command(None, %r)" % args.cmd
            result = run(remote, node, code, as_statement=False)
        elif args.py is not None:
            result = run(remote, node, "import unreal\n" + args.py, as_statement=False)
        else:
            with open(args.file, encoding="utf-8") as handle:
                result = run(remote, node, handle.read(), as_statement=False)

        for line in result.get("output", []):
            print(line.get("output", "").rstrip())

        if not result.get("success", False):
            print("실패:", result.get("result"))
            return 1

        return 0
    finally:
        remote.stop()


if __name__ == "__main__":
    sys.exit(main())
