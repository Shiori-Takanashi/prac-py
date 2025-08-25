import random
import time
from functools import wraps

from logs.logs01 import get_logger  # 自作ロガーを想定

log = get_logger()


# --- デコレータ定義 ---
def log_task(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        log.info(f"{func.__name__} 開始")
        try:
            result = func(*args, **kwargs)
            log.info(f"{func.__name__} 成功")
            return result
        except Exception as e:
            log.error(f"{func.__name__} 失敗: {e}")
            raise
        finally:
            log.debug(f"{func.__name__} 終了")

    return wrapper


# --- ダミー処理 ---
@log_task
def dummy_process():
    time.sleep(random.uniform(0.5, 1.0))

    # ランダムで例外発生
    if random.random() < 0.3:
        raise RuntimeError("疑似エラー")

    return "OK"


def main() -> None:
    log.info("処理開始")
    for _ in range(5):
        try:
            dummy_process()
        except Exception:
            pass  # 失敗は握りつぶす（動作確認用）
    log.info("全タスク完了")


if __name__ == "__main__":
    main()
