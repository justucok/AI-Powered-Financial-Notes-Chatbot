import io
import logging

import pikepdf
from pypdf import PdfReader

logger = logging.getLogger(__name__)


def decrypt_and_extract_text(pdf_bytes: bytes, password: str = "") -> str:
    """Membuka PDF e-statement dan mengekstrak semua teks dari setiap halaman.

    Args:
        pdf_bytes: Konten file PDF dalam bentuk bytes.
        password: Password untuk membuka proteksi PDF, kosong jika tidak terkunci.

    Returns:
        String berisi semua teks yang diekstrak dari PDF.

    Raises:
        ValueError: Jika PDF terkunci tanpa password valid atau file bukan PDF valid.
    """
    try:
        open_kwargs = {"password": password} if password else {}
        with pikepdf.open(io.BytesIO(pdf_bytes), **open_kwargs) as pdf:
            output_buffer = io.BytesIO()
            pdf.save(output_buffer)
            decrypted_bytes = output_buffer.getvalue()

    except pikepdf.PasswordError as exc:
        if password:
            raise ValueError("Password PDF salah atau file tidak dapat dibuka.") from exc
        raise ValueError("PDF ini terkunci. Masukkan password PDF untuk melanjutkan.") from exc
    except Exception as exc:
        logger.exception("Gagal mendekripsi PDF.")
        raise ValueError("File PDF tidak valid atau rusak.") from exc

    # Langkah 3: Ekstrak teks dari PDF yang sudah didekripsi
    reader = PdfReader(io.BytesIO(decrypted_bytes))
    pages_text: list[str] = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            pages_text.append(f"--- Halaman {i + 1} ---\n{text}")

    full_text = "\n\n".join(pages_text)
    if not full_text.strip():
        raise ValueError("Tidak ada teks yang dapat diekstrak dari PDF ini.")

    return full_text
