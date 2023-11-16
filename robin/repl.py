from threading import Thread
from os import path
import traceback
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

from .pulse import Tone, Chirp, Noise, Pulse
from .config import BASE_PATH
from .util import handle_close


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
                    if isinstance(result, Pulse):
                        print(result)
                        on_trigger_pulse(result)
            except KeyboardInterrupt:
                break
            except:
                traceback.print_exc()
                continue
        exit_event.set()

    repl_thread = Thread(target=repl_inner)
    repl_thread.daemon = True
    repl_thread.start()
