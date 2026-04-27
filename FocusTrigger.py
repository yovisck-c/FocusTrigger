import threading
import time
import json
import random
import sys
import os
import tkinter as tk
from tkinter import font as tkfont
import requests

#Configurações
INTERVAL_HOURS = 1 # intervalo entre pop-ups (horas)
PAUSED = False # estado inicial
API_KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apikey.txt")

#Banco de questões fallback (sem internet)
FALLBACK_QUESTIONS = [
    ("Calcule o limite:", r"lim (x→2) de (x² - 4) / (x - 2)", "4"),
    ("Calcule o limite:", r"lim (x→0) de sen(x) / x", "1"),
    ("Calcule o limite:", r"lim (x→3) de (x² - 9) / (x - 3)", "6"),
    ("Calcule o limite:", r"lim (x→1) de (x³ - 1) / (x - 1)", "3"),
    ("Calcule o limite:", r"lim (x→0) de (1 - cos(x)) / x²", "1/2"),
    ("Calcule o limite:", r"lim (x→∞) de (3x² + 2x) / (x² + 1)", "3"),
    ("Calcule o limite:", r"lim (x→2) de (x³ - 8) / (x - 2)", "12"),
    ("Calcule o limite:", r"lim (x→0) de tan(x) / x", "1"),
    ("Calcule o limite:", r"lim (x→4) de (√x - 2) / (x - 4)", "1/4"),
    ("Calcule o limite:", r"lim (x→∞) de (5x + 3) / (2x - 1)", "5/2"),
    ("Calcule o limite:", r"lim (x→0) de (e^x - 1) / x", "1"),
    ("Calcule o limite:", r"lim (x→1) de (√x - 1) / (x - 1)", "1/2"),
]

def load_api_key():
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, "r") as f:
            return f.read().strip()
    return None

def fetch_question_from_claude(api_key):
    """Chama a API da Anthropic usando a biblioteca requests."""
    url = "https://api.anthropic.com/v1/messages"
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 300,
        "messages": [{
            "role": "user",
            "content": (
                "Gere UMA questão de cálculo de limite para iniciante universitário. "
                "Responda SOMENTE em JSON com este formato exato (sem markdown, sem explicação):\n"
                '{"titulo": "Calcule o limite:", "expressao": "lim (x→?) de ...", "resposta": "valor numérico ou fração"}\n'
                "A questão deve ser original, variada e resolvível analiticamente. "
                "Exemplos de tipos: fatoração, indeterminação 0/0, limites no infinito, limites trigonométricos básicos."
            )
        }]
    }

    response = requests.post(url, headers=headers, json=payload, timeout=10)
    response.raise_for_status()  # Levanta erro se o status não for 200
    
    data = response.json()
    text = data["content"][0]["text"].strip()
    
    # Limpa possível markdown caso o modelo ignore a instrução
    text = text.replace("```json", "").replace("```", "").strip()
    obj = json.loads(text)
    
    return obj["titulo"], obj["expressao"], obj["resposta"]

def get_question():
    """Retorna (titulo, expressão, resposta) — via API ou fallback."""
    api_key = load_api_key()
    if api_key:
        try:
            return fetch_question_from_claude(api_key)
        except Exception:
            pass
    # fallback aleatório
    q = random.choice(FALLBACK_QUESTIONS)
    return q[0], q[1], q[2]

#Pop-up
# Usa função em vez de classe para garantir instância fresca a cada chamada
def show_popup():
    root = tk.Tk()
    root.title("Hora de calcular!")
    root.configure(bg="#0d0d0f")
    root.resizable(False, False)
    root.attributes("-topmost", True)
    root.protocol("WM_DELETE_WINDOW", lambda: None)  # bloqueia X

    W, H = 560, 380
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - W) // 2
    y = (sh - H) // 2
    root.geometry(f"{W}x{H}+{x}+{y}")

    #Fontes
    try:
        title_font = tkfont.Font(family="Courier New", size=11, weight="bold")
        expr_font = tkfont.Font(family="Courier New", size=18, weight="bold")
        label_font = tkfont.Font(family="Courier New", size=10)
        btn_font = tkfont.Font(family="Courier New", size=10, weight="bold")
        small_font = tkfont.Font(family="Courier New", size=8)
    except Exception:
        title_font = expr_font = label_font = btn_font = small_font = ("TkDefaultFont", 10)

    #Cabeçalho
    tk.Frame(root, bg="#12e06a", height=4).pack(fill="x")

    top = tk.Frame(root, bg="#0d0d0f", pady=18)
    top.pack(fill="x", padx=30)
    tk.Label(top, text="▸ FOCUSTRIGGER", font=title_font, fg="#12e06a", bg="#0d0d0f").pack(anchor="w")
    tk.Label(top, text="Resolva para continuar usando o PC", font=small_font, fg="#555566", bg="#0d0d0f").pack(anchor="w")

    #Divisor
    tk.Frame(root, bg="#1e1e28", height=1).pack(fill="x", padx=30)

    #Área da questão
    mid = tk.Frame(root, bg="#0d0d0f", pady=20)
    mid.pack(fill="x", padx=30)

    titulo_var = tk.StringVar(value="Carregando questão...")
    expr_var = tk.StringVar(value="")
    resp_var = tk.StringVar(value="")

    tk.Label(mid, textvariable=titulo_var, font=label_font, fg="#aaaacc", bg="#0d0d0f").pack(anchor="w")
    tk.Label(mid, textvariable=expr_var, font=expr_font, fg="#ffffff", bg="#0d0d0f", wraplength=500, justify="left").pack(anchor="w", pady=(8, 0))

    #Gabarito (oculto)
    gabarito_frame = tk.Frame(root, bg="#0d0d0f")
    gabarito_frame.pack(fill="x", padx=30)
    gabarito_lbl = tk.Label(gabarito_frame, text="", font=small_font, fg="#12e06a", bg="#0d0d0f")
    gabarito_lbl.pack(anchor="w")

    #Entrada
    entry_frame = tk.Frame(root, bg="#0d0d0f", pady=10)
    entry_frame.pack(fill="x", padx=30)
    tk.Label(entry_frame, text="Sua resposta →", font=label_font, fg="#555566", bg="#0d0d0f").pack(side="left", padx=(0, 10))
    entry = tk.Entry(entry_frame, font=expr_font, bg="#1a1a24", fg="#12e06a", insertbackground="#12e06a", relief="flat", width=14, highlightthickness=1, highlightbackground="#333344", highlightcolor="#12e06a")
    entry.pack(side="left")
    entry.focus_set()

    #Botões
    btn_frame = tk.Frame(root, bg="#0d0d0f", pady=14)
    btn_frame.pack(fill="x", padx=30)

    tk.Button(btn_frame, text="VER GABARITO", font=btn_font, bg="#1a1a24", fg="#555566", relief="flat", padx=12, pady=6, cursor="hand2", activebackground="#1a1a24", activeforeground="#aaaacc", command=lambda: gabarito_lbl.config(text=f"Resposta: {resp_var.get()}")).pack(side="left", padx=(0, 10))

    def try_close():
        if entry.get().strip():
            root.destroy()

    tk.Button(btn_frame, text="CONFIRMAR  ▸", font=btn_font, bg="#12e06a", fg="#0d0d0f", relief="flat", padx=16, pady=6, cursor="hand2", activebackground="#0fcc5a", activeforeground="#0d0d0f", command=try_close).pack(side="right")

    root.bind("<Return>", lambda e: try_close())

    #Carrega questão em thread
    def load_q():
        titulo, expressao, resposta = get_question()
        titulo_var.set(titulo)
        expr_var.set(expressao)
        resp_var.set(resposta)

    threading.Thread(target=load_q, daemon=True).start()
    root.mainloop()


#Mantém compatibilidade com chamadas antigas via PopupWindow().show()
class PopupWindow:
    def show(self):
        show_popup()

#Tray icon (pystray)
def run_tray(stop_event):
    try:
        import pystray
        from PIL import Image, ImageDraw

        #Ícone
        img = Image.new("RGB", (64, 64), "#0d0d0f")
        d = ImageDraw.Draw(img)
        d.ellipse([8, 8, 56, 56], fill="#12e06a")
        #Pequeno quadrado escuro no centro como detalhe visual
        d.rectangle([26, 26, 38, 38], fill="#0d0d0f")

        def rebuild_menu(icon):
            icon.menu = pystray.Menu(pystray.MenuItem("Testar pop-up agora", trigger_debug), pystray.Menu.SEPARATOR, pystray.MenuItem("Retomar" if PAUSED else "Pausar (modo jogo)", toggle_pause), pystray.MenuItem("Sair do FocusTrigger", quit_app),)
            icon.title = "FocusTrigger [PAUSADO]" if PAUSED else "FocusTrigger"

        def trigger_debug(icon, item):
            threading.Thread(target=show_popup, daemon=True).start()

        def toggle_pause(icon, item):
            global PAUSED
            PAUSED = not PAUSED
            rebuild_menu(icon)

        def quit_app(icon, item):
            stop_event.set()
            icon.stop()

        menu = pystray.Menu(pystray.MenuItem("Testar pop-up agora", trigger_debug), pystray.Menu.SEPARATOR, pystray.MenuItem("Pausar (modo jogo)", toggle_pause), pystray.MenuItem("Sair do FocusTrigger", quit_app))
        icon = pystray.Icon("FocusTrigger", img, "FocusTrigger", menu)
        icon.run()
    except ImportError:
        stop_event.wait()

# Loop principal
def main():
    stop_event = threading.Event()

    tray_thread = threading.Thread(target=run_tray, args=(stop_event,), daemon=True)
    tray_thread.start()

    interval_secs = INTERVAL_HOURS * 3600

    while not stop_event.is_set():
        # Aguarda o intervalo (checando pausa a cada 30s)
        elapsed = 0
        while elapsed < interval_secs:
            if stop_event.is_set():
                return
            time.sleep(30)
            if not PAUSED:
                elapsed += 30

        if stop_event.is_set():
            return

        if not PAUSED:
            show_popup()

if __name__ == "__main__":
    main()