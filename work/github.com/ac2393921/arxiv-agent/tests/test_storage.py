"""Storage モジュールのテスト"""
import json
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from src.storage import Storage


@pytest.fixture
def temp_storage_file():
    """一時的なストレージファイルを作成"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = f.name
    yield temp_path
    # クリーンアップ
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def storage(temp_storage_file):
    """Storage インスタンスを作成"""
    return Storage(temp_storage_file)


class TestStorage:
    """Storage クラスのテスト"""

    def test_is_processed_returns_false_for_new_paper(self, storage):
        """新しい論文IDに対してFalseを返す"""
        arxiv_id = "2025.12345"
        assert storage.is_processed(arxiv_id) is False

    def test_mark_processed_records_paper_id(self, storage, temp_storage_file):
        """論文IDを処理済みとして記録する"""
        arxiv_id = "2025.12345"
        storage.mark_processed(arxiv_id)

        # ファイルに保存されているか確認
        with open(temp_storage_file, 'r') as f:
            data = json.load(f)

        assert arxiv_id in data
        assert isinstance(data[arxiv_id], str)  # タイムスタンプ文字列

    def test_is_processed_returns_true_for_processed_paper(self, storage):
        """処理済み論文IDに対してTrueを返す"""
        arxiv_id = "2025.12345"
        storage.mark_processed(arxiv_id)
        assert storage.is_processed(arxiv_id) is True

    def test_cleanup_old_entries_removes_expired(self, storage, temp_storage_file):
        """古いエントリを削除する"""
        # 古いエントリと新しいエントリを追加
        old_date = (datetime.now() - timedelta(days=31)).isoformat()
        new_date = datetime.now().isoformat()

        data = {
            "2025.11111": old_date,
            "2025.22222": new_date,
        }

        with open(temp_storage_file, 'w') as f:
            json.dump(data, f)

        # 30日より古いエントリを削除
        storage.cleanup_old_entries(days=30)

        # 新しいエントリのみ残っているか確認
        assert storage.is_processed("2025.11111") is False
        assert storage.is_processed("2025.22222") is True

    def test_storage_file_created_if_not_exists(self, temp_storage_file):
        """ストレージファイルが存在しない場合は作成される"""
        # ファイルを削除
        if os.path.exists(temp_storage_file):
            os.unlink(temp_storage_file)

        # 新しいStorageインスタンスを作成
        storage = Storage(temp_storage_file)
        arxiv_id = "2025.12345"
        storage.mark_processed(arxiv_id)

        # ファイルが作成されているか確認
        assert os.path.exists(temp_storage_file)
        assert storage.is_processed(arxiv_id) is True

    def test_multiple_papers_can_be_stored(self, storage):
        """複数の論文を保存できる"""
        paper_ids = ["2025.11111", "2025.22222", "2025.33333"]

        for paper_id in paper_ids:
            storage.mark_processed(paper_id)

        for paper_id in paper_ids:
            assert storage.is_processed(paper_id) is True

    def test_empty_storage_file_is_handled(self, temp_storage_file):
        """空のストレージファイルを処理できる"""
        # 空のJSONファイルを作成
        with open(temp_storage_file, 'w') as f:
            json.dump({}, f)

        storage = Storage(temp_storage_file)
        assert storage.is_processed("2025.12345") is False
