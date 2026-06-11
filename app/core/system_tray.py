"""System tray icon para controlar el servidor."""
import os
import sys
import time
import threading


def _run_tray():
    """Función que ejecuta el icono del system tray (se ejecuta en proceso separado)."""
    try:
        import pystray
        from PIL import Image, ImageDraw
        import requests
        import webbrowser

        def create_icon_image():
            """Crea la imagen del icono."""
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            icon_paths = [
                os.path.join(base_dir, "static", "favicon.ico"),
                os.path.join(base_dir, "static", "icon.ico"),
                os.path.join(base_dir, "static", "logo.png"),
            ]
            
            for path in icon_paths:
                if os.path.exists(path):
                    try:
                        return Image.open(path)
                    except:
                        pass
            
            # Crear un icono por defecto (círculo azul con W)
            size = (64, 64)
            image = Image.new("RGB", size, color=(0, 100, 200))
            draw = ImageDraw.Draw(image)
            
            # Círculo exterior
            draw.ellipse([4, 4, 60, 60], outline="white", width=3)
            
            # Letra W
            draw.line([16, 44, 16, 20], fill="white", width=3)
            draw.line([16, 20, 32, 44], fill="white", width=3)
            draw.line([32, 44, 48, 20], fill="white", width=3)
            draw.line([48, 20, 48, 44], fill="white", width=3)
            
            return image

        def open_browser(icon=None, item=None):
            """Abre la interfaz en el navegador."""
            webbrowser.open("http://127.0.0.1:9080/ui")

        def check_server_status():
            """Verifica si el servidor está activo."""
            try:
                response = requests.get("http://127.0.0.1:9080/health", timeout=2)
                return response.status_code == 200
            except:
                return False

        def stop_server(icon=None, item=None):
            """Detiene el servidor."""
            try:
                requests.post("http://127.0.0.1:9080/admin/shutdown", timeout=2)
            except:
                pass
            icon.stop()

        def restart_server(icon=None, item=None):
            """Reinicia el servidor."""
            try:
                requests.post("http://127.0.0.1:9080/admin/restart", timeout=2)
            except:
                pass
            icon.stop()

        def quit_app(icon=None, item=None):
            """Sale del system tray."""
            icon.stop()

        # Esperar un momento a que el servidor arranque
        time.sleep(2)

        # Crear icono
        icon_image = create_icon_image()
        
        # Verificar estado del servidor
        server_running = check_server_status()
        
        # Crear menú
        if server_running:
            menu = pystray.Menu(
                pystray.MenuItem("  >>>  Interfaz activa", lambda i: None, enabled=False),
                pystray.MenuItem("---", lambda i: None),
                pystray.MenuItem("Abrir interfaz", open_browser, default=True),
                pystray.MenuItem("---", lambda i: None),
                pystray.MenuItem("Reiniciar servidor", restart_server),
                pystray.MenuItem("Detener servidor", stop_server),
                pystray.MenuItem("---", lambda i: None),
                pystray.MenuItem("Salir", quit_app)
            )
            tooltip = "Wui - Plataforma de Automatización (Activo)"
        else:
            menu = pystray.Menu(
                pystray.MenuItem("  >>>  Servidor detenido", lambda i: None, enabled=False),
                pystray.MenuItem("---", lambda i: None),
                pystray.MenuItem("Abrir interfaz", open_browser),
                pystray.MenuItem("---", lambda i: None),
                pystray.MenuItem("Salir", quit_app)
            )
            tooltip = "Wui - Plataforma de Automatización (Detenido)"

        # Crear y ejecutar icono
        icon = pystray.Icon("wui", icon_image, tooltip, menu)
        icon.run()

    except Exception as e:
        print(f"ERROR en system tray: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)


def create_tray_icon():
    """Crea y muestra el icono del system tray en un proceso separado."""
    import multiprocessing
    p = multiprocessing.Process(target=_run_tray, daemon=True)
    p.start()
    return p


def start_tray_from_lifespan():
    """Se llama desde el lifespan de FastAPI."""
    try:
        create_tray_icon()
    except Exception as e:
        print(f"Error iniciando system tray: {e}", file=sys.stderr)