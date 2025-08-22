# annotator.py
import re
import sys
from pathlib import Path

LEVELS = "info|error|warning|debug|critical"

# 例: 'L001: ' を検出（幅は3桁以上許容）
LABEL_RE = re.compile(r"^L\d{3,}:\s?")

# logging.<level>( まで + 可変の文字列プレフィックス + 開きクオート
# クオートは ' " ''' """ に対応（トリプルクオート可）
CALL_RE = re.compile(
    rf"(logging\.({LEVELS})\s*\(\s*)"  # g1: 'logging.info(' まで
    r"((?:[rR]?[fF]|[fF][rR]|[rR])?)"  # g2: 文字列プレフィックス（任意）
    r"(?P<q>'''|\"\"\"|'|\")"  # g3: 開きクオート
)


def annotate_text(code: str, start: int = 1) -> tuple[str, int]:
    """
    ソース全体を対象に、左→右へ走査しながら L番号を順に付与する。
    既存の 'Lddd:' が先頭にある文字列はスキップ。
    戻り値: (変換後テキスト, 付与件数)
    """
    count = start

    def repl(m: re.Match) -> str:
        nonlocal count, code
        insert_pos = m.end()  # クオート直後（文字列の先頭）
        # 既にラベルが付与済みなら何もしない
        if LABEL_RE.match(code[insert_pos:]):
            return m.group(0)
        label = f"L{count:03d}: "
        count += 1
        # g1 + g2 + クオート + ラベル を返し、後続はそのまま残る
        return f"{m.group(1)}{m.group(3)}{m.group('q')}{label}"

    new_code, n = CALL_RE.subn(repl, code)
    # subn の置換件数 n は「マッチ数」であり、ラベル既存スキップ分も含む。
    # 実際に付与した件数は (count - start)。
    return new_code, (count - start)


def main() -> None:
    if len(sys.argv) != 2:
        print("使い方: python log_annotator_min.py <python_file>")
        sys.exit(2)

    path = Path(sys.argv[1])
    if not path.is_file():
        print("ファイルが見つかりません。")
        sys.exit(2)

    src = path.read_text(encoding="utf-8")
    new_src, added = annotate_text(src, start=1)

    if added == 0:
        print("付与対象なし（既にラベル済みか、対象外の呼び出しのみ）。")
        return

    path.write_text(new_src, encoding="utf-8")
    print(f"{added} 件 付与しました: {path}")


if __name__ == "__main__":
    main()
