import asyncio
import json
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Any

import requests
from tenacity import (retry, retry_if_exception_type, stop_after_attempt,
                      wait_fixed)

from logs.logs01 import get_logger

logger = get_logger(__name__)


class EpsGetter:
    def __init__(self, url: str) -> None:
        self.initial_url = url
        self.data = None

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def request_for_ep(self) -> Any:
        logger.info(f"{self.initial_url}にリクエストを送信します。")
        res = requests.get(self.initial_url)
        if res.status_code != 200:
            logger.error(f"ステータスコードに異常があります: {res.status_code}")
            raise ValueError(f"ステータスコードに異常があります: {res.status_code}")
        try:
            data = res.json()
        except JSONDecodeError:
            logger.error("JSONのデコードに失敗しました: %s", e)
            raise
        logger.info("JSONの取得とデコードに成功しました。")
        self.data = data
        return data

    def setup_dir_and_file(self) -> tuple[Path, Path]:
        dir_path = Path(__file__).resolve().parent / "json"
        try:
            dir_path.mkdir(exist_ok=True)  # ← typo修正
            logger.info(f"{dir_path}の作成に成功しました。")
        except (OSError, TypeError) as e:
            logger.error(f"{dir_path}の作成に失敗しました。: %s", e)
            raise RuntimeError

        file_path = dir_path / "endpoints.json"
        return dir_path, file_path

    def write_json(self) -> None:
        dir_path, file_path = self.setup_dir_and_file()  # ← () を付けて呼び出し
        try:
            with open(file_path, "w", encoding="utf-8") as f:  # ← file_path に修正
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except (OSError, TypeError) as e:
            logger.error("JSONの書き込みに失敗しました: %s", e)
            raise RuntimeError(f"JSONの書き込みに失敗しました: {e}")
        logger.info(f"JSONの書き込みに成功しました。")


def run() -> None:
    initial_url = "https://pokeapi.co/api/v2/"
    ep_getter = EndpointsGetter(initial_url)  # ← クラス名修正
    ep_getter.request_for_ep()
    ep_getter.write_json()


def main() -> None:
    logger.info("プログラムを開始します。")
    run()
    logger.info("プログラムが終了しました。")


if __name__ == "__main__":
    main()
