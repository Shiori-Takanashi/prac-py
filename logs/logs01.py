# log/log01.py
import logging

_log_counter = 0


class NumberedFormatter(logging.Formatter):
    """各ログに通し番号 log_id を付与。str.format スタイルを使用。"""

    def __init__(self, fmt, datefmt=None):
        super().__init__(fmt=fmt, datefmt=datefmt, style="{")  # ← 重要: style='{'

    def format(self, record: logging.LogRecord) -> str:
        global _log_counter
        _log_counter += 1
        record.log_id = f"LOG{_log_counter:04d}"
        return super().format(record)


def get_logger(name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()  # インスタンス化を忘れない
        formatter = NumberedFormatter(
            "{asctime} | {levelname:^7} | {log_id} | {filename}:{lineno} | {funcName:^7} | {message}",
            datefmt="%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False  # ルートへ伝播させず二重出力を防止
    return logger
