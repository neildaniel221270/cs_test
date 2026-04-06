from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Generator, Iterable, List, Optional, Union

from gpt4all import GPT4All

# Optional embeddings support
try:
    from gpt4all import Embed4All  # type: ignore
    HAS_EMBED = True
except Exception:
    Embed4All = None  # type: ignore
    HAS_EMBED = False


DEFAULT_MODEL = "Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf"
DEFAULT_MODEL_DIR = "./models/llm"


class LocalLLM:
    """
    Small wrapper around GPT4All for:
    - loading a model by official model name or local .gguf path
    - one-shot generation
    - streaming generation
    - stateful chat sessions
    - optional embeddings
    """

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        model_dir: Optional[str] = DEFAULT_MODEL_DIR,
        device: str = "cpu",
        n_threads: Optional[int] = None,
        allow_download: bool = True,
    ) -> None:
        self.model_input = model
        self.model_dir = model_dir
        self.device = device
        self.n_threads = n_threads
        self.allow_download = allow_download

        model_name, model_path = self._resolve_model_input(model, model_dir)

        self._llm = GPT4All(
            model_name,
            model_path=model_path,
            allow_download=allow_download,
            device=device,
            n_threads=n_threads,
        )

        self._embedder = Embed4All() if HAS_EMBED else None

    def __enter__(self) -> "LocalLLM":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    @staticmethod
    def _resolve_model_input(model: str, model_dir: Optional[str]) -> tuple[str, Optional[str]]:
        """
        Convert input into (model_name, model_path) for GPT4All.

        Supported inputs:
        - official model name, e.g. "Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf"
        - absolute path to a local .gguf file
        - relative path to a local .gguf file
        """
        path = Path(model)

        # If the user passed a real local file, split into filename + parent dir
        if path.exists() and path.is_file():
            return path.name, str(path.parent)

        # If it looks like a path but does not exist, fail clearly
        if any(sep in model for sep in ("/", "\\")) and model.endswith(".gguf"):
            raise FileNotFoundError(f"Local model file not found: {model}")

        # Otherwise treat it as an official GPT4All model name
        return model, model_dir

    # ---------- Text generation ----------

    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.4,
        top_k: int = 40,
        min_p: float = 0.0,
        repeat_penalty: float = 1.18,
    ) -> str:
        return self._llm.generate(
            prompt,
            max_tokens=max_tokens,
            temp=temperature,
            top_p=top_p,
            top_k=top_k,
            min_p=min_p,
            repeat_penalty=repeat_penalty,
        )

    def stream(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.4,
        top_k: int = 40,
        min_p: float = 0.0,
        repeat_penalty: float = 1.18,
    ) -> Generator[str, None, None]:
        for token in self._llm.generate(
            prompt,
            max_tokens=max_tokens,
            temp=temperature,
            top_p=top_p,
            top_k=top_k,
            min_p=min_p,
            repeat_penalty=repeat_penalty,
            streaming=True,
        ):
            yield token

    # ---------- Chat helpers ----------

    def chat(
        self,
        turns: Iterable[str],
        max_tokens: int = 512,
        system_message: Optional[str] = None,
        chat_template: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 0.4,
        top_k: int = 40,
        min_p: float = 0.0,
        repeat_penalty: float = 1.18,
    ) -> List[str]:
        replies: List[str] = []

        session_kwargs = {}
        if system_message is not None:
            session_kwargs["system_message"] = system_message
        if chat_template is not None:
            session_kwargs["chat_template"] = chat_template

        with self._llm.chat_session(**session_kwargs):
            for user_msg in turns:
                reply = self._llm.generate(
                    user_msg,
                    max_tokens=max_tokens,
                    temp=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    min_p=min_p,
                    repeat_penalty=repeat_penalty,
                )
                replies.append(reply)

        return replies

    def interactive_chat(
        self,
        max_tokens: int = 512,
        stream: bool = True,
        system_message: Optional[str] = None,
        chat_template: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 0.4,
        top_k: int = 40,
        min_p: float = 0.0,
        repeat_penalty: float = 1.18,
    ) -> None:
        session_kwargs = {}
        if system_message is not None:
            session_kwargs["system_message"] = system_message
        if chat_template is not None:
            session_kwargs["chat_template"] = chat_template

        print("Local chat started. Type 'exit' or 'quit' to stop.\n")

        try:
            with self._llm.chat_session(**session_kwargs):
                while True:
                    try:
                        user_input = input("You: ").strip()
                    except EOFError:
                        print("\nGoodbye!")
                        break

                    if not user_input:
                        continue

                    if user_input.lower() in {"exit", "quit"}:
                        print("Goodbye!")
                        break

                    print("Assistant: ", end="", flush=True)

                    if stream:
                        for tok in self._llm.generate(
                            user_input,
                            max_tokens=max_tokens,
                            temp=temperature,
                            top_p=top_p,
                            top_k=top_k,
                            min_p=min_p,
                            repeat_penalty=repeat_penalty,
                            streaming=True,
                        ):
                            sys.stdout.write(tok)
                            sys.stdout.flush()
                        print()
                    else:
                        reply = self._llm.generate(
                            user_input,
                            max_tokens=max_tokens,
                            temp=temperature,
                            top_p=top_p,
                            top_k=top_k,
                            min_p=min_p,
                            repeat_penalty=repeat_penalty,
                        )
                        print(reply)
        except KeyboardInterrupt:
            print("\nGoodbye!")

    # ---------- Embeddings ----------

    def embed(self, texts: Union[str, List[str]]) -> List[List[float]]:
        if self._embedder is None:
            raise RuntimeError(
                "Embeddings are not available in this GPT4All installation. "
                "Try upgrading the gpt4all package."
            )

        if isinstance(texts, str):
            texts = [texts]

        return [self._embedder.embed(t) for t in texts]

    # ---------- Cleanup ----------

    def close(self) -> None:
        try:
            if self._embedder is not None:
                self._embedder.close()
        finally:
            self._llm.close()


def read_text_file_if_provided(path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    return Path(path).read_text(encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a local GPT4All model")

    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Model name or path to .gguf (default: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--model-dir",
        default=DEFAULT_MODEL_DIR,
        help=f"Directory for model cache/downloads (default: {DEFAULT_MODEL_DIR})"
    )
    parser.add_argument(
        "--device",
        default="cpu",
        help="cpu, gpu, cuda, kompute, amd, nvidia, or a specific device name"
    )
    parser.add_argument(
        "--prompt",
        help="Single prompt for one-shot generation"
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        help="Start interactive chat mode"
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Stream tokens to stdout"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=256,
        help="Maximum tokens to generate"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Sampling temperature"
    )
    parser.add_argument(
        "--top-p",
        type=float,
        default=0.4,
        help="Top-p sampling"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=40,
        help="Top-k sampling"
    )
    parser.add_argument(
        "--min-p",
        type=float,
        default=0.0,
        help="Min-p sampling"
    )
    parser.add_argument(
        "--repeat-penalty",
        type=float,
        default=1.18,
        help="Penalty for repetition"
    )
    parser.add_argument(
        "--n-threads",
        type=int,
        default=None,
        help="CPU threads to use (default: auto)"
    )
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="Disable model download"
    )
    parser.add_argument(
        "--system-message",
        default=None,
        help="Optional system message for chat mode"
    )
    parser.add_argument(
        "--chat-template-file",
        default=None,
        help="Path to a Jinja chat template file (useful for fully offline/sideloaded chat)"
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    chat_template = read_text_file_if_provided(args.chat_template_file)

    with LocalLLM(
        model=args.model,
        model_dir=args.model_dir,
        device=args.device,
        n_threads=args.n_threads,
        allow_download=not args.no_download,
    ) as llm:
        if args.chat:
            llm.interactive_chat(
                max_tokens=args.max_tokens,
                stream=args.stream,
                system_message=args.system_message,
                chat_template=chat_template,
                temperature=args.temperature,
                top_p=args.top_p,
                top_k=args.top_k,
                min_p=args.min_p,
                repeat_penalty=args.repeat_penalty,
            )
            return

        if args.prompt:
            if args.stream:
                for tok in llm.stream(
                    args.prompt,
                    max_tokens=args.max_tokens,
                    temperature=args.temperature,
                    top_p=args.top_p,
                    top_k=args.top_k,
                    min_p=args.min_p,
                    repeat_penalty=args.repeat_penalty,
                ):
                    sys.stdout.write(tok)
                    sys.stdout.flush()
                print()
            else:
                print(
                    llm.generate(
                        args.prompt,
                        max_tokens=args.max_tokens,
                        temperature=args.temperature,
                        top_p=args.top_p,
                        top_k=args.top_k,
                        min_p=args.min_p,
                        repeat_penalty=args.repeat_penalty,
                    )
                )
            return

        parser.error("Provide --prompt for one-shot mode or --chat for interactive mode.")


if __name__ == "__main__":
    main()

# python local_llm.py --chat --stream --no-download