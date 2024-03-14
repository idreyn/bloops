from threading import Thread
from os import path
import sys
import traceback
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

from .echolocation.pulse import *  # noqa: F403
from .constants import BASE_PATH


def run_repl(on_trigger_pulse, profile, exit_event):
    def repl_inner():
        session = PromptSession(
            history=FileHistory(path.join(BASE_PATH, ".robin_repl_history"))
        )
        user_namespace = {"profile": profile}
        while True:
            try:
                next_input = session.prompt("(  •͈ )> ")
                if next_input.strip() in ["exit", "quit"]:
                    break
                else:
                    try:
                        result = eval(next_input, None, user_namespace)
                    except Exception:
                        result = exec(next_input, None, user_namespace)
                    if isinstance(result, Pulse):  # noqa: F405
                        print(result)
                        on_trigger_pulse(result)
            except KeyboardInterrupt:
                break
            except:  # noqa: E722
                traceback.print_exc()
                continue
        exit_event.set()

    if sys.stdin and sys.stdin.isatty():
        repl_thread = Thread(target=repl_inner, daemon=True)
        repl_thread.start()
