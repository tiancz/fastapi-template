import os
from typing import Generator, Optional
from fastapi.responses import StreamingResponse
import aiofiles


class LocalStorage:
    """FastAPI implementation for local storage."""

    def __init__(self, storage_path: Optional[str] = None):
        # 从环境变量或默认值获取存储路径
        self.folder = storage_path or os.environ.get("STORAGE_LOCAL_PATH", "storage")

        # 确保路径是绝对路径
        if not os.path.isabs(self.folder):
            self.folder = os.path.join(os.getcwd(), self.folder)

        # 确保存储目录存在
        os.makedirs(self.folder, exist_ok=True)
        print(f"Storage initialized at: {self.folder}")

    def _get_full_path(self, filename: str) -> str:
        """获取文件的完整路径（安全处理路径）"""
        # 移除可能的前导斜杠和防止路径遍历攻击
        filename = filename.lstrip('/')
        filename = os.path.normpath(filename)

        # 确保文件名在存储目录内
        full_path = os.path.join(self.folder, filename)
        if not full_path.startswith(self.folder):
            raise ValueError("Invalid filename: path traversal detected")

        return full_path

    async def save(self, filename: str, data: bytes) -> str:
        """异步保存文件到本地存储"""
        full_path = self._get_full_path(filename)

        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # 异步写入文件
        async with aiofiles.open(full_path, "wb") as f:
            await f.write(data)

        return full_path

    async def save_upload_file(self, filename: str, contents) -> str:
        """保存上传的文件"""
        full_path = self._get_full_path(filename)
        # 创建目录
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # 上传文件内容并保存
        async with aiofiles.open(full_path, "wb") as f:
            await f.write(contents)
        print(f"File saved: {full_path}")
        return full_path

    async def load_once(self, filename: str) -> bytes:
        """异步一次性加载整个文件内容"""
        full_path = self._get_full_path(filename)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {filename}")

        async with aiofiles.open(full_path, "rb") as f:
            return await f.read()

    async def load_stream(self, filename: str, chunk_size: int = 8192) -> Generator[bytes, None, None]:
        """异步流式加载文件内容"""
        full_path = self._get_full_path(filename)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {filename}")

        async with aiofiles.open(full_path, "rb") as f:
            while chunk := await f.read(chunk_size):
                yield chunk

    def get_streaming_response(self, filename: str,
                               content_type: str = "application/octet-stream") -> StreamingResponse:
        """获取 FastAPI 流式响应"""
        full_path = self._get_full_path(filename)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {filename}")

        def file_generator():
            with open(full_path, "rb") as f:
                while chunk := f.read(8192):
                    yield chunk

        return StreamingResponse(
            file_generator(),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={os.path.basename(filename)}"}
        )

    async def download(self, filename: str, target_filepath: str) -> str:
        """异步下载文件到指定路径"""
        full_path = self._get_full_path(filename)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {filename}")

        # 确保目标目录存在
        os.makedirs(os.path.dirname(target_filepath), exist_ok=True)

        # 异步复制文件
        async with aiofiles.open(full_path, "rb") as src:
            async with aiofiles.open(target_filepath, "wb") as dst:
                while chunk := await src.read(8192):
                    await dst.write(chunk)

        return target_filepath

    def exists(self, filename: str) -> bool:
        """检查文件是否存在"""
        full_path = self._get_full_path(filename)
        return os.path.exists(full_path)

    async def delete(self, filename: str) -> bool:
        """异步删除文件"""
        full_path = self._get_full_path(filename)

        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False

    def list_files(self, prefix: str = "") -> list[str]:
        """列出指定前缀的文件"""
        prefix_path = self._get_full_path(prefix)
        files = []

        for root, _, filenames in os.walk(prefix_path):
            for filename in filenames:
                full_path = os.path.join(root, filename)
                # 转换为相对路径
                rel_path = os.path.relpath(full_path, self.folder)
                files.append(rel_path)

        return files

    def get_size(self, filename: str) -> int:
        """获取文件大小"""
        full_path = self._get_full_path(filename)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {filename}")

        return os.path.getsize(full_path)


# 依赖注入函数
def get_local_storage() -> LocalStorage:
    """获取本地存储实例的依赖函数"""
    return LocalStorage()

