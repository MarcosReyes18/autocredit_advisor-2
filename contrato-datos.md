# Contrato de datos · AutoCredit Advisor

La fuente del dashboard es `data/Base_SAS_Equipo3.csv`. El archivo incluido tiene 12 columnas; no debe reemplazarse. **REAL** significa que la cifra viene del CSV, **CALCULADO** que la obtuvo el código a partir de datos reales o del modelo, y **SIMULADO** que se agregó para demostrar una función que la fuente no incluye. Los umbrales de decisión son **POLÍTICA** del equipo.

## 1. Columnas del archivo original

El tipo indicado es el tipo esperado **después de convertir el CSV**. Aunque el archivo CSV guarda caracteres, todos estos campos deben convertirse a números; una celda no numérica causa error. La ausencia nunca se interpreta automáticamente como cero.

| Columna | Tipo esperado | Unidad | Origen | Si está vacía |
|---|---|---|---|---|
| REVOLVING_UTILIZATION | decimal | proporción (1 = 100 %) | REAL · CSV | Desconocido; se conserva como nulo. |
| DEBT_TO_INCOME | decimal | proporción deuda/ingreso | REAL · CSV | Falta dato crítico; se bloquea la validación. |
| MISSED_PAYMENTS_12M | entero | número de pagos fallidos en 12 meses | REAL · CSV | Falta dato crítico; se bloquea la validación. |
| SAVINGS_BALANCE | decimal | unidades monetarias de origen* | REAL · CSV | Falta dato crítico; se bloquea la validación. |
| DOWN_PAYMENT_PCT | decimal | proporción del enganche | REAL · CSV | Desconocido; se conserva como nulo. |
| FINANCIAL_LITERACY_SCORE | decimal | puntos (escala por confirmar) | REAL · CSV | Desconocido; se conserva como nulo; excluido del modelo. |
| LOAN_TO_VALUE | decimal | proporción préstamo/valor | REAL · CSV | Falta dato crítico; se bloquea la validación. |
| DELINQ_90 | entero | número de atrasos de 90+ días | REAL · CSV | Desconocido; se conserva como nulo. |
| YEARS_CREDIT_HISTORY | decimal | años de historial | REAL · CSV | Desconocido; se conserva como nulo. |
| PAYMENT_TO_INCOME | decimal | proporción pago/ingreso | REAL · CSV | Falta dato crítico; se bloquea la validación. |
| BANKRUPTCY_FLAG | entero 0/1 | indicador (0=no; 1=sí) | REAL · CSV | Desconocido; nunca se interpreta como 0. |
| DEFAULT | entero 0/1 | resultado histórico (0=no; 1=sí) | REAL · CSV | Falta variable objetivo; se bloquea la validación. |

*El archivo no acredita por sí solo una moneda. La interfaz usa el símbolo $, pero no se debe afirmar que es MXN o USD sin comprobar la fuente. Este campo debe mantenerse numérico para ordenar correctamente importes.

**Privacidad:** `DEFAULT` histórico no se presenta en expedientes individuales del analista; gerencia solo recibe agregados. La matriz de permisos de la aplicación sigue vigente.

## 2. Columnas y cifras construidas para las pantallas

En estas columnas también debe constar el origen. Cuando no existe dato suficiente, la interfaz debe mostrar «Sin dato» o «—», no un cero inventado. Se incluye el nombre interno cuando existe.

| Columna o cifra publicada | Tipo | Unidad | Origen | Si está vacía |
|---|---|---|---|---|
| FOLIO / Folio | texto | identificador | SIMULADO | No se puede abrir el expediente. |
| ANALISTA_ID | texto | identificador del analista | SIMULADO | No se asigna una solicitud. |
| RECIBIDA_MIN / Recibida | número o texto de visualización | minutos desde recepción | SIMULADO | Se muestra «Sin hora»; no se supone cero. |
| PD | decimal | probabilidad (0 a 1; en pantalla %) | CALCULADO · modelo | Sin recomendación hasta tener datos suficientes. |
| NIVEL | categoría | Bajo, Medio, Alto | CALCULADO · PD + POLÍTICA | Sin clasificación. |
| CALIDAD / Datos | categoría | Completo, Incompleto, Fuera de rango | CALCULADO | Se solicita revisar el expediente. |
| SUGERENCIA / Sugerencia del modelo | categoría | Aprobar, Condicionar, Rechazar | CALCULADO + POLÍTICA | Sin sugerencia; requiere revisión. |
| ESTADO_SOLICITUD | categoría | Pendiente, En espera, Resuelta | SIMULADO / bitácora | Pendiente solo por regla explícita de la demo. |
| SEG_DTI | categoría | tercil de DTI | CALCULADO · DEBT_TO_INCOME | Sin segmento si falta DTI. |
| SEG_ENGANCHE | categoría | banda de enganche | CALCULADO · DOWN_PAYMENT_PCT | Sin segmento. |
| SEG_PAGOS | categoría | banda de pagos fallidos | CALCULADO · MISSED_PAYMENTS_12M | Sin segmento. |
| SEG_BANCARROTA | categoría | Sí / No | CALCULADO · BANKRUPTCY_FLAG | Sin segmento. |
| SEG_LTV | categoría | banda de LTV | CALCULADO · LOAN_TO_VALUE | Sin segmento. |
| n / Registros crediticios | entero | registros | CALCULADO · conteo de REAL | Cero solo cuando efectivamente no hay filas. |
| tasa / Tasa de incumplimiento | decimal | proporción (en pantalla %) | CALCULADO · DEFAULT | No se publica con n menor de 30. |
| DTI promedio | decimal | proporción (en pantalla %) | CALCULADO · DEBT_TO_INCOME | Se muestra «—» si no hay valores válidos. |
| Campos críticos completos | decimal | proporción (en pantalla %) | CALCULADO · campos críticos | Se muestra «—» sin filas válidas. |
| Registros fuera de límites | entero | registros | CALCULADO · límites de src/config.py | Cero solo si se revisaron datos y no hubo casos. |
| Alertas y series del monitor | número / categoría | según métrica | SIMULADO, salvo bitácora indicada | No se presenta como monitoreo productivo. |

Los textos `DTI`, `LTV` y `Valor` de algunas tablas son representaciones formateadas para lectura; no deben confundirse con el tipo numérico de las columnas originales. Las reglas de privacidad por rol prevalecen sobre lo que aparece en este contrato.

## 3. Convención de ausencias y errores

| Marcador leído | Conversión | Interpretación |
|---|---|---|
| Celda vacía, `NA`, `N/A`, `NULL`, `NONE`, `NAN`, `?`, `-`, `S/D` | `None` en la validación | No se conoce el valor; **no** equivale a cero. |
| `0` | Número cero | Dato presente y válido; en `DEFAULT` significa no incumplimiento. |
| `1` | Número uno | Dato presente y válido; en `DEFAULT` significa incumplimiento. |
| Texto como `NO_ES_UN_NUMERO` en una columna numérica | Error | Se rechaza el archivo en el pipeline. |
| Infinito o `DEFAULT` diferente de 0/1 | Error | Se rechaza el archivo. |
| Valor no aplicable | Nulo documentado | Solo se usa si una regla de negocio lo determina; no se infiere del cero. |

**Importante:** la tabla enumera marcadores aceptados por la nueva verificación; no afirma que todos aparezcan en el archivo actual. El reporte de la ejecución indica cuáles se encontraron realmente.

**Resultado comprobado en CI:** en la [corrida del 15 de noviembre de 2026](https://github.com/a01664722-ai/autocredit_advisor-2/actions/runs/43777067259), las 80,000 filas superaron la verificación de las 12 columnas y no aparecieron marcadores de ausencia. En una [corrida negativa independiente](https://github.com/a01664722-ai/autocredit_advisor-2/actions/runs/43777208621), el pipeline sí rechazó un valor de texto en `SAVINGS_BALANCE`.

## 4. Cómo se comprueba

- `python -m scripts.verificar_contrato data/Base_SAS_Equipo3.csv` revisa encabezados, que las 12 columnas sean numéricas, enteros donde corresponde, banderas 0/1, ausencias críticas y al menos 30 registros.
- `tests/test_contrato_datos.py` prueba un CSV correcto y casos con texto en una columna numérica, `DEFAULT=2`, ausencia de DTI y ausencia no crítica.
- `.github/workflows/pruebas.yml` corre la verificación y `pytest` en los cambios del repositorio.
- **Límite de esta entrega sin tocar pantallas:** estas comprobaciones son externas. La aplicación ya muestra un error si falta el CSV o el esquema; para conectar la nueva validación de tipos al arranque y añadir `column_order` en las tablas hace falta autorización expresa para modificar código de la app, que se mantuvo intacto por indicación del equipo.
