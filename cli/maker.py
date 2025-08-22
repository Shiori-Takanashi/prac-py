from pathlib import Path
from functools import wraps
import click
from typing import Callable


def make_path(make_path: Callable) -> Callable:
    def wraps(*args, **kwargs):
        result = make_path(*args, **kwargs)
        target = Path(__file__).resolve().parent.parent
        total = result.get("total", None)
        name = result.get("name", None)
        dirpath = target / name
        if not dirpath.is_dir():
            try:
                dirpath.mkdir(parents=True, exist_ok=False)
            except FileExistsError:
                raise FileExistsError(f"Directory {dirpath.name} already exists.")
        if not target.is_dir():
            raise FileNotFoundError(f"Directory {target} does not exist.")
        if total is None:
            return
        if name is None:
            return
        latest_file_path = target / f"{name}{total:02d}.py"
        if latest_file_path.exists():
            return
        init = target / name / "__init__.py"
        if not init.exists():
            init.touch()
        for total in range(1, total + 1):
            file_path = target / name / f"{name}{total:02d}.py"
            file_path.touch()
        return result

    return wraps


@click.command()
@click.option("--total", type=int, required=True)
@click.option("--name", type=str, required=True)
@make_path
def enter_total_and_name(total: int, name: str):
    """
    totalとnameを入力させる。
    """
    return {"total": total, "name": name}


if __name__ == "__main__":
    enter_total_and_name()
