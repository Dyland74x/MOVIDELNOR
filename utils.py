import logging
from functools import wraps
from time import sleep
import traceback
from flask import render_template
import tempfile
import webbrowser

logger = logging.getLogger(__name__)

def retry_on_failure(max_retries=3, delay=1):
    """
    Decorador para reintentar una función si falla.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Intento {attempt+1} falló: {e}")
                    if attempt == max_retries - 1:
                        logger.error(f"Fallo definitivo: {traceback.format_exc()}")
                        raise
                    sleep(delay)
            return None
        return decorated
    return decorator


def imprimir_ticket(turno, modulo):
    """
    Imprime un ticket usando la impresora predeterminada de Windows (win32print).
    Si win32print no está disponible, abre el ticket en el navegador.
    """

    html = render_template('ticket_print.html', turno=turno, modulo=modulo)
    
    try:
        import win32print
        import win32ui
        
        contenido = f"""
SISTEMA DE TURNOS
=================
Turno: {turno.numero_turno}
Módulo: {modulo.nombre}
Fecha: {turno.creado_en.strftime('%d/%m/%Y %H:%M:%S')}

Gracias por su espera
"""
        printer_name = win32print.GetDefaultPrinter()
        hprinter = win32print.OpenPrinter(printer_name)
        try:
            win32print.StartDocPrinter(hprinter, 1, ("Ticket", None, "RAW"))
            win32print.StartPagePrinter(hprinter)
            win32print.WritePrinter(hprinter, contenido.encode('utf-8'))
            win32print.EndPagePrinter(hprinter)
            win32print.EndDocPrinter(hprinter)
        finally:
            win32print.ClosePrinter(hprinter)
        logger.info(f"Ticket impreso correctamente: {turno.numero_turno}")
        return
    except ImportError:
        logger.warning("win32print no instalado. Se usará la vista previa en navegador.")
    except Exception as e:
        logger.error(f"Error con win32print: {e}. Se usará la vista previa en navegador.")

    # Fallback: abrir el ticket en el navegador
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html)
        temp_html = f.name
    webbrowser.open(temp_html)
    logger.info(f"Ticket abierto en navegador: {temp_html}")