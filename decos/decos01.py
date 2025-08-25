# wsl_path_ops.py
import logging
import shutil
import time
from functools import wraps
from pathlib import Path

# ログ整形（レベル幅を固定して縦を揃える）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-6s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def trace(func):
    """START/END を常に出す（例外でも END を出す）"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"L001: START: {func.__name__}")
        try:
            return func(*args, **kwargs)
        finally:
            logging.info(f"L002: END  : {func.__name__}")

    return wrapper


class WSLPathValidator:
    """
    WSL想定の構文検証:
      - POSIX 側: NUL 禁止, 総パス長(概ね 4096 bytes)と各要素長(概ね 255 bytes)をざっくり検査
      - /mnt/<drive>/ 配下(Windowsドライブ): Windows 禁止文字 <>:\"/\\|?*，末尾スペース/ドット禁止 を追加検査
    存在確認は含めない（exists()/is_file()/is_dir() で別途）
    """

    _WIN_INVALID = '<>:"\\|?*'
    _TOTAL_MAX = 4096
    _ELEM_MAX = 255

    def is_windows_mount(self, p: Path) -> bool:
        parts = p.as_posix().split("/")
        # 例: /mnt/c/Users/... → ["", "mnt", "c", "Users", ...]
        return len(parts) >= 3 and parts[1] == "mnt"

    def validate_syntax(self, p: Path) -> tuple[bool, str]:
        s = p.as_posix()
        if "\x00" in s:
            return False, "NUL 文字は不可"
        if len(s.encode()) > self._TOTAL_MAX:
            return False, "パス長が長すぎる"

        is_win = self.is_windows_mount(p)
        for part in p.parts:
            if part in ("/", "", "mnt"):  # ルートや /mnt はスキップ
                continue
            # Windows ドライブ名もスキップ（"c" 等）
            if is_win and len(part) == 1 and part.isalpha():
                continue

            if len(part.encode()) > self._ELEM_MAX:
                return False, f"要素 '{part}' が長すぎる"

            if is_win:
                if any(ch in part for ch in self._WIN_INVALID):
                    return False, f"Windows 禁止文字を含む: '{part}'"
                if part.endswith(" ") or part.endswith("."):
                    return False, f"Windows で末尾スペース/ドットは不可: '{part}'"

        return True, "OK"


def canonicalize(p: Path) -> Path:
    """存在の有無に関係なく、相対／.. を解消して絶対化する"""
    return p.resolve(strict=False)


def ensure_fresh_dir(d: Path) -> bool:
    """
    ディレクトリを「空で存在する」状態に整える。
    - ファイルがあればエラー
    - ディレクトリがあれば削除してから作り直す
    """
    if d.exists():
        if d.is_file():
            logging.error(f"L003: {d} はファイル。ディレクトリが必要。")
            return False
        logging.info(f"L004: {d} を削除して作り直す。")
        try:
            shutil.rmtree(d)
        except Exception as e:
            logging.error(f"L005: {d} の削除に失敗: {e}")
            return False
    try:
        d.mkdir(parents=True, exist_ok=False)
        logging.info(f"L006: {d} を作成。")
        return True
    except Exception as e:
        logging.error(f"L007: {d} の作成に失敗: {e}")
        return False


def ensure_file_absent(f: Path) -> bool:
    """
    ファイルを「存在しない」状態に整える。
    - ディレクトリがあればエラー
    - ファイルがあれば削除
    """
    if f.exists():
        if f.is_dir():
            logging.error(f"L008: {f} はディレクトリ。ファイルが必要。")
            return False
        try:
            f.unlink()
            logging.info(f"L009: {f} を削除。")
        except Exception as e:
            logging.error(f"L010: {f} の削除に失敗: {e}")
            return False
    return True


@trace
def make_and_remove_file(name: str, duration: int) -> None:
    """
    1) temp ディレクトリを空で作る
    2) その中に name ファイルを作成 → 待機 → 削除 → 再作成
    """
    validator = WSLPathValidator()

    # --- ディレクトリ ---
    dirpath = canonicalize(Path(__file__).parent.parent / "temp")
    ok, reason = validator.validate_syntax(dirpath)
    if not ok:
        logging.error(f"L011: ディレクトリパスが不正: {reason} [{dirpath}]")
        return

    if not ensure_fresh_dir(dirpath):
        return

    # --- ファイル ---
    filepath = canonicalize(dirpath / name)
    ok, reason = validator.validate_syntax(filepath)
    if not ok:
        logging.error(f"L012: ファイルパスが不正: {reason} [{filepath}]")
        return

    if not ensure_file_absent(filepath):
        return

    # 作成 → 待機 → 削除 → 再作成（挙動確認のため）
    try:
        filepath.touch()
        logging.info(f"L013: 作成: {filepath}")
        time.sleep(duration)

        filepath.unlink()
        logging.info(f"L014: 削除: {filepath}")
        time.sleep(duration)

        filepath.touch()
        logging.info(f"L015: 再作成: {filepath}")
    except Exception as e:
        logging.error(f"L016: ファイル操作に失敗: {e}")


if __name__ == "__main__":
    # 例: temp ディレクトリ内に 'sample.txt' を作って消してもう一度作る
    make_and_remove_file("sample.txt", 1)
