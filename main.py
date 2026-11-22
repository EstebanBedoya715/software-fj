"""
main.py
-------
Simulación de Software FJ: más de 10 operaciones completas que mezclan
casos válidos e inválidos para demostrar que el sistema nunca se detiene.

Ejecución:   python main.py
Resultado:   salida en consola + registro completo en logs/software_fj.log
"""

from gestor import SistemaGestion
from logger import ARCHIVO_LOG, obtener_logger

log = obtener_logger()


def titulo(texto):
    """Imprime un encabezado de sección."""
    print(f"\n--- {texto} ---")


def main():
    log.info("=" * 60)
    log.info("INICIO DE LA SIMULACIÓN SOFTWARE FJ")
    sistema = SistemaGestion()

    # ------------------------------------------------------------------
    titulo("1-4. Registro de clientes (válidos e inválidos)")
    ana = sistema.registrar_cliente(nombre="ana maría torres", documento="1088123456",
                                    email="ana.torres@correo.com", telefono="3101234567")   # válido
    sistema.registrar_cliente(nombre="Luis Pérez", documento="1090111222",
                              email="luis-correo-invalido", telefono="3209998877")           # email inválido
    sistema.registrar_cliente(nombre="Ana Duplicada", documento="1088123456",
                              email="otra@correo.com", telefono="3101112233")                # documento duplicado
    carlos = sistema.registrar_cliente(nombre="Carlos Gómez", documento="79456123",
                                       email="carlos@empresa.co", telefono="3157654321")     # válido
    sistema.registrar_cliente(nombre="Marta Ruiz", documento="52111222")                     # faltan parámetros

    # ------------------------------------------------------------------
    titulo("5-9. Creación de servicios (válidos e inválidos)")
    sala = sistema.crear_servicio("sala", nombre="Sala Innovación", tarifa_hora=50000, capacidad=10)
    sistema.crear_servicio("sala", nombre="Sala Fantasma", tarifa_hora=40000, capacidad=-5)   # capacidad inválida
    equipo = sistema.crear_servicio("equipo", nombre="Portátil Pro", tarifa_hora=8000, tipo_equipo="Portátil")
    asesoria = sistema.crear_servicio("asesoria", nombre="Asesoría Cloud", tarifa_hora=90000,
                                      especialista="Laura Ríos", nivel="senior")
    sistema.crear_servicio("drone", nombre="Drone", tarifa_hora=1000)                          # tipo inexistente
    sala_cerrada = sistema.crear_servicio("sala", nombre="Sala Mantenimiento", tarifa_hora=30000,
                                          capacidad=6, disponible=False)

    # ------------------------------------------------------------------
    titulo("10-13. Reservas exitosas")
    r1 = sistema.crear_reserva(ana.id, sala.id, 3, asistentes=8, proyector=True)
    sistema.confirmar_reserva(r1.id)
    sistema.procesar_reserva(r1.id, impuesto=0.19, descuento=0.05)    # variante impuesto + descuento

    r2 = sistema.crear_reserva(carlos.id, equipo.id, 24, seguro=True)
    sistema.confirmar_reserva(r2.id)
    sistema.procesar_reserva(r2.id, cupon="FJ10")                     # variante con cupón

    r3 = sistema.crear_reserva(ana.id, asesoria.id, 2)
    sistema.confirmar_reserva(r3.id)
    sistema.procesar_reserva(r3.id)                                   # solo IVA por defecto

    # ------------------------------------------------------------------
    titulo("14-20. Reservas y operaciones fallidas")
    sistema.crear_reserva(ana.id, sala.id, 20)                         # horas fuera de rango
    sistema.crear_reserva(carlos.id, sala.id, 2, asistentes=50)        # excede capacidad
    sistema.crear_reserva(carlos.id, sala_cerrada.id, 2)               # servicio no disponible
    sistema.crear_reserva("CLI-999", sala.id, 2)                       # cliente inexistente

    r4 = sistema.crear_reserva(carlos.id, asesoria.id, 1)
    sistema.procesar_reserva(r4.id)                                    # procesar sin confirmar
    sistema.confirmar_reserva(r4.id)
    sistema.procesar_reserva(r4.id, descuento=0.6)                     # descuento excesivo (cálculo inconsistente)
    sistema.procesar_reserva(r4.id, cupon="NOEXISTE")                  # cupón inválido
    sistema.cancelar_reserva(r4.id, "El cliente cambió de planes")     # cancelación válida
    sistema.confirmar_reserva(r4.id)                                   # confirmar una cancelada

    # ------------------------------------------------------------------
    sistema.resumen()
    log.info("FIN DE LA SIMULACIÓN (el sistema se mantuvo estable)")
    print(f"\nRegistro completo en: {ARCHIVO_LOG}")


if __name__ == "__main__":
    main()
