import tempfile
import shutil
import subprocess
from pathlib import Path
import os
import logging

from django.core.files import File as DjangoFile

logger = logging.getLogger('documentos.utils')


def convert_to_pdf(input_path: str, timeout: int = 120) -> str | None:
    """
    Convert an office document to PDF using LibreOffice headless.
    Returns path to a generated temporary PDF or None on failure.
    The caller is responsible for cleaning up the temporary directory.
    """
    p = Path(input_path)
    suffix = p.suffix.lower()
    tmpdir = tempfile.mkdtemp(prefix='doc_preview_')
    logger.info('convert_to_pdf: input=%s tmpdir=%s suffix=%s', input_path, tmpdir, suffix)

    if suffix == '.pdf':
        out_pdf = Path(tmpdir) / p.name
        shutil.copy2(p, out_pdf)
        logger.info('convert_to_pdf: input is already PDF, copied to %s', out_pdf)
        return str(out_pdf)

    try:
        cmd = ['soffice', '--headless', '--convert-to', 'pdf', '--outdir', tmpdir, input_path]
        env = os.environ.copy()
        env['HOME'] = tmpdir
        proc = subprocess.run(cmd, check=False, timeout=timeout, env=env, capture_output=True, text=True)
        logger.info('convert_to_pdf: soffice returncode=%s stdout_len=%s stderr_len=%s', proc.returncode, len(proc.stdout or ''), len(proc.stderr or ''))
        if proc.returncode != 0:
            logger.error('convert_to_pdf: soffice failed: stdout=%s stderr=%s', proc.stdout, proc.stderr)
            shutil.rmtree(tmpdir, ignore_errors=True)
            return None

        out_pdf = Path(tmpdir) / (p.stem + '.pdf')
        if out_pdf.exists():
            logger.info('convert_to_pdf: produced %s', out_pdf)
            return str(out_pdf)

        pdfs = list(Path(tmpdir).glob('*.pdf'))
        if pdfs:
            logger.info('convert_to_pdf: found via glob %s', pdfs[0])
            return str(pdfs[0])

        logger.error('convert_to_pdf: no pdf found in tmpdir')
        shutil.rmtree(tmpdir, ignore_errors=True)
        return None
    except Exception as e:
        logger.exception('convert_to_pdf: exception converting %s: %s', input_path, e)
        shutil.rmtree(tmpdir, ignore_errors=True)
        return None


def generar_preview_pdf(documento) -> bool:
    if not getattr(documento, 'archivo', None):
        return False

    pdf_path = convert_to_pdf(documento.archivo.path)
    if not pdf_path:
        return False

    try:
        with open(pdf_path, 'rb') as pf:
            documento.preview_pdf.save(Path(pdf_path).name, DjangoFile(pf), save=False)
        documento.save(update_fields=['preview_pdf'])
    except Exception:
        return False

    try:
        shutil.rmtree(Path(pdf_path).parent)
    except Exception:
        pass

    return True
