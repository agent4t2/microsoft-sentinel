import os
import asyncio
from azure.storage.blob.aio import ContainerClient
import json
import logging
import azure.functions as func
import re
import time
import aiohttp
from json import JSONDecodeError
import traceback
from io import BytesIO
import zipfile

from .sentinel_connector_async import AzureSentinelConnectorAsync

logging.getLogger(
    'azure.core.pipeline.policies.http_logging_policy').setLevel(logging.ERROR)
logging.getLogger('charset_normalizer').setLevel(logging.ERROR)

MAX_SCRIPT_EXEC_TIME_MINUTES = 50

AZURE_STORAGE_CONNECTION_STRING = os.environ['AZURE_STORAGE_CONNECTION_STRING']
CONTAINER_NAME = os.environ['CONTAINER_NAME']
ARCHIVE_CONTAINER_NAME = os.environ['ARCHIVE_CONTAINER_NAME']
WORKSPACE_ID = os.environ['WORKSPACE_ID']
SHARED_KEY = os.environ['SHARED_KEY']
LOG_TYPE = 'Fastly'
LINE_SEPARATOR = os.environ.get(
    'lineSeparator',  '[\n\r\x0b\v\x0c\f\x1c\x1d\x85\x1e\u2028\u2029]+')

MAX_CONCURRENT_PROCESSING_FILES = int(
    os.environ.get('MAX_CONCURRENT_PROCESSING_FILES', 10))
MAX_PAGE_SIZE = int(MAX_CONCURRENT_PROCESSING_FILES * 20)
MAX_BUCKET_SIZE = int(os.environ.get('MAX_BUCKET_SIZE', 2000))
MAX_CHUNK_SIZE_MB = int(os.environ.get('MAX_CHUNK_SIZE_MB', 1))

LOG_ANALYTICS_URI = os.environ.get('logAnalyticsUri')
if not LOG_ANALYTICS_URI or str(LOG_ANALYTICS_URI).isspace():
    LOG_ANALYTICS_URI = 'https://' + WORKSPACE_ID + '.ods.opinsights.azure.com'

pattern = r'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$'
match = re.match(pattern, str(LOG_ANALYTICS_URI))
if not match:
    raise Exception("Invalid Log Analytics Uri.")

async def main(mytimer: func.TimerRequest):
    try:
        logging.info('Starting script')
        logging.info('Concurrency parameters: MAX_CONCURRENT_PROCESSING_FILES {}, MAX_PAGE_SIZE {}, MAX_BUCKET_SIZE {}.'.format(
            MAX_CONCURRENT_PROCESSING_FILES, MAX_PAGE_SIZE, MAX_BUCKET_SIZE))
        conn = AzureBlobStorageConnector(
            AZURE_STORAGE_CONNECTION_STRING, CONTAINER_NAME, ARCHIVE_CONTAINER_NAME, MAX_CONCURRENT_PROCESSING_FILES)
        container_client = conn._create_container_client()
        archive_container_client = conn._create_archive_container_client()
        async with container_client, archive_container_client:
            async with aiohttp.ClientSession() as session:
                cors = []
                async for blob in conn.get_blobs():
                    try:
                        cor = conn.process_blob(blob, container_client, archive_container_client, session)
                        cors.append(cor)
                    except Exception as e:
                        logging.error(f'Exception in processing blob is {e}')
                    if len(cors) >= MAX_PAGE_SIZE:
                        await asyncio.gather(*cors)
                        cors = []
                    if conn.check_if_script_runs_too_long():
                        logging.info('Script is running too long. Stop processing new blobs.')
                        break

                if cors:
                    await asyncio.gather(*cors)
                    logging.info('Processed {} files with {} events.'.format(
                        conn.total_blobs, conn.total_events))

        logging.info('Script finished. Processed files: {}. Processed events: {}'.format(
            conn.total_blobs, conn.total_events))
    except Exception as ex:
        logging.error('An error occurred in the main script: {}'.format(str(ex)))
        logging.error(traceback.format_exc())

class AzureBlobStorageConnector:
    def __init__(self, conn_string, container_name, archive_container_name, max_concurrent_processing_fiiles=10):
        self.__conn_string = conn_string
        self.__container_name = container_name
        self.__archive_container_name = archive_container_name 
        self.semaphore = asyncio.Semaphore(max_concurrent_processing_fiiles)
        self.script_start_time = int(time.time())
        self.total_blobs = 0
        self.total_events = 0

    def _create_container_client(self):
        try:
            return ContainerClient.from_connection_string(
                self.__conn_string, self.__container_name,
                logging_enable=False, max_single_get_size=MAX_CHUNK_SIZE_MB*1024*1024, max_chunk_get_size=MAX_CHUNK_SIZE_MB*1024*1024)
        except Exception as ex:
            logging.error('An error occurred in _create_container_client: {}'.format(str(ex)))
            logging.error(traceback.format_exc())
            return None

    def _create_archive_container_client(self): 
        try:
            return ContainerClient.from_connection_string(
                self.__conn_string, self.__archive_container_name,
                logging_enable=False, max_single_get_size=MAX_CHUNK_SIZE_MB*1024*1024, max_chunk_get_size=MAX_CHUNK_SIZE_MB*1024*1024)
        except Exception as ex:
            logging.error('An error occurred in _create_archive_container_client: {}'.format(str(ex)))
            logging.error(traceback.format_exc())
            return None

    async def get_blobs(self):
        try:
            container_client = self._create_container_client()
            logging.info("inside get_blobs function")
            async with container_client:
                async for blob in container_client.list_blobs():
                    name = blob['name']
                    if (
                        'ownership-challenge' not in name and
                        '/' not in name and
                        name.endswith('.log')
                    ):
                        yield blob
                    else:
                        logging.info(f"Skipped blob: {name}")
        except Exception as ex:
            logging.error(f'An error occurred in get_blobs: {ex}')
            logging.error(traceback.format_exc())

    def check_if_script_runs_too_long(self):
        now = int(time.time())
        duration = now - self.script_start_time
        max_duration = int(MAX_SCRIPT_EXEC_TIME_MINUTES * 60 * 0.85)
        return duration > max_duration

    async def archive_blob(self, blob, container_client, archive_container_client):
        """
        Downloads the blob, zips it in-memory, uploads to archive container.
        Returns True on success, False on error.
        """
        try:
            # Download blob content
            logging.info(f"Archiving blob {blob['name']}")
            blob_cor = await container_client.download_blob(blob['name'])
            blob_data = b''
            async for chunk in blob_cor.chunks():
                blob_data += chunk

            # Create in-memory zip file
            zip_buffer = BytesIO()
            zip_name = os.path.basename(blob['name']) + '.zip'
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr(os.path.basename(blob['name']), blob_data)
            zip_buffer.seek(0)

            # Upload to archive container
            await archive_container_client.upload_blob(
                zip_name, zip_buffer, overwrite=True)
            logging.info(f"Blob {blob['name']} archived as {zip_name}.")
            return True
        except Exception as ex:
            logging.error(f"Failed to archive blob {blob['name']}: {ex}")
            logging.error(traceback.format_exc())
            return False

    async def delete_blob(self, blob, container_client):
        try:
            logging.info("inside delete_blob function...")
            logging.info("Deleting blob {}".format(blob['name']))
            await container_client.delete_blob(blob['name'])
        except Exception as ex:
            logging.error(f'An error occurred while deleting blob {blob["name"]}: {ex}')
            logging.error(traceback.format_exc())

    async def process_blob(self, blob, container_client, archive_container_client, session: aiohttp.ClientSession):
        try:
            async with self.semaphore:
                logging.info("Start processing {}".format(blob['name']))
                try:
                    sentinel = AzureSentinelConnectorAsync(
                        session, LOG_ANALYTICS_URI, WORKSPACE_ID, SHARED_KEY, LOG_TYPE, queue_size=MAX_BUCKET_SIZE)
                    blob_cor = await container_client.download_blob(blob['name'], encoding="utf-8")
                except Exception as e:
                    logging.error(f'error while connecting to Sentinel: {e}')
                    logging.error(traceback.format_exc())
                    return

                s = ''
                async for chunk in blob_cor.chunks():
                    s += chunk.decode(errors="replace")
                    lines = re.split(r'{0}'.format(LINE_SEPARATOR), s)
                    for n, line in enumerate(lines):
                        if n < len(lines) - 1:
                            if line:
                                try:
                                    event = json.loads(line)
                                    await sentinel.send(event)
                                except (JSONDecodeError, ValueError) as je:
                                    logging.warning(f"Skipping malformed JSON line in {blob['name']} at index {n}: {je}")
                    s = lines[-1] if lines else ''

                if s:
                    try:
                        event = json.loads(s)
                        await sentinel.send(event)
                    except (JSONDecodeError, ValueError) as je:
                        logging.warning(f"Skipping malformed final JSON line in {blob['name']}: {je}")

                await sentinel.flush()

                # --- ARCHIVE BLOB before deleting ---
                archive_success = await self.archive_blob(blob, container_client, archive_container_client)
                if archive_success:
                    await self.delete_blob(blob, container_client)
                else:
                    logging.error(f"Archiving failed for {blob['name']}. Skipping deletion.")

                self.total_blobs += 1
                self.total_events += sentinel.successfull_sent_events_number
                logging.info("Finish processing {}. Sent events: {}".format(
                    blob['name'], sentinel.successfull_sent_events_number))
                if self.total_blobs % 100 == 0:
                    logging.info('Processed {} files with {} events.'.format(
                        self.total_blobs, self.total_events))

        except Exception as ex:
            logging.error(f"Error in process_blob is {ex}")

