# Copyright 2022 MosaicML LLM Foundry authors
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Callable, List
from unittest.mock import patch

from composer.core import State, Time, TimeUnit
from composer.devices import DeviceCPU
from composer.loggers import Logger

from llmfoundry.callbacks.hf_checkpointer import HuggingFaceCheckpointer

dummy_s3_path = 's3://dummy/path'
dummy_oci_path = 'oci://dummypath'
dummy_gc_path = 'gs://dummy/path'
dummy_uc_path = 'dbfs://dummypath/Volumes/the_catalog/the_schema/yada_yada'

dummy_save_interval = Time(1, TimeUnit.EPOCH)


def dummy_log_info(log_output: List[str]):
    def _dummy_log_info(*msgs: str):
        log_output.extend(msgs)

    return _dummy_log_info


@patch(
    'composer.loggers.remote_uploader_downloader.RemoteUploaderDownloader.upload_file',
    lambda *_, **__: None)
def assert_checkpoint_saves_to_uri(uri: str, build_tiny_hf_mpt: Callable):
    uri_base = uri.split('://')[0]
    model = build_tiny_hf_mpt(attn_config={
        'attn_impl': 'triton',
        'attn_uses_sequence_id': False,
    })

    dummy_state = State(model=model,
                        rank_zero_seed=42,
                        run_name='dummy_run',
                        device=DeviceCPU())
    dummy_logger = Logger(dummy_state)
    # mock the State and Logger
    logs = []
    with patch('logging.Logger.info', dummy_log_info(logs)):
        my_checkpointer = HuggingFaceCheckpointer(
            save_folder=uri, save_interval=dummy_save_interval)
        my_checkpointer._save_checkpoint(dummy_state, dummy_logger)

    assert any([uri_base in str(log) for log in logs])


def test_checkpoint_saves_to_s3(build_tiny_hf_mpt: Callable):
    assert_checkpoint_saves_to_uri(dummy_s3_path, build_tiny_hf_mpt)


class DummyData:

    def __init__(self, *_, **__: Any):
        self.data = '🪐'
        pass


class DummyClient:

    def __init__(self, *_, **__: Any):
        pass

    def get_namespace(self, *_, **__: Any):
        return DummyData()


def test_checkpoint_saves_to_oci(build_tiny_hf_mpt: Callable,
                                 oci_temp_file: None):
    with patch('oci.config.from_file', lambda _: {}), \
         patch('oci.object_storage.ObjectStorageClient', lambda *_, **__: DummyClient()), \
         patch('oci.object_storage.UploadManager', lambda *_, **__: None):
        assert_checkpoint_saves_to_uri(dummy_oci_path, build_tiny_hf_mpt)


def test_checkpoint_saves_to_gc(build_tiny_hf_mpt: Callable,
                                gcs_account_credentials: None):
    assert_checkpoint_saves_to_uri(dummy_gc_path, build_tiny_hf_mpt)


def test_checkpoint_saves_to_uc(build_tiny_hf_mpt: Callable,
                                uc_account_credentials: None):
    assert_checkpoint_saves_to_uri(dummy_uc_path, build_tiny_hf_mpt)
