"""
excepciones.py
--------------
Jerarquía de excepciones personalizadas del sistema Software FJ.

Todas heredan de SoftwareFJError, de modo que el sistema pueda capturar
cualquier error propio con un solo "except SoftwareFJError" y distinguir
los errores inesperados (Exception) de los errores controlados.
"""


class SoftwareFJError(Exception):
    """Excepción base de la aplicación Software FJ."""

    # Código corto que identifica el tipo de error en los logs.
    codigo = "FJ-000"

    def __init__(self, mensaje="Error en el sistema Software FJ"):
        # Se llama al constructor de Exception para conservar el mensaje.
        super().__init__(mensaje)
        # Se guarda el mensaje para poder usarlo en el log.
        self.mensaje = mensaje

    def __str__(self):
        # Formato uniforme: [CODIGO] mensaje
        return f"[{self.codigo}] {self.mensaje}"


class ClienteInvalidoError(SoftwareFJError):
    """Datos personales del cliente inválidos o cliente inexistente/duplicado."""
    codigo = "FJ-101"


class ServicioInvalidoError(SoftwareFJError):
    """Datos o parámetros inválidos al crear o usar un servicio."""
    codigo = "FJ-201"


class ServicioNoDisponibleError(SoftwareFJError):
    """El servicio existe pero no está disponible para reservar."""
    codigo = "FJ-202"


class ReservaInvalidaError(SoftwareFJError):
    """La reserva no puede crearse o procesarse con los datos dados."""
    codigo = "FJ-301"


class OperacionNoPermitidaError(SoftwareFJError):
    """Operación inválida para el estado actual (ej. confirmar una cancelada)."""
    codigo = "FJ-302"


class ParametroFaltanteError(SoftwareFJError):
    """Falta un parámetro obligatorio para completar la operación."""
    codigo = "FJ-401"


class CalculoInconsistenteError(SoftwareFJError):
    """El cálculo de costos produjo un resultado inconsistente."""
    codigo = "FJ-402"
