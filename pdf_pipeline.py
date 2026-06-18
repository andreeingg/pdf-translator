"""
Pipeline PDF - Conversion de documentos
Uso:
  python pdf_pipeline.py to-md  <archivo.pdf>   -> genera <archivo.md>
  python pdf_pipeline.py to-pdf <archivo_ES.md> -> genera <archivo_ES.pdf>
"""

import sys
import warnings
import argparse
from pathlib import Path

import markdown
from xhtml2pdf import pisa
from markitdown import MarkItDown

warnings.filterwarnings("ignore")

CSS = """
@page { margin: 2.5cm; size: A4; }
body {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 10pt;
    line-height: 1.5;
    color: #222;
}
h1 { font-size: 17pt; color: #003366; margin-top: 24px; margin-bottom: 8px; }
h2 { font-size: 14pt; color: #003366; margin-top: 18px; margin-bottom: 6px; }
h3 { font-size: 12pt; color: #005599; margin-top: 14px; margin-bottom: 4px; }
h4 { font-size: 10pt; color: #005599; font-weight: bold; }
p  { margin: 6px 0; text-align: justify; }
ul, ol { margin: 4px 0 4px 18px; }
li { margin: 2px 0; }
table {
    border-collapse: collapse;
    width: 100%;
    margin: 10px 0;
    font-size: 9pt;
}
th {
    background-color: #003366;
    color: white;
    padding: 5px 7px;
    text-align: left;
}
td {
    border: 1px solid #cccccc;
    padding: 4px 7px;
    vertical-align: top;
}
tr:nth-child(even) td { background-color: #f5f5f5; }
code {
    background: #f4f4f4;
    padding: 1px 4px;
    border-radius: 2px;
    font-size: 9pt;
}
hr { border: none; border-top: 1px solid #cccccc; margin: 14px 0; }
"""


def human_size(path: Path) -> str:
    size = path.stat().st_size
    for unit in ("B", "KB", "MB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} MB"


def cmd_to_md(pdf_path: Path) -> None:
    """Convierte PDF a Markdown en la misma carpeta."""
    if not pdf_path.exists():
        print(f"[ERROR] No se encontro: {pdf_path}")
        sys.exit(1)
    if pdf_path.suffix.lower() != ".pdf":
        print(f"[ERROR] Se esperaba un .pdf, recibido: {pdf_path.suffix}")
        sys.exit(1)

    out_path = pdf_path.with_suffix(".md")

    print(f"Convirtiendo: {pdf_path.name}")
    md_converter = MarkItDown()
    result = md_converter.convert(str(pdf_path))

    out_path.write_text(result.text_content, encoding="utf-8")
    total_lines = len(result.text_content.splitlines())
    print(f"Guardado   : {out_path.name}  ({human_size(out_path)}, {total_lines} lineas)")
    print(f"\nProximo paso: comparte esta ruta con Claude para la traduccion:")
    print(f"  \"{out_path}\"")


def cmd_to_pdf(md_path: Path) -> None:
    """Convierte Markdown a PDF en la misma carpeta."""
    if not md_path.exists():
        print(f"[ERROR] No se encontro: {md_path}")
        sys.exit(1)
    if md_path.suffix.lower() != ".md":
        print(f"[ERROR] Se esperaba un .md, recibido: {md_path.suffix}")
        sys.exit(1)

    out_path = md_path.with_suffix(".pdf")

    print(f"Convirtiendo: {md_path.name}")
    md_content = md_path.read_text(encoding="utf-8")

    html_body = markdown.markdown(
        md_content,
        extensions=["tables", "fenced_code", "nl2br"]
    )
    full_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>{CSS}</style>
</head>
<body>{html_body}</body>
</html>"""

    with open(out_path, "wb") as f:
        result = pisa.CreatePDF(full_html, dest=f, encoding="utf-8")

    if result.err:
        print(f"[ERROR] al generar PDF: {result.err}")
        sys.exit(1)

    print(f"Guardado   : {out_path.name}  ({human_size(out_path)})")


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline PDF <-> Markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Ejemplos:
  python pdf_pipeline.py to-md  informe.pdf       (PDF -> Markdown)
  python pdf_pipeline.py to-pdf informe_ES.md     (Markdown -> PDF)
"""
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    p_md = sub.add_parser("to-md", help="PDF -> Markdown")
    p_md.add_argument("archivo", help="Archivo .pdf de entrada")

    p_pdf = sub.add_parser("to-pdf", help="Markdown -> PDF")
    p_pdf.add_argument("archivo", help="Archivo .md de entrada")

    args = parser.parse_args()

    if args.comando == "to-md":
        cmd_to_md(Path(args.archivo))
    else:
        cmd_to_pdf(Path(args.archivo))


if __name__ == "__main__":
    main()
