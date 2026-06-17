# PDF Translator Pipeline

Herramienta para convertir PDFs técnicos en inglés a Markdown y PDF en español,
usando Claude Code como motor de traducción (sin costo de API adicional).

## Flujo de trabajo

```
informe.pdf  -->  [Paso 1]  -->  informe.md
                                     |
                              Claude lo traduce
                                     |
                              informe_ES.md
                                     |
                  [Paso 3]  -->  informe_ES.pdf
```

## Requisitos

- Python 3.10 o superior
- Claude Code (para el paso de traducción)

## Instalacion

### Opcion 1 — Script automatico (Windows)
Doble clic en `instalar.bat`

### Opcion 2 — Manual (Windows / Mac / Linux)
```bash
pip install -r requirements.txt
```

## Uso

### Paso 1: PDF a Markdown
```bash
python pdf_pipeline.py to-md  "ruta/al/informe.pdf"
```
Genera `informe.md` en la misma carpeta.

### Paso 2: Traduccion con Claude
Abre Claude Code y comparte la ruta del `.md`:
> "Traduccion tecnica del ingles al espanol: ruta/informe.md"

Claude lee el archivo, lo traduce y guarda `informe_ES.md`.

### Paso 3: Markdown a PDF
```bash
python pdf_pipeline.py to-pdf "ruta/al/informe_ES.md"
```
Genera `informe_ES.pdf` en la misma carpeta.

## Dependencias principales

| Paquete | Funcion |
|---|---|
| `markitdown` | Extrae texto de PDF sin procesar imagenes |
| `markdown` | Convierte Markdown a HTML |
| `xhtml2pdf` | Convierte HTML a PDF |

## Por que este flujo ahorra tokens?

Cuando adjuntas un PDF directamente a Claude, cada pagina se procesa como imagen
(alto costo de tokens). Con este pipeline, Claude solo recibe texto plano, reduciendo
el consumo entre 60-70%.
