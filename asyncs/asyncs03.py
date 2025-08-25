import asyncio
import aiohttp
import aiofile
import json
from pathlib import Path
from json.decoder import JSONDecodeError

class BaseFetcher:
    ROOT_URL = "https://pokeapi.co/api/v2"
    ROOT_JSON_DIR = Path(__file__).parent.resolve() / "json"
    TIMEOUT = 10

    def __init__(self):
        pass

    def try_decode_json(self, res, display_url: str):
        try:
            data = res.json()
        except JSONDecodeError:
            logger.error(f"{display_url}のJSONのデコードに失敗。")
            return

    def extract_idx_in_url(self, url: str) -> str:
        idx_str = url.strip("/").split("/")[0]
        return idx_str

    def extract_ep_name_in_url(self, url: str) -> str:
        ep_name = url.strip("/").split("/")[-1]
        return ep_name

class BaseAsyncFetcher(BaseFetcher):
    SEMAPHORE = 50

    def __init__(self, )

class DetailFetcher(BaseFetch):

    def __init__(self, ep_name: str, ep_ids: list[str]) -> None:
        self.ep_name = ep_name
        self.ep_ids = ep_ids

    async def fetch_single_json(
        self,
        fetch_url: str,
        session: aiohttp.ClientSession,
        semaphore: asyncio.Semaphore,
        timeout: int = TIMEOUT
    ) -> Optional[dict]:
        display_url = fetch_url.strip(ROOT_URL)
        async with semaphore:
            try:
                async with session.get(fetch_url, timeout=timeout) as res:
                    if res.status_code != 200:
                        logger.error(f"{display_url}でのステータスコードに異常があります: {res.status_code}")
                        return
                    res = await res
            except Exception as e:
                logger.error(f"{display_url}へのリクエストが失敗: {e}")
                return
        data = self.try_decode_json(res)
        return data

    async def write_data_for_json(self) -> None:

    def setup_unique_dir(self, ep_name: str, prefix: str) -> Path:
        unique_dir_name = f"{prefix}_{ep_name}"
        unique_dir_path = ROOT_JSON_DIR / dirname
        unique_dir_path.mkdir(exist_ok=True)
        return unique_dir_path

    async def process_single_json(self, url):
        ep_name = self.extract_ep_name_in_url(url)

        idx_str = self.extract_idx_in_url(url)



    def setup_fetch_urls(
        self,
        ep_name: str,
        ep_ids: list[int]
    ):
    fetch_urls = [f"{ROOR_URL}/{ep_name}/{ep_id}" for ep_id in ep_ids]
    return fetch_urls
