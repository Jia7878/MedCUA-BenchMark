"""Serve a stable MedCUA-Bench study list over the public OHIF DICOMweb data."""

from __future__ import annotations

import argparse
import gzip
import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


REMOTE_DICOMWEB_ROOT = "https://d14fa38qiwhyfd.cloudfront.net/dicomweb"

# This fixed 30-study cohort preserves the task targets used by the benchmark:
# 27 radiology/other studies and the three expected slide-microscopy studies.
ALLOWED_STUDY_UIDS = (
    "1.2.840.113619.2.290.3.3767434740.232.1619607454.466",
    "1.3.6.1.4.1.14519.5.2.1.7009.2403.871108593056125491804754960339",
    "1.3.6.1.4.1.14519.5.2.1.7009.2403.334240657131972136850343327463",
    "1.3.6.1.4.1.14519.5.2.1.4334.1501.772823147212833057678103865443",
    "2.16.840.1.114362.1.11972228.22789312658.616067305.306.2",
    "1.3.6.1.4.1.14519.5.2.1.4792.2001.105216574054253895819671475627",
    "61.7.93273854116647800470730671671118421206",
    "1.3.6.1.4.1.14519.5.2.1.1706.4009.192455081946878476141947586891",
    "61.7.110976287009623783394893059131426578073",
    "1.2.124.113532.10.122.1.203.20051130.122937.2950157",
    "1.2.276.0.7230010.3.1.2.447481088.1.1669202398.851612",
    "1.2.840.113619.2.290.3.3767434740.838.1526468636.966",
    "1.3.6.1.4.1.14519.5.2.1.3671.4754.298665348758363466150039312520",
    "1.3.6.1.4.1.5962.99.1.2968617883.1314880426.1493322302363.3.0",
    "1.3.6.1.4.1.14519.5.2.1.1706.8374.643249677828306008300337414785",
    "2.25.103659964951665749659160840573802789777",
    "2.25.141277760791347900862109212450152067508",
    "2.25.275741864483510678566144889372061815320",
    "1.3.6.1.4.1.14519.5.2.1.3023.4024.215308722288168917637555384485",
    "1.3.6.1.4.1.14519.5.2.1.7695.4007.324475281161490036195179843543",
    "1.2.826.0.1.3680043.2.1125.1.11608962641993666019702920539307840",
    "1.3.6.1.4.1.14519.5.2.1.256467663913010332776401703474716742458",
    "1.2.840.113619.2.290.3.3767434740.226.1600859119.501",
    "1.3.76.13.65829.2.20130125082826.1072139.2",
    "1.3.6.1.4.1.14519.5.2.1.99.1071.21255249241959598781018667405790",
    "1.3.6.1.4.1.14519.5.2.1.99.1071.19949805185931008572499729370934",
    "1.3.6.1.4.1.14519.5.2.1.99.1071.26968527900428638961173806140069",
    "1.3.6.1.4.1.14519.5.2.1.99.1071.30380506825315291544089774688247",
    "1.3.6.1.4.1.25403.345050719074.3824.20170125095438.5",
    "1.3.6.1.4.1.25403.345050719074.3824.20170125095258.1",
)

_STUDY_UID_TAG = "0020000D"
_ALLOWED_SET = frozenset(ALLOWED_STUDY_UIDS)
_LOGGER = logging.getLogger("medcua.qido_proxy")


def _study_uid(study: dict) -> str | None:
    values = study.get(_STUDY_UID_TAG, {}).get("Value", [])
    return values[0] if values else None


def filter_studies(studies: list[dict]) -> list[dict]:
    """Filter and order a QIDO study response by the frozen cohort."""
    by_uid = {_study_uid(study): study for study in studies}
    missing = [uid for uid in ALLOWED_STUDY_UIDS if uid not in by_uid]
    if missing:
        raise RuntimeError(
            "The public OHIF endpoint is missing required MedCUA-Bench "
            f"studies: {', '.join(missing)}"
        )
    return [by_uid[uid] for uid in ALLOWED_STUDY_UIDS]


class QIDOProxyHandler(BaseHTTPRequestHandler):
    server_version = "MedCUAQIDOProxy/0.1"

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Accept, Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlsplit(self.path)
        if not parsed.path.startswith("/dicomweb"):
            self.send_error(404, "Expected a /dicomweb path")
            return

        remote_path = parsed.path.removeprefix("/dicomweb")
        remote_url = f"{REMOTE_DICOMWEB_ROOT}{remote_path}"
        if parsed.query:
            remote_url = f"{remote_url}?{parsed.query}"

        request = Request(
            remote_url,
            headers={
                "Accept": self.headers.get("Accept", "application/dicom+json"),
                "Accept-Encoding": "identity",
                "User-Agent": self.server_version,
            },
        )

        try:
            with urlopen(request, timeout=60) as response:
                body = response.read()
                status = response.status
                content_type = response.headers.get(
                    "Content-Type", "application/octet-stream"
                )
                content_encoding = response.headers.get("Content-Encoding", "")
        except HTTPError as error:
            body = error.read()
            status = error.code
            content_type = error.headers.get(
                "Content-Type", "application/octet-stream"
            )
            content_encoding = error.headers.get("Content-Encoding", "")
        except URLError as error:
            self.send_error(502, f"Unable to reach public DICOMweb endpoint: {error}")
            return

        if content_encoding.lower() == "gzip":
            try:
                body = gzip.decompress(body)
            except OSError as error:
                self.send_error(502, f"Invalid gzip response from DICOMweb endpoint: {error}")
                return

        if parsed.path.rstrip("/") == "/dicomweb/studies" and status == 200:
            try:
                body = json.dumps(
                    filter_studies(json.loads(body)),
                    separators=(",", ":"),
                ).encode("utf-8")
                content_type = "application/dicom+json"
            except (json.JSONDecodeError, RuntimeError, UnicodeDecodeError) as error:
                self.send_error(503, str(error))
                return

        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, message, *args):
        _LOGGER.info("%s - %s", self.address_string(), message % args)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3002)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    server = ThreadingHTTPServer((args.host, args.port), QIDOProxyHandler)
    _LOGGER.info("Serving stable QIDO cohort at http://%s:%d/dicomweb", *server.server_address)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
