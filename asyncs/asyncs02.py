import asyncio
import json
from json.decoder import JSONDecodeError
from pathlib import Path

from typing import Optional

import requests

from logs.logs01 import get_logger

logger = get_logger(__name__)


class IdsGetter:
    root_path = Path(__file__).parent.resolve()
    json_dir_path = root_path / "json"
    eps_json_path = json_dir_path / "eps.json"

    def __init__(self) -> None:
        self._eps_data: Optional[dict[str, str]] = None
        self._ep_names: Optional[list[str]] = None
        self._ep_urls: Optional[list[str]] = None

    def load_eps_json(self, eps_json_path: Path = eps_json_path) -> None:
        try:
            with open(eps_json_path, "r", encoding="utf-8") as f:
                eps_data: dict = json.load(f)
        except FileNotFoundError as e:
            logger.error(f"ファイルが見つかりません: {eps_json_path} ({e})")
            raise
        except JSONDecodeError as e:
            logger.error(f"JSONの解析に失敗しました: {eps_json_path} ({e})")
            raise
        except OSError as e:
            logger.error(f"ファイル操作エラー: {eps_json_path} ({e})")
            raise

        self._eps_data = eps_data
        self._ep_names = list(eps_data.keys())
        self._ep_urls = list(eps_data.values())

    @property
    def eps_data(self) -> dict[str, str]:
        return self._eps_data

    @property
    def ep_names(self) -> list[str]:
        return self._ep_names

    @property
    def ep_urls(self) -> list[str]:
        return self._ep_urls

    def output_data(self, filename: str, data: list | dict, dir_path: Path = json_dir_path) -> None:
        if not data:
            msg = "書き出しのためのデータは空です。"
            logger.warning(msg)
            raise ValueError(msg)
        try:
            dir_path.mkdir(exist_ok=True)
            logger.debug("書き出しのためのディレクトリを作成しました。")
        except RuntimeError:
            logger.warning(f"{dir_path.name}ディレクトリの作成に失敗しました。")
            raise

        file_path = dir_path / filename
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.debug(f"データをJSONで保存しました。")
        except Exception as e:
            raise

    def request_json(self, target_url):
        try:
            res = requests.get(target_url)
            ep_data = res.json()
        except Exception as e:
            logger.error(f"エラー: {e}")
            return None, None
        results = ep_data.get("results", None)
        next_url = ep_data.get("next", None)
        return results, next_url

    def extract_ids_from_results(self, results: list[dict]) -> list[int]:
        urls = [result.get("url", None) for result in results]
        if not all(urls):
            logger.error(f"全てのURLが取得できませんでした。")
        try:
            ids = [url.split("/")[-2] for url in urls]
        except ValueError:
            logger.error(f"URLたちからidを抽出できません。")
            return
        return ids

    def get_all_ids_of_ep(self, ep_name: str) -> list[int]:
        if self._eps_data is None:
            raise ValueError("eps_data がロードされていません")

        ep_url = self._eps_data.get(ep_name, None)
        if not ep_url:
            raise ValueError(f"{ep_name} に対応するURLが見つかりません")

        offset = 0
        limit = 200
        next_url: str | None = None
        all_ids: list[int] = []

        while True:
            if next_url:
                target_url = next_url
            else:
                target_url = f"{ep_url}/?offset={offset}&limit={limit}"

            results, next_url = self.request_json(target_url)
            if results:
                extracted_ids = self.extract_ids_from_results(results)
                all_ids.extend(extracted_ids)

            if not next_url:
                break

        return all_ids


    def json_file_path(self, filename: str, json_dir_path: Path = json_dir_path) -> Path:
        json_dir_path.mkdir(exist_ok=True)
        filename = filename.replace("-", "_")
        json_file_path = json_dir_path / f"{filename}.json"
        return json_file_path


def run() -> None:
    ids_getter = IdsGetter()
    ids_getter.load_eps_json()

    results: list[str] = ids_getter.ep_names
    if not results:
        raise ValueError("endpoints.json にデータがありません")

    for target_ep_name in results:
        content = ids_getter.get_all_ids_of_ep(target_ep_name)
        if content:
            json_file_path = ids_getter.json_file_path(target_ep_name)
            ids_getter.output_data(json_file_path, content)


def main() -> None:
    logger.info("プログラム開始")
    run()
    logger.info("プログラム終了")


if __name__ == "__main__":
    main()
