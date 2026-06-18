"""
Pipeline PDF - Conversion de documentos
Uso:
  python pdf_pipeline.py to-md  <archivo.pdf>        -> genera <archivo.md>
  python pdf_pipeline.py split  <archivo.md>         -> genera <archivo_p01.md>, <archivo_p02.md>, ...
  python pdf_pipeline.py join   <archivo_ES.md> <p01_ES.md> <p02_ES.md> ...  -> une partes traducidas
  python pdf_pipeline.py to-pdf <archivo_ES.md>      -> genera <archivo_ES.pdf>
"""

import sys
import re
import warnings
import argparse
from pathlib import Path

import markdown
from xhtml2pdf import pisa
from markitdown import MarkItDown

warnings.filterwarnings("ignore")

# Tamano objetivo por parte en lineas (~600 lineas ~ 1 min de traduccion)
CHUNK_TARGET = 600

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

SECTION_RE = re.compile(r"^#{1,2} ", re.MULTILINE)


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
    print(f"Guardado   : {out_path.name}  ({human_size(out_path)})")
    total_lines = len(result.text_content.splitlines())
    print(f"Lineas     : {total_lines}")

    if total_lines > CHUNK_TARGET:
        partes = -(-total_lines // CHUNK_TARGET)  # ceil division
        print(f"\nDocumento largo ({total_lines} lineas). Recomendado dividir en {partes} partes:")
        print(f"  python pdf_pipeline.py split \"{out_path}\"")
    else:
        print(f"\nProximo paso: comparte este .md con Claude para la traduccion.")
    print(f"Ruta: {out_path}")


def _split_into_chunks(lines: list[str], target: int) -> list[list[str]]:
    """
    Divide lineas en grupos respetando los encabezados de seccion (# o ##).
    Cada grupo tiene aproximadamente 'target' lineas.
    """
    # Encontrar indices de encabezados principales
    breaks = [i for i, l in enumerate(lines) if SECTION_RE.match(l)]

    if not breaks:
        # Sin encabezados: cortar por tamano fijo
        return [lines[i:i + target] for i in range(0, len(lines), target)]

    # Agrupar secciones hasta alcanzar el target
    chunks = []
    current_start = 0
    current_size = 0

    for idx, break_pos in enumerate(breaks):
        section_end = breaks[idx + 1] if idx + 1 < len(breaks) else len(lines)
        section_size = section_end - break_pos

        # Si agregar esta seccion supera el doble del target, forzar corte antes
        if current_size >= target and break_pos > current_start:
            chunks.append(lines[current_start:break_pos])
            current_start = break_pos
            current_size = section_size
        else:
            current_size += section_size

    # Ultimo chunk
    if current_start < len(lines):
        chunks.append(lines[current_start:])

    # El bloque inicial (antes del primer encabezado) va junto al primer chunk
    if breaks and breaks[0] > 0:
        prefix = lines[: breaks[0]]
        if chunks:
            chunks[0] = prefix + chunks[0]
        else:
            chunks = [prefix]

    return [c for c in chunks if c]


def cmd_split(md_path: Path, target: int = CHUNK_TARGET) -> None:
    """Divide un .md largo en partes numeradas para traduccion rapida."""
    if not md_path.exists():
        print(f"[ERROR] No se encontro: {md_path}")
        sys.exit(1)
    if md_path.suffix.lower() != ".md":
        print(f"[ERROR] Se esperaba un .md, recibido: {md_path.suffix}")
        sys.exit(1)

    lines = md_path.read_text(encoding="utf-8").splitlines(keepends=True)
    total = len(lines)
    print(f"Dividiendo : {md_path.name}  ({total} lineas)")

    chunks = _split_into_chunks(lines, target)
    stem = md_path.stem
    folder = md_path.parent

    paths = []
    for i, chunk in enumerate(chunks, start=1):
        out = folder / f"{stem}_p{i:02d}.md"
        out.write_text("".join(chunk), encoding="utf-8")
        print(f"  Parte {i:02d} : {out.name}  ({len(chunk)} lineas)")
        paths.append(out)

    print(f"\nTotal: {len(chunks)} partes generadas.")
    print("\nProximo paso — comparte cada parte con Claude en orden:")
    for p in paths:
        print(f"  \"{p}\"  ->  traducir y guardar como  \"{p.stem}_ES.md\"")
    print(f"\nCuando todas las partes esten traducidas, ejecuta:")
    joined_name = folder / f"{stem}_ES.md"
    parts_str = " ".join(f'"{p.stem}_ES.md"' for p in paths)
    print(f'  python pdf_pipeline.py join "{joined_name}" {parts_str}')


def cmd_join(output_path: Path, part_paths: list[Path]) -> None:
    """Une partes traducidas en un unico archivo .md."""
    for p in part_paths:
        if not p.exists():
            print(f"[ERROR] No se encontro: {p}")
            sys.exit(1)

    print(f"Uniendo {len(part_paths)} partes -> {output_path.name}")
    combined = []
    for p in part_paths:
        content = p.read_text(encoding="utf-8")
        combined.append(content)
        print(f"  + {p.name}  ({len(content.splitlines())} lineas)")

    output_path.write_text("\n".join(combined), encoding="utf-8")
    print(f"Guardado   : {output_path.name}  ({human_size(output_path)})")
    print(f"\nProximo paso:")
    print(f"  python pdf_pipeline.py to-pdf \"{output_path}\"")


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
  python pdf_pipeline.py to-md  informe.pdf                          (PDF -> Markdown)
  python pdf_pipeline.py split  informe.md                           (divide para traduccion rapida)
  python pdf_pipeline.py join   informe_ES.md p01_ES.md p02_ES.md   (une partes traducidas)
  python pdf_pipeline.py to-pdf informe_ES.md                        (Markdown -> PDF)
"""
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    p_md = sub.add_parser("to-md", help="PDF -> Markdown")
    p_md.add_argument("archivo", help="Archivo .pdf de entrada")

    p_split = sub.add_parser("split", help="Divide .md en partes para traduccion por partes")
    p_split.add_argument("archivo", help="Archivo .md de entrada")
    p_split.add_argument("--lineas", type=int, default=CHUNK_TARGET,
                         help=f"Lineas objetivo por parte (default: {CHUNK_TARGET})")

    p_join = sub.add_parser("join", help="Une partes traducidas en un .md final")
    p_join.add_argument("salida", help="Archivo .md de salida (ej: informe_ES.md)")
    p_join.add_argument("partes", nargs="+", help="Archivos .md de las partes traducidas, en orden")

    p_pdf = sub.add_parser("to-pdf", help="Markdown -> PDF")
    p_pdf.add_argument("archivo", help="Archivo .md de entrada")

    args = parser.parse_args()

    if args.comando == "to-md":
        cmd_to_md(Path(args.archivo))
    elif args.comando == "split":
        cmd_split(Path(args.archivo), target=args.lineas)
    elif args.comando == "join":
        cmd_join(Path(args.salida), [Path(p) for p in args.partes])
    else:
        cmd_to_pdf(Path(args.archivo))


if __name__ == "__main__":
    main()
