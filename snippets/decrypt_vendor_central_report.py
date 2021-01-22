import base64
import csv
import json

import requests
import smart_open
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from snippets.clients.spa_client import SpaClient


def decrypt_vc_report(
    integration_id: str,
    region: str,
    refresh_token: str,
    report_document_id: str,
    output_bucket: str,
):
    # using Downstream's internal client for interacting with Amazon APIs to get the vendor central report
    client = SpaClient(region, refresh_token, integration_id)
    res = client.get_report_document(report_document_id)

    init_vector = base64.b64decode(res["encryptionDetails"]["initializationVector"])
    key = base64.b64decode(res["encryptionDetails"]["key"])
    download_res = requests.get(res["url"], stream=True)
    decryptor = AES.new(key, AES.MODE_CBC, iv=init_vector)

    s3_key = f"region={region}/{report_document_id}"
    original_s3_key = f"{s3_key}.tsv.gz"
    final_s3_key = f"{s3_key}.json.gz"
    s3_url = f"s3://{output_bucket}"
    original_s3_url = f"{s3_url}/{original_s3_key}"
    final_s3_url = f"{s3_url}/{final_s3_key}"

    with smart_open.open(original_s3_url, "wb", ignore_ext=True) as outfile:
        bytes_read = 0
        for chunk in download_res.iter_content(256 * 1024):
            bytes_read += len(chunk)
            content = decryptor.decrypt(chunk)

            if bytes_read == int(download_res.headers["content-length"]):
                content = unpad(content, AES.block_size)

            outfile.write(content)

    with smart_open.open(
        original_s3_url, encoding=download_res.encoding
    ) as infile, smart_open.open(final_s3_url, "wb") as outfile:
        delimiter = "\t"
        reader = csv.DictReader(infile, delimiter=delimiter)
        for row in reader:
            item = json.dumps(row, ensure_ascii=False)
            line = f"{item}\n"
            outfile.write(line.encode("utf-8"))
