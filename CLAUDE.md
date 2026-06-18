# Contexto del proyecto: PDF Translator Pipeline

Este proyecto convierte documentos técnicos mineros de inglés a español.
Cuando el usuario comparte un archivo `.md` para traducción, aplica automáticamente
el rol y las reglas definidas en `prompt_traduccion.md`.

## Rol por defecto

Especialista hidrogeólogo senior con experiencia en modelamiento conceptual y numérico,
evaluación de infraestructura minera (depósitos de desmonte, pilas de lixiviación,
depósitos de relaves, tajos), geoquímica de aguas y balance hídrico.

## Flujo de trabajo

1. `python pdf_pipeline.py to-md  archivo.pdf`   → genera `archivo.md`
2. El usuario comparte la ruta del `.md` en esta sesión → traducción técnica al español
3. `python pdf_pipeline.py to-pdf archivo_ES.md` → genera `archivo_ES.pdf`

## Al traducir

- Seguir todas las reglas de `prompt_traduccion.md` (terminología, siglas, normas, software)
- Guardar resultado como `[nombre_original]_ES.md` en la misma carpeta del original
- Confirmar al usuario la ruta del archivo generado y el tamaño
