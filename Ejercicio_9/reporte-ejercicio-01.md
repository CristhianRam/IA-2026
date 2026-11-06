# Reporte Ejercicio 1 — Encadenamiento en la biblioteca
---

## 1. Archivo de la Base de Conocimiento (`biblioteca.yaml`)

```yaml
# Base de conocimiento: Biblioteca
facts:
  - Estudiante(Ana)
  - Estudiante(Luis)
  - Profesor(Marta)
  - TieneCredencial(Ana)
  - TieneCredencial(Marta)
  - HorarioNocturno(Hoy)

rules:
  - id: R_miembro_est
    if:
      - Estudiante(x)
      - TieneCredencial(x)
    then: Miembro(x)
  - id: R_miembro_prof
    if:
      - Profesor(x)
    then: Miembro(x)
  - id: R_acceso
    if:
      - Miembro(x)
      - HorarioNocturno(Hoy)
    then: AccesoNoche(x)
  - id: R_beca
    if:
      - Estudiante(x)
      - TieneCredencial(x)
    then: Becario(x)

query: AccesoNoche(Ana)
```

---

## 2. Resultados y Trazas de Inferencia

### Resumen de Consultas

| Consulta | Hacia Adelante (FC) | Hacia Atrás (BC) |
|---|:---:|:---:|
| `AccesoNoche(Ana)` | **SÍ** (Probada) | **SÍ** (Probada) |
| `AccesoNoche(Luis)` | **NO** (No probada) | **NO** (No probada) |
| `AccesoNoche(Marta)` | **SÍ** (Probada) | **SÍ** (Probada) |

---

### Consulta 1: `AccesoNoche(Ana)`

#### Encadenamiento hacia adelante (*Forward Chaining*)
```text
Agenda (given facts): Estudiante(Ana), Estudiante(Luis), Profesor(Marta), TieneCredencial(Ana), TieneCredencial(Marta), HorarioNocturno(Hoy)
Query: AccesoNoche(Ana)
--- round 1 ---
Fire R_miembro_est  {x_1/Ana}  ⇒  Miembro(Ana)
Fire R_miembro_prof  {x_2/Marta}  ⇒  Miembro(Marta)
Fire R_beca  {x_4/Ana}  ⇒  Becario(Ana)
--- round 2 ---
Fire R_acceso  {x_7/Ana}  ⇒  AccesoNoche(Ana)
Fire R_acceso  {x_7/Marta}  ⇒  AccesoNoche(Marta)
--- round 3 ---
No new facts.
Query proved: AccesoNoche(Ana)
```
- **Resultado:** SÍ (Probada).
- **Átomos nuevos inferidos en orden:** `Miembro(Ana)`, `Miembro(Marta)`, `Becario(Ana)`, `AccesoNoche(Ana)`, `AccesoNoche(Marta)`.

#### Encadenamiento hacia atrás (*Backward Chaining*)
```text
Query: AccesoNoche(Ana)
goal  AccesoNoche(Ana)
rule   R_acceso  {x_3/Ana}
  goal  Miembro(Ana)
  rule   R_miembro_est  {x_3/Ana, x_4/Ana}
    goal  Estudiante(Ana)
    fact   Estudiante(Ana)  {x_3/Ana, x_4/Ana}
    goal  TieneCredencial(Ana)
    fact   TieneCredencial(Ana)  {x_3/Ana, x_4/Ana}
  goal  HorarioNocturno(Hoy)
  fact   HorarioNocturno(Hoy)  {x_3/Ana, x_4/Ana}
Query proved.
```
- **Resultado:** SÍ (Probada).
- **Metas visitadas:** `AccesoNoche(Ana)`, `Miembro(Ana)`, `Estudiante(Ana)`, `TieneCredencial(Ana)`, `HorarioNocturno(Hoy)`.

---

### Consulta 2: `AccesoNoche(Luis)`

#### Encadenamiento hacia adelante (*Forward Chaining*)
```text
Agenda (given facts): Estudiante(Ana), Estudiante(Luis), Profesor(Marta), TieneCredencial(Ana), TieneCredencial(Marta), HorarioNocturno(Hoy)
Query: AccesoNoche(Luis)
--- round 1 ---
Fire R_miembro_est  {x_1/Ana}  ⇒  Miembro(Ana)
Fire R_miembro_prof  {x_2/Marta}  ⇒  Miembro(Marta)
Fire R_beca  {x_4/Ana}  ⇒  Becario(Ana)
--- round 2 ---
Fire R_acceso  {x_7/Ana}  ⇒  AccesoNoche(Ana)
Fire R_acceso  {x_7/Marta}  ⇒  AccesoNoche(Marta)
--- round 3 ---
No new facts.
Query not proved.
```
- **Resultado:** NO (No probada).
- **Átomos nuevos inferidos:** `Miembro(Ana)`, `Miembro(Marta)`, `Becario(Ana)`, `AccesoNoche(Ana)`, `AccesoNoche(Marta)`. Luis no aparece en ningún átomo nuevo derivado.

#### Encadenamiento hacia atrás (*Backward Chaining*)
```text
Query: AccesoNoche(Luis)
goal  AccesoNoche(Luis)
rule   R_acceso  {x_3/Luis}
  goal  Miembro(Luis)
  rule   R_miembro_est  {x_3/Luis, x_4/Luis}
    goal  Estudiante(Luis)
    fact   Estudiante(Luis)  {x_3/Luis, x_4/Luis}
    goal  TieneCredencial(Luis)
    fail   TieneCredencial(Luis)
  rule   R_miembro_prof  {x_3/Luis, x_9/Luis}
    goal  Profesor(Luis)
    fail   Profesor(Luis)
  fail   Miembro(Luis)
fail   AccesoNoche(Luis)
Query not proved.
```
- **Resultado:** NO (No probada).
- **Metas visitadas:** `AccesoNoche(Luis)`, `Miembro(Luis)`, `Estudiante(Luis)`, `TieneCredencial(Luis)`, `Profesor(Luis)`.

---

### Consulta 3: `AccesoNoche(Marta)`

#### Encadenamiento hacia adelante (*Forward Chaining*)
```text
Agenda (given facts): Estudiante(Ana), Estudiante(Luis), Profesor(Marta), TieneCredencial(Ana), TieneCredencial(Marta), HorarioNocturno(Hoy)
Query: AccesoNoche(Marta)
--- round 1 ---
Fire R_miembro_est  {x_1/Ana}  ⇒  Miembro(Ana)
Fire R_miembro_prof  {x_2/Marta}  ⇒  Miembro(Marta)
Fire R_beca  {x_4/Ana}  ⇒  Becario(Ana)
--- round 2 ---
Fire R_acceso  {x_7/Ana}  ⇒  AccesoNoche(Ana)
Fire R_acceso  {x_7/Marta}  ⇒  AccesoNoche(Marta)
--- round 3 ---
No new facts.
Query proved: AccesoNoche(Marta)
```
- **Resultado:** SÍ (Probada).
- **Átomos nuevos inferidos:** `Miembro(Ana)`, `Miembro(Marta)`, `Becario(Ana)`, `AccesoNoche(Ana)`, `AccesoNoche(Marta)`.

#### Encadenamiento hacia atrás (*Backward Chaining*)
```text
Query: AccesoNoche(Marta)
goal  AccesoNoche(Marta)
rule   R_acceso  {x_3/Marta}
  goal  Miembro(Marta)
  rule   R_miembro_est  {x_3/Marta, x_4/Marta}
    goal  Estudiante(Marta)
    fail   Estudiante(Marta)
  rule   R_miembro_prof  {x_3/Marta, x_9/Marta}
    goal  Profesor(Marta)
    fact   Profesor(Marta)  {x_3/Marta, x_9/Marta}
  goal  HorarioNocturno(Hoy)
  fact   HorarioNocturno(Hoy)  {x_3/Marta, x_9/Marta}
Query proved.
```
- **Resultado:** SÍ (Probada).
- **Metas visitadas:** `AccesoNoche(Marta)`, `Miembro(Marta)`, `Estudiante(Marta)`, `Profesor(Marta)`, `HorarioNocturno(Hoy)`.

---

## 3. Reporte de Análisis

### 1. ¿Por qué `Becario(Ana)` sale en el encadenamiento hacia adelante de `AccesoNoche(Ana)` y no en el de hacia atrás?

El encadenamiento hacia adelante (*forward chaining*) es un procedimiento **dirigido por los datos** (*data-driven*). Su dinámica consiste en saturar la base de conocimiento derivando todas las consecuencias lógicas posibles ronda por ronda: en cada iteración examina todas las reglas e incorpora cualquier conclusión cuyas premisas se encuentren unificadas con los hechos conocidos. Dado que en la base inicial existen simultáneamente `Estudiante(Ana)` y `TieneCredencial(Ana)`, la regla `R_beca` queda plenamente satisfecha en la ronda 1 y deriva `Becario(Ana)`, con total independencia de cuál sea la consulta solicitada.

Por el contrario, el encadenamiento hacia atrás (*backward chaining*) es un procedimiento **dirigido por la meta** (*goal-driven*). Comienza en la consulta (`AccesoNoche(Ana)`) y únicamente descompone metas en submetas consultando aquellas reglas cuya cabeza unifica con la meta en turno. Para demostrar `AccesoNoche(Ana)` mediante `R_acceso`, las únicas submetas requeridas son `Miembro(Ana)` y `HorarioNocturno(Hoy)`. A su vez, `Miembro(Ana)` se prueba con éxito inmediato mediante `R_miembro_est`. Como la cabeza de la regla `R_beca` es `Becario(x)` y en ningún momento el predicado `Becario` es una meta requerida por la consulta, el algoritmo hacia atrás jamás visita, evalúa ni dispara dicha regla.

### 2. ¿Por qué hacia atrás prueba `R_miembro_est` al buscar `Miembro(Marta)`, si Marta es profesora?

El algoritmo de encadenamiento hacia atrás opera de manera puramente sintáctica siguiendo el **orden estricto de declaración de las reglas** en la base de conocimiento. Al intentar resolver la meta `Miembro(Marta)`, busca las reglas cuya conclusión unifique con `Miembro(x)`:
1. La primera regla disponible en la tabla es `R_miembro_est` (`Estudiante(x) ∧ TieneCredencial(x) → Miembro(x)`), unificando `x/Marta`.
2. El motor de inferencia no posee clarividencia ni conocimiento semántico previo que le indique que Marta no es estudiante; la única manera formal de verificar si la regla es aplicable es intentar probar su primera premisa (`Estudiante(Marta)`).
3. Al consultar la base de hechos, `Estudiante(Marta)` no existe (ni existe regla alguna para deducirlo), por lo que esta rama falla inmediatamente.

Es precisamente este fallo sintáctico el que desencadena el retroceso (*backtracking*), permitiendo al algoritmo pasar a la siguiente regla en el orden: `R_miembro_prof`, la cual tiene éxito al constatar el hecho `Profesor(Marta)`.

### 3. Incorporación del hecho `TieneCredencial(Luis)` y reevaluación de `AccesoNoche(Luis)`

Al añadir el hecho `TieneCredencial(Luis)` a la base de conocimiento y ejecutar nuevamente el programa para la consulta `AccesoNoche(Luis)`:

#### Comportamiento observado
- **En la ronda 1 hacia adelante**, Luis cuenta ahora tanto con `Estudiante(Luis)` como con `TieneCredencial(Luis)`. Esto permite que se disparen dos reglas para `x = Luis`:
  1. `R_miembro_est` deriva el átomo nuevo `Miembro(Luis)`.
  2. `R_beca` deriva el átomo nuevo `Becario(Luis)`.
- **En la ronda 2 hacia adelante**, al disponer ya de `Miembro(Luis)` y `HorarioNocturno(Hoy)`, la regla `R_acceso` se dispara para `x = Luis` y deriva el átomo nuevo `AccesoNoche(Luis)`.
- **En la ronda 3 hacia adelante**, no surgen hechos nuevos y el algoritmo concluye.

#### Átomos nuevos que aparecen
Respecto al conjunto de 5 átomos inferidos originalmente, aparecen **3 átomos nuevos**:
1. `Miembro(Luis)` (Ronda 1)
2. `Becario(Luis)` (Ronda 1)
3. `AccesoNoche(Luis)` (Ronda 2)

El conjunto total de átomos inferidos se expande a 8:
`Miembro(Ana)`, `Miembro(Luis)`, `Miembro(Marta)`, `Becario(Ana)`, `Becario(Luis)`, `AccesoNoche(Ana)`, `AccesoNoche(Luis)`, `AccesoNoche(Marta)`.

#### Traza de comprobación con el programa
```text
--- FC con TieneCredencial(Luis) ---
Agenda (given facts): Estudiante(Ana), Estudiante(Luis), Profesor(Marta), TieneCredencial(Ana), TieneCredencial(Marta), HorarioNocturno(Hoy), TieneCredencial(Luis)
Query: AccesoNoche(Luis)
--- round 1 ---
Fire R_miembro_est  {x_1/Ana}  ⇒  Miembro(Ana)
Fire R_miembro_est  {x_1/Luis}  ⇒  Miembro(Luis)
Fire R_miembro_prof  {x_2/Marta}  ⇒  Miembro(Marta)
Fire R_beca  {x_4/Ana}  ⇒  Becario(Ana)
Fire R_beca  {x_4/Luis}  ⇒  Becario(Luis)
--- round 2 ---
Fire R_acceso  {x_7/Ana}  ⇒  AccesoNoche(Ana)
Fire R_acceso  {x_7/Luis}  ⇒  AccesoNoche(Luis)
Fire R_acceso  {x_7/Marta}  ⇒  AccesoNoche(Marta)
--- round 3 ---
No new facts.
Query proved: AccesoNoche(Luis)

--- BC con TieneCredencial(Luis) ---
Query: AccesoNoche(Luis)
goal  AccesoNoche(Luis)
rule   R_acceso  {x_3/Luis}
  goal  Miembro(Luis)
  rule   R_miembro_est  {x_3/Luis, x_4/Luis}
    goal  Estudiante(Luis)
    fact   Estudiante(Luis)  {x_3/Luis, x_4/Luis}
    goal  TieneCredencial(Luis)
    fact   TieneCredencial(Luis)  {x_3/Luis, x_4/Luis}
  goal  HorarioNocturno(Hoy)
  fact   HorarioNocturno(Hoy)  {x_3/Luis, x_4/Luis}
Query proved.
```

#### Veredicto
La consulta `AccesoNoche(Luis)` queda **PROBADA (SÍ)** en ambos algoritmos.

