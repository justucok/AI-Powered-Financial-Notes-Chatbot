import io
import logging

import pikepdf
from pypdf import PdfReader

logger = logging.getLogger(__name__)


def decrypt_and_extract_text(pdf_bytes: bytes, password: str) -> str:
    """Membuka PDF berpassword dan mengekstrak semua teks dari setiap halaman.

    Args:
        pdf_bytes: Konten file PDF dalam bentuk bytes.
        password: Password untuk membuka proteksi PDF.

    Returns:
        String berisi semua teks yang diekstrak dari PDF.

    Raises:
        ValueError: Jika password salah atau file bukan PDF valid.
    """
    try:
        # Langkah 1: Buka dan dekripsi PDF menggunakan pikepdf
        with pikepdf.open(io.BytesIO(pdf_bytes), password=password) as pdf:
            # Langkah 2: Tulis ulang PDF yang sudah terbuka ke buffer (tanpa password)
            output_buffer = io.BytesIO()
            pdf.save(output_buffer)
            decrypted_bytes = output_buffer.getvalue()

    except pikepdf.PasswordError as exc:
        raise ValueError("Password PDF salah atau file tidak dapat dibuka.") from exc
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
