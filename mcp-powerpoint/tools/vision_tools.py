import base64
import io
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image


# Пути из переменных окружения или значения по умолчанию
PPTX_OUTPUT_DIR = Path(os.getenv("PPTX_OUTPUT_DIR", "/output")).resolve()
PPTX_PREVIEW_DIR = Path(os.getenv("PPTX_PREVIEW_DIR", "/preview")).resolve()

DEFAULT_PREVIEW_DIR = PPTX_PREVIEW_DIR

ALLOWED_ROOTS = [
    PPTX_OUTPUT_DIR,
    PPTX_PREVIEW_DIR,
]


def _safe_path(value, must_exist=False):
    """
    Защита от выхода за пределы разрешённых директорий.
    """
    path = Path(value).expanduser().resolve()

    if not any(path.is_relative_to(root) for root in ALLOWED_ROOTS):
        raise ValueError(f"Path is outside allowed roots: {path}")

    if must_exist and not path.exists():
        raise FileNotFoundError(f"File does not exist: {path}")

    return path


def _find_libreoffice():
    """
    Ищем исполняемый файл LibreOffice.
    """
    for name in ("soffice", "libreoffice"):
        path = shutil.which(name)
        if path:
            return path

    candidates = [
        Path("/usr/bin/soffice"),
        Path("/usr/bin/libreoffice"),
        Path("C:/Program Files/LibreOffice/program/soffice.exe"),
        Path("C:/Program Files (x86)/LibreOffice/program/soffice.exe"),
    ]

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    raise RuntimeError(
        "LibreOffice not found. Install libreoffice-impress or LibreOffice."
    )


def _convert_pptx_to_pdf_workdir(pptx_path, workdir):
    """
    Конвертирует PPTX в PDF во временную рабочую директорию.
    """
    libreoffice = _find_libreoffice()
    workdir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="lo_profile_") as profile:
        profile_uri = Path(profile).as_uri()

        cmd = [
            libreoffice,
            "--headless",
            "--norestore",
            "--invisible",
            f"-env:UserInstallation={profile_uri}",
            "--convert-to",
            "pdf",
            "--outdir",
            str(workdir),
            str(pptx_path),
        ]

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
        )

    if proc.returncode != 0:
        raise RuntimeError(
            f"LibreOffice conversion failed: {proc.stderr or proc.stdout}"
        )

    expected_pdf = workdir / f"{pptx_path.stem}.pdf"

    if expected_pdf.exists():
        return expected_pdf

    pdf_files = sorted(workdir.glob("*.pdf"))
    if pdf_files:
        return pdf_files[0]

    raise RuntimeError(f"PDF was not created in {workdir}")


def _pdf_to_images(pdf_path, dpi=96, max_slides=None):
    """
    Рендерит PDF в список PIL Image.
    """
    pdf = pdfium.PdfDocument(str(pdf_path))

    try:
        total_pages = len(pdf)

        if max_slides is not None:
            total_pages = min(total_pages, max(0, max_slides))

        scale = dpi / 72.0
        images = []

        for page_index in range(total_pages):
            page = pdf[page_index]
            bitmap = page.render(scale=scale)
            image = bitmap.to_pil()
            images.append(image)

        return images

    finally:
        pdf.close()


def _pil_to_base64(image):
    """
    Кодирует PIL Image в base64 PNG.
    """
    buffer = io.BytesIO()

    if image.mode != "RGB":
        image = image.convert("RGB")

    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def export_presentation_pdf_impl(pptx_path, output_dir=None):
    """
    Export PPTX to PDF using LibreOffice headless.
    """
    pptx = _safe_path(pptx_path, must_exist=True)

    if output_dir:
        outdir = _safe_path(output_dir)
    else:
        outdir = DEFAULT_PREVIEW_DIR / pptx.stem

    outdir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="lo_export_") as tmp:
        tmp_pdf_path = _convert_pptx_to_pdf_workdir(pptx, Path(tmp))

        target_pdf_path = outdir / f"{pptx.stem}.pdf"
        shutil.copyfile(tmp_pdf_path, target_pdf_path)

    return {
        "pptx": str(pptx),
        "pdf": str(target_pdf_path),
        "size_bytes": target_pdf_path.stat().st_size,
        "mime_type": "application/pdf",
    }


def render_presentation_preview_impl(
    pptx_path,
    output_dir=None,
    dpi=96,
    max_slides=None,
    include_base64=True,
):
    """
    Render PPTX slides into PNG images.
    """
    pptx = _safe_path(pptx_path, must_exist=True)

    if output_dir:
        outdir = _safe_path(output_dir)
    else:
        outdir = DEFAULT_PREVIEW_DIR / pptx.stem

    outdir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="vision_preview_") as tmp:
        pdf_path = _convert_pptx_to_pdf_workdir(pptx, Path(tmp))
        images = _pdf_to_images(
            pdf_path=pdf_path,
            dpi=dpi,
            max_slides=max_slides,
        )

    slides = []

    for slide_number, image in enumerate(images, start=1):
        if image.mode != "RGB":
            image = image.convert("RGB")

        png_path = outdir / f"slide_{slide_number:02d}.png"
        image.save(png_path, "PNG")

        item = {
            "slide": slide_number,
            "path": str(png_path),
            "width": image.width,
            "height": image.height,
            "mime_type": "image/png",
        }

        if include_base64:
            item["image_base64"] = _pil_to_base64(image)

        slides.append(item)

    return {
        "pptx": str(pptx),
        "preview_dir": str(outdir),
        "slides_rendered": len(slides),
        "dpi": dpi,
        "slides": slides,
    }


def render_slide_preview_impl(pptx_path, slide_number, dpi=120):
    """
    Render one specific slide from a PPTX file into PNG.
    """
    if slide_number < 1:
        raise ValueError("slide_number must be >= 1")

    data = render_presentation_preview_impl(
        pptx_path=pptx_path,
        dpi=dpi,
        max_slides=slide_number,
        include_base64=True,
    )

    if len(data["slides"]) < slide_number:
        raise ValueError(
            f"Slide {slide_number} not found. "
            f"Render slides: {len(data['slides'])}."
        )

    return data["slides"][slide_number - 1]


def register_tools(mcp):
    """
    Register vision tools in MCP server.

    IMPORTANT:
    This MCP/FastMCP version does not tolerate Optional[...] annotations
    in tool function signatures, so we use simple types only.
    """

    @mcp.tool()
    def export_presentation_pdf(pptx_path: str, output_dir: str = ""):
        """
        Export a PPTX presentation to PDF using LibreOffice headless.

        If output_dir is empty, preview will be saved to /preview/<pptx_name>/.
        """
        return export_presentation_pdf_impl(
            pptx_path=pptx_path,
            output_dir=output_dir or None,
        )

    @mcp.tool()
    def get_presentation_preview(
        pptx_path: str,
        output_dir: str = "",
        dpi: int = 96,
        max_slides: int = 4,
        include_base64: bool = True,
    ):
        """
        Render PPTX slides into PNG images so a vision LLM can inspect them.

        Recommended values for local CPU:
        dpi=72..100, max_slides=4..6.

        Set max_slides=0 to render all slides.
        If output_dir is empty, preview will be saved to /preview/<pptx_name>/.
        """
        return render_presentation_preview_impl(
            pptx_path=pptx_path,
            output_dir=output_dir or None,
            dpi=dpi,
            max_slides=None if max_slides <= 0 else max_slides,
            include_base64=include_base64,
        )

    @mcp.tool()
    def get_slide_preview(
        pptx_path: str,
        slide_number: int,
        dpi: int = 120,
    ):
        """
        Render one slide from a PPTX file into PNG.
        """
        return render_slide_preview_impl(
            pptx_path=pptx_path,
            slide_number=slide_number,
            dpi=dpi,
        )