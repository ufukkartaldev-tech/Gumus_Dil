# -*- coding: utf-8 -*-

class LibraryBridge:
    """GümüşDil Evrensel Kütüphane Köprüsü (Python/C++ Mapping)"""
    
    # Kütüphane Haritası: GümüşDil İsmi -> {Python Bilgisi, C++ Bilgisi}
    LIBRARY_MAP = {
        "matematik": {
            "py": {"module": "math", "alias": "matematik"},
            "cpp": {"include": "cmath", "namespace": "std"}
        },
        "zaman": {
            "py": {"module": "time", "alias": "zaman"},
            "cpp": {"include": "chrono", "namespace": "std::chrono"}
        },
        "rastgele": {
            "py": {"module": "random", "alias": "rastgele"},
            "cpp": {"include": "cstdlib", "namespace": "std"}
        },
        "sistem": {
            "py": {"module": "os", "alias": "sistem"},
            "cpp": {"include": "cstdlib", "namespace": "std"}
        },
        "arayüz": {
            "py": {"module": "tkinter", "alias": "arayüz"},
            "cpp": {"include": "QtWidget", "namespace": "Qt"}
        },
        "veritabanı": {
            "py": {"module": "sqlite3", "alias": "veritabanı"},
            "cpp": {"include": "sqlite3.h", "namespace": ""}
        },
        "görüntü_işleme": {
            "py": {"module": "cv2", "alias": "görüntü_işleme"},
            "cpp": {"include": "opencv2/opencv.hpp", "namespace": "cv"}
        },
        "çizim": {
            "py": {"module": "matplotlib.pyplot", "alias": "çizim"},
            "cpp": {"include": "pbPlots.hpp", "namespace": ""}
        },
        "oyun": {
            "py": {"module": "pygame", "alias": "oyun"},
            "cpp": {"include": "SFML/Graphics.hpp", "namespace": "sf"}
        },
        "donanım": {
            "py": {"module": "RPi.GPIO", "alias": "donanım"},
            "cpp": {"include": "wiringPi.h", "namespace": ""}
        },
        "kripto": {
            "py": {"module": "cryptography", "alias": "kripto"},
            "cpp": {"include": "openssl/evp.h", "namespace": ""}
        },
        "json": {
            "py": {"module": "json", "alias": "json"},
            "cpp": {"include": "nlohmann/json.hpp", "namespace": "nlohmann"}
        },
        "istatistik": {
            "py": {"module": "statistics", "alias": "istatistik"},
            "cpp": {"include": "boost/accumulators/accumulators.hpp", "namespace": "boost"}
        },
        "ağ": {
            "py": {"module": "requests", "alias": "ağ"},
            "cpp": {"include": "curl/curl.h", "namespace": ""}
        },
        "veri": {
            "py": {"module": "pandas", "alias": "veri"},
            "cpp": {"include": "csv.h", "namespace": ""}
        },
        "yapay_zeka": {
            "py": {"module": "sklearn", "alias": "yapay_zeka"},
            "cpp": {"include": "mlpack.hpp", "namespace": "mlpack"}
        },
        "web_isteği": {
            "py": {"module": "urllib.request", "alias": "web_isteği"},
            "cpp": {"include": "httplib.h", "namespace": "httplib"}
        },
        "ses": {
            "py": {"module": "winsound", "alias": "ses"},
            "cpp": {"include": "mmsystem.h", "namespace": ""}
        },
        "işlemci": {
            "py": {"module": "multiprocessing", "alias": "işlemci"},
            "cpp": {"include": "thread", "namespace": "std"}
        },
        "günlük": {
            "py": {"module": "logging", "alias": "günlük"},
            "cpp": {"include": "spdlog/spdlog.h", "namespace": "spdlog"}
        },
        "test": {
            "py": {"module": "unittest", "alias": "test"},
            "cpp": {"include": "gtest/gtest.h", "namespace": "testing"}
        },
        "sıkıştırma": {
            "py": {"module": "zipfile", "alias": "sıkıştırma"},
            "cpp": {"include": "zlib.h", "namespace": ""}
        },
        "eşleştirme": {
            "py": {"module": "re", "alias": "eşleştirme"},
            "cpp": {"include": "regex", "namespace": "std"}
        },
        "csv": {
            "py": {"module": "csv", "alias": "csv"},
            "cpp": {"include": "rapidcsv.h", "namespace": "rapidcsv"}
        },
        "xml": {
            "py": {"module": "xml.etree.ElementTree", "alias": "xml"},
            "cpp": {"include": "pugixml.hpp", "namespace": "pugi"}
        },
        "ikili": {
            "py": {"module": "struct", "alias": "ikili"},
            "cpp": {"include": "cstdint", "namespace": "std"}
        },
        "bulut": {
            "py": {"module": "boto3", "alias": "bulut"},
            "cpp": {"include": "aws/core/Aws.h", "namespace": "Aws"}
        },
        "blokzincir": {
            "py": {"module": "hashlib", "alias": "blokzincir"},
            "cpp": {"include": "openssl/sha.h", "namespace": ""}
        },
        "kuantum": {
            "py": {"module": "qiskit", "alias": "kuantum"},
            "cpp": {"include": "qpp/qpp.h", "namespace": "qpp"}
        },
        "dil_işleme": {
            "py": {"module": "nltk", "alias": "dil_işleme"},
            "cpp": {"include": "icu.h", "namespace": "icu"}
        },
        "bilimsel": {
            "py": {"module": "scipy", "alias": "bilimsel"},
            "cpp": {"include": "gsl/gsl_math.h", "namespace": "gsl"}
        },
        "soket": {
            "py": {"module": "socket", "alias": "soket"},
            "cpp": {"include": "sys/socket.h", "namespace": ""}
        },
        "eşzamanlı": {
            "py": {"module": "asyncio", "alias": "eşzamanlı"},
            "cpp": {"include": "boost/asio.hpp", "namespace": "boost::asio"}
        },
        "görselleştirme": {
            "py": {"module": "plotly", "alias": "görselleştirme"},
            "cpp": {"include": "matplot/matplot.h", "namespace": "matplot"}
        },
        "serileştirme": {
            "py": {"module": "pickle", "alias": "serileştirme"},
            "cpp": {"include": "boost/serialization/serialization.hpp", "namespace": "boost::serialization"}
        },
        "yapılandırma": {
            "py": {"module": "yaml", "alias": "yapılandırma"},
            "cpp": {"include": "yaml-cpp/yaml.h", "namespace": "YAML"}
        },
        "zaman_dilimi": {
            "py": {"module": "pytz", "alias": "zaman_dilimi"},
            "cpp": {"include": "date/tz.h", "namespace": "date"}
        },
        "harita": {
            "py": {"module": "geopy", "alias": "harita"},
            "cpp": {"include": "gdal.h", "namespace": "gdal"}
        },
        "belge": {
            "py": {"module": "reportlab", "alias": "belge"},
            "cpp": {"include": "poppler-qt5.h", "namespace": "poppler"}
        },
        "hızlandırıcı": {
            "py": {"module": "pycuda", "alias": "hızlandırıcı"},
            "cpp": {"include": "cuda_runtime.h", "namespace": "cuda"}
        },
        "seri_port": {
            "py": {"module": "serial", "alias": "seri_port"},
            "cpp": {"include": "serial/serial.h", "namespace": "serial"}
        },
        "transfer": {
            "py": {"module": "ftplib", "alias": "transfer"},
            "cpp": {"include": "libssh2.h", "namespace": ""}
        }
    }

    @staticmethod
    def get_python_import(gumus_module):
        info = LibraryBridge.LIBRARY_MAP.get(gumus_module)
        if info:
            py = info["py"]
            return f"import {py['module']} as {py['alias']}"
        return f"import {gumus_module}"

    @staticmethod
    def get_cpp_include(gumus_module):
        info = LibraryBridge.LIBRARY_MAP.get(gumus_module)
        if info:
            return info["cpp"]["include"]
        return gumus_module

