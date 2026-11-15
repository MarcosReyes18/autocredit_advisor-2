# AutoCredit Advisor · Entregable 2 (Build y Test)

Dashboard de riesgo de crédito en Streamlit. **No se alteraron las pantallas ni el CSV que usa la aplicación:** `data/Base_SAS_Equipo3.csv`.

## Archivos de la entrega

| Criterio | Evidencia |
|---|---|
| Investigación de Anthropic y tres cambios | [investigacion/claude.md](investigacion/claude.md) |
| Instrucciones al asistente | [CLAUDE.md](CLAUDE.md) |
| Contrato por columna, tipos, unidad, origen y ausencias | [contrato-datos.md](contrato-datos.md) |
| Verificación de números y ausencias | [scripts/verificar_contrato.py](scripts/verificar_contrato.py) |
| Pruebas de casos correctos e incorrectos | [tests/test_contrato_datos.py](tests/test_contrato_datos.py) |
| Pipeline | [.github/workflows/pruebas.yml](.github/workflows/pruebas.yml) |
| Prompts de la semana | [prompts/B2.md](prompts/B2.md) |
| Idea y evidencia individual | [ideas/A01664722.md](ideas/A01664722.md) y [avance/A01664722.md](avance/A01664722.md) |

## Cómo ejecutar y verificar

Requiere Python 3.11 y las dependencias indicadas:

```bash
python -m pip install -r requirements-dev.txt
python -m scripts.verificar_contrato data/Base_SAS_Equipo3.csv
python -m pytest -q
streamlit run app.py
```

El validador revisa las 12 columnas numéricas, encabezados, variables binarias 0/1, ausencias en variables críticas y tamaño mínimo. Si encuentra un problema, termina con código de salida 1. El pipeline ejecuta la misma comprobación y las pruebas en `push` y `pull_request`.

- [Corrida exitosa en `main`](https://github.com/a01664722-ai/autocredit_advisor-2/actions/runs/43777067259): **80,000 filas y 12 columnas numéricas validadas**, sin marcadores de ausencia; la suite de pruebas terminó correctamente.
- [Corrida fallida intencional](https://github.com/a01664722-ai/autocredit_advisor-2/actions/runs/43777208621): el mismo validador rechazó la fila 2 de un CSV de prueba porque `SAVINGS_BALANCE` contenía `NO_ES_UN_NUMERO`. GitHub Actions detuvo el job con código 1. La prueba se hizo en `prueba/b2-contrato-dato-invalido`, sin tocar la base real ni la rama `main`.
- [Todas las ejecuciones del workflow](https://github.com/a01664722-ai/autocredit_advisor-2/actions/workflows/pruebas.yml).
- **Protección de `main`:** para bloquear también una fusión, el administrador debe configurar el check como obligatorio en las reglas de protección de la rama.

## Acceso y origen de cifras

Repositorio: https://github.com/a01664722-ai/autocredit_advisor-2

**URL pública de Streamlit:** aún no hay una dirección verificada en el repositorio; deberá incorporarse la URL real y probarse en ventana privada. `localhost` no cuenta como publicación.

La app ofrece cuentas de demostración para analistas (Adrián y Sofía), gerencia (Mariana) y soporte/operación (Luis), con permisos según el rol.

- **REAL:** dato del CSV o decisión registrada realmente en bitácora.
- **CALCULADO:** resultado derivado de esos datos o del modelo.
- **SIMULADO:** folios, asignaciones, fechas y escenarios creados para demostrar la pantalla.
- **POLÍTICA:** umbrales definidos por el equipo.

## Alcance de los cambios

Se mantienen intactos `app.py`, `vistas/`, `src/`, `.streamlit/` y `data/Base_SAS_Equipo3.csv`. Se agregan documentación, pruebas y automatización; se retiran únicamente auxiliares antiguos que no utiliza el código.

**Límite pendiente por la restricción visual:** la nueva verificación de tipos corre externamente y en CI, pero no se integra al inicio de la app. Tampoco se añadió `column_order` a las tablas ni se corrigió la ordenación de valores monetarios formateados. Estos puntos de la rúbrica requieren permiso para modificar código de la app, por lo que no se declara cumplimiento completo.
