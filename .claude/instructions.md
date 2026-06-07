# Instrucciones para Claude Code — Proyecto Winback Coomeva

## Plan maestro
Sigue paso a paso el archivo `.claude/MVP_Winback_Coomeva.md`. Es la fuente de verdad
para arquitectura, stack, modelo de datos, código de cada componente y orden de implementación.

## Reglas de trabajo
1. Lee el plan completo antes de generar código.
2. Implementa los pasos del 1 al 9 en orden, sin saltar fases.
3. Después de crear o editar CADA archivo, haz commit siguiendo el estándar
   Conventional Commits documentado en la sección 6 del plan.
   Formato obligatorio: `tipo: descripción corta en inglés` (sin ámbito).
4. Mantén actualizado `.claude/progress.md` marcando cada paso completado.
5. No introduzcas dependencias de pago (Twilio, SendGrid, AWS pago). Solo opciones
   gratuitas descritas en la sección 1 del plan.
6. Los datos deben ser sintéticos (mínimo 2000 prospectos). No usar APIs externas
   ni datos reales sensibles.
7. Si encuentras ambigüedad, prioriza simplicidad y que la demo sea operable localmente.