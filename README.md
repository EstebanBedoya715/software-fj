# Software FJ – Sistema Integral de Gestión de Clientes, Servicios y Reservas

Curso **Programación (213023)** – UNAD – Fase 4: Prácticas simuladas.
Aplicación en Python 3 (solo librería estándar), orientada a objetos, **sin base de datos**.
Los archivos se usan únicamente para el registro de eventos y errores (`logs/software_fj.log`).

## Ejecución

```bash
python main.py
```

Salida en consola + registro completo en `logs/software_fj.log`.

## Estructura

| Archivo | Contenido |
|---|---|
| `excepciones.py` | Jerarquía de excepciones personalizadas (`SoftwareFJError` y 7 hijas) |
| `logger.py` | Configuración del archivo de logs |
| `entidad.py` | Clase abstracta `Entidad` (id único + `describir()` abstracto) |
| `cliente.py` | `Cliente`: atributos privados, propiedades con validación estricta |
| `servicio.py` | `Servicio` (abstracta) + `ReservaSala`, `AlquilerEquipo`, `Asesoria` |
| `reserva.py` | `Reserva` con confirmar / cancelar / procesar y estados |
| `gestor.py` | `SistemaGestion`: listas internas y ejecución segura de operaciones |
| `main.py` | Simulación de 31 operaciones (válidas e inválidas) |

## Conceptos de POO aplicados

- **Abstracción:** `Entidad` y `Servicio` son abstractas (`ABC`, `@abstractmethod`).
- **Herencia:** `Cliente`, `Servicio` y `Reserva` heredan de `Entidad`; las 3 clases de servicio heredan de `Servicio`.
- **Polimorfismo:** `describir()`, `validar_parametros()` y `costo_base()` se sobrescriben en cada servicio.
- **Encapsulación:** atributos privados (`__nombre`, `__estado`, …) con `@property` y setters validados.
- **Sobrecarga (simulada):** `calcular_costo(horas)`, `(horas, impuesto)`, `(horas, impuesto, descuento)`, `(horas, cupon="FJ10")`.

## Manejo de excepciones

- Excepciones personalizadas con código (`FJ-101`, `FJ-201`, …).
- `try/except/else/finally` en `Reserva.procesar()` y en `SistemaGestion._ejecutar()`.
- **Encadenamiento** con `raise ... from error` (ej. `TypeError` → `ParametroFaltanteError`).
- Todo error se registra en el log y el programa **continúa** ejecutándose.

## Reglas de negocio

| Servicio | Duración | Costo |
|---|---|---|
| Sala | 1–8 h, asistentes ≤ capacidad | tarifa × h (+ $20.000 si proyector) |
| Equipo | 1–72 h | tarifa × h (+5 % si seguro) |
| Asesoría | 1–6 h | tarifa × h (× 1.25 si es senior) |

Cupones: `FJ10` (10 %) y `FJ20` (20 %). Descuento total máximo: 50 %. IVA por defecto: 19 %.
