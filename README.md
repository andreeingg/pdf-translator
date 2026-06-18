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

1. Abre una sesion nueva de Claude Code
2. Pega el contenido de `prompt_traduccion.md` (establece el rol de especialista)
3. Comparte la ruta del `.md`:
   > "Traduce este documento: ruta/informe.md"

Claude actua como hidrogeólogo senior, aplica la terminología técnica correcta
y guarda `informe_ES.md` en la misma carpeta.

> Si abres Claude Code desde la carpeta `pdf-translator/`, el archivo `CLAUDE.md`
> carga el contexto automaticamente — no necesitas pegar el prompt.

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
