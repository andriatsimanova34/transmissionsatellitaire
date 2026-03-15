#!/usr/bin/env python3
"""
Simulation Hamming(7,4) - Liaison Satellite
Notation : x = mot émis, y = mot reçu
           d1 d2 d3 d4 = bits de données, p1 p2 p3 = bits de parité
Onglet 1 : simulation bit unique animée
Onglet 2 : transmission d'un mot textuel complet
"""

import tkinter as tk
import random

# ─────────────────────────────────────────────
# LOGIQUE HAMMING(7,4)
# ─────────────────────────────────────────────

def encode_hamming(data_bits):
    """Encode 4 bits en mot Hamming(7,4).
    Structure : [p1, p2, d1, p3, d2, d3, d4]
    """
    d1, d2, d3, d4 = data_bits
    p1 = d1 ^ d2 ^ d4
    p2 = d1 ^ d3 ^ d4
    p3 = d2 ^ d3 ^ d4
    return [p1, p2, d1, p3, d2, d3, d4]

def introduce_error(codeword, position):
    result = codeword[:]
    if 1 <= position <= 7:
        result[position - 1] ^= 1
    return result

def compute_syndrome(received):
    y = received
    s1 = y[0] ^ y[2] ^ y[4] ^ y[6]
    s2 = y[1] ^ y[2] ^ y[5] ^ y[6]
    s3 = y[3] ^ y[4] ^ y[5] ^ y[6]
    return s1, s2, s3

def decode_hamming(received):
    s1, s2, s3 = compute_syndrome(received)
    syndrome = s3 * 4 + s2 * 2 + s1
    corrected = received[:]
    if syndrome != 0:
        corrected[syndrome - 1] ^= 1
    data = [corrected[2], corrected[4], corrected[5], corrected[6]]
    return corrected, syndrome, data

def bits_to_decimal(bits):
    return sum(b * (2 ** (len(bits) - 1 - i)) for i, b in enumerate(bits))

def decimal_to_bits4(n):
    n = max(0, min(15, n))
    return [(n >> (3 - i)) & 1 for i in range(4)]

def char_to_bits4(c):
    code = ord(c.upper()) & 0x0F
    return decimal_to_bits4(code)

def char_to_bits8(c):
    code = ord(c) & 0xFF
    return [(code >> (7 - i)) & 1 for i in range(8)]

def bits8_to_char(bits):
    val = sum(b * (2 ** (7 - i)) for i, b in enumerate(bits))
    return chr(val) if 32 <= val <= 126 else '?'

def encode_text(text):
    result = []
    for ch in text:
        bits8 = char_to_bits8(ch)
        high4, low4 = bits8[:4], bits8[4:]
        result.append((ch, 0, high4, encode_hamming(high4)))
        result.append((ch, 1, low4,  encode_hamming(low4)))
    return result

# ─────────────────────────────────────────────
# COULEURS & STYLE
# ─────────────────────────────────────────────

BG        = "#0f0f1a"
BG2       = "#16162a"
BG3       = "#1e1e35"
CARD      = "#1a1a2e"
BORDER    = "#2a2a4a"
ACCENT    = "#6c63ff"
ACCENT2   = "#00d4aa"
AMBER     = "#ffa94d"
TEXT      = "#e8e8f0"
TEXT2     = "#9898b8"
TEXT3     = "#5a5a7a"
GREEN     = "#51cf66"
RED       = "#ff6b6b"
PURPLE    = "#845ef7"
TEAL      = "#20c997"

BIT_PARITY_BG = "#2d1f6e"
BIT_PARITY_FG = "#a78bfa"
BIT_DATA_BG   = "#0f3d30"
BIT_DATA_FG   = "#34d399"
BIT_ERROR_BG  = "#4a0e0e"
BIT_ERROR_FG  = "#f87171"
BIT_FIXED_BG  = "#0f3d1a"
BIT_FIXED_FG  = "#4ade80"

FONT_TITLE = ("Courier New", 16, "bold")
FONT_HEAD  = ("Courier New", 11, "bold")
FONT_BODY  = ("Courier New", 10)
FONT_SMALL = ("Courier New", 9)
FONT_MONO  = ("Courier New", 11, "bold")
FONT_BIG   = ("Courier New", 20, "bold")

# ─────────────────────────────────────────────
# WIDGETS PERSONNALISÉS
# ─────────────────────────────────────────────

class BitCell(tk.Canvas):
    def __init__(self, parent, value=0, style="data", size=44, **kwargs):
        super().__init__(parent, width=size, height=size,
                         bg=BG2, highlightthickness=0, **kwargs)
        self.size  = size
        self.style = style
        self.value = value
        self._draw()

    def _draw(self):
        s = self.size
        styles = {
            "data":    (BIT_DATA_BG,   BIT_DATA_FG,   TEAL),
            "parity":  (BIT_PARITY_BG, BIT_PARITY_FG, PURPLE),
            "error":   (BIT_ERROR_BG,  BIT_ERROR_FG,  RED),
            "fixed":   (BIT_FIXED_BG,  BIT_FIXED_FG,  GREEN),
            "neutral": (BG3,           TEXT2,          BORDER),
        }
        bg, fg, border = styles.get(self.style, styles["neutral"])
        self.delete("all")
        self._rounded_rect(3, 3, s-3, s-3, 6, fill=bg, outline=border, width=1.5)
        self.create_text(s//2, s//2, text=str(self.value),
                         font=("Courier New", max(10, s//3), "bold"), fill=fg)

    def _rounded_rect(self, x1, y1, x2, y2, r, **kw):
        self.create_polygon(
            x1+r, y1, x2-r, y1, x2, y1,   x2, y1+r,
            x2, y2-r, x2, y2,   x2-r, y2, x1+r, y2,
            x1, y2,   x1, y2-r, x1, y1+r, x1, y1,
            smooth=True, **kw)

    def set(self, value, style=None):
        self.value = value
        if style:
            self.style = style
        self._draw()


class LabeledSection(tk.Frame):
    def __init__(self, parent, title, color=ACCENT, **kwargs):
        super().__init__(parent, bg=CARD, **kwargs)
        hdr = tk.Frame(self, bg=CARD)
        hdr.pack(fill="x", padx=8, pady=(5, 2))
        tk.Label(hdr, text="▶", font=("Courier New", 8), bg=CARD, fg=color).pack(side="left")
        tk.Label(hdr, text=f"  {title}", font=FONT_HEAD, bg=CARD, fg=color).pack(side="left")
        self.body = tk.Frame(self, bg=CARD)
        self.body.pack(fill="both", expand=True, padx=8, pady=(0, 5))


class FormulaLine(tk.Frame):
    def __init__(self, parent, formula, result_ok=None, **kwargs):
        super().__init__(parent, bg=BG3, **kwargs)
        color = GREEN if result_ok is True else (RED if result_ok is False else TEXT2)
        tk.Label(self, text=formula, font=FONT_BODY, bg=BG3, fg=color,
                 anchor="w", padx=6, pady=2).pack(fill="x")


# ─────────────────────────────────────────────
# APPLICATION PRINCIPALE
# ─────────────────────────────────────────────

class HammingSatelliteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulation Hamming(7,4) — Liaison Satellite")
        self.configure(bg=BG)
        self.resizable(True, True)

        # État onglet 1
        self.data_bits      = [1, 0, 1, 1]
        self.codeword       = [0]*7
        self.received       = [0]*7
        self.corrected_bits = [0]*7
        self.syndrome       = 0
        self.decoded        = [0]*4
        self.step_delay     = 500
        self.speed_var      = tk.IntVar(value=2)

        # État onglet 2
        self.text_input_var = tk.StringVar(value="HELLO")
        self.text_noise_var = tk.DoubleVar(value=0.15)

        self._build_ui()
        self._run_simulation()

    # ═══════════════════════════════════════════
    # UI PRINCIPALE
    # ═══════════════════════════════════════════

    def _build_ui(self):
        # Titre
        tb = tk.Frame(self, bg=BG, pady=8)
        tb.pack(fill="x", padx=16)
        tk.Label(tb, text="◈  HAMMING(7,4) SIMULATION PAR SATELLITE",
                 font=FONT_TITLE, bg=BG, fg=ACCENT).pack(side="left")
        tk.Label(tb, text="Eutelsat 5W · 14.25 GHz · 35 786 km",
                 font=FONT_SMALL, bg=BG, fg=TEXT3).pack(side="right")
        tk.Frame(self, bg=ACCENT, height=1).pack(fill="x", padx=16)

        # Onglets
        tab_bar = tk.Frame(self, bg=BG, pady=4)
        tab_bar.pack(fill="x", padx=16)
        self._tab_bit_btn = tk.Button(
            tab_bar, text="  ⬡  BIT UNIQUE  ", font=FONT_SMALL,
            relief="flat", cursor="hand2", bg=ACCENT, fg="white",
            padx=10, pady=3, command=self._show_tab_bit)
        self._tab_bit_btn.pack(side="left", padx=(0, 4))
        self._tab_txt_btn = tk.Button(
            tab_bar, text="  ✦  TRANSMISSION TEXTE  ", font=FONT_SMALL,
            relief="flat", cursor="hand2", bg=BG3, fg=TEXT2,
            padx=10, pady=3, command=self._show_tab_text)
        self._tab_txt_btn.pack(side="left")

        # Conteneur
        self._container = tk.Frame(self, bg=BG)
        self._container.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        # ── Onglet 1 ─────────────────────────────
        self._frame_bit = tk.Frame(self._container, bg=BG)
        bit_canvas = tk.Canvas(self._frame_bit, bg=BG, highlightthickness=0)
        bit_vsb = tk.Scrollbar(self._frame_bit, orient="vertical", command=bit_canvas.yview)
        bit_canvas.configure(yscrollcommand=bit_vsb.set)
        bit_vsb.pack(side="right", fill="y")
        bit_canvas.pack(side="left", fill="both", expand=True)
        bit_inner = tk.Frame(bit_canvas, bg=BG)
        self._bit_win = bit_canvas.create_window((0, 0), window=bit_inner, anchor="nw")
        bit_inner.bind("<Configure>", lambda e: bit_canvas.configure(
            scrollregion=bit_canvas.bbox("all")))
        bit_canvas.bind("<Configure>", lambda e: bit_canvas.itemconfig(
            self._bit_win, width=e.width))
        bit_canvas.bind("<MouseWheel>", lambda e: bit_canvas.yview_scroll(
            -1*(e.delta//120), "units"))
        left  = tk.Frame(bit_inner, bg=BG)
        right = tk.Frame(bit_inner, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 6))
        right.pack(side="left", fill="both", expand=True, padx=(6, 0))
        self._build_input(left)
        self._build_encoding(left)
        self._build_channel(left)
        self._build_syndrome(right)
        self._build_correction(right)
        self._build_result(right)
        self._build_controls(right)
        self._build_stats(right)

        # ── Onglet 2 ─────────────────────────────
        self._frame_txt = tk.Frame(self._container, bg=BG)
        self._build_text_tab(self._frame_txt)

        self._frame_bit.pack(fill="both", expand=True)

    def _show_tab_bit(self):
        self._frame_txt.pack_forget()
        self._frame_bit.pack(fill="both", expand=True)
        self._tab_bit_btn.config(bg=ACCENT,  fg="white")
        self._tab_txt_btn.config(bg=BG3,     fg=TEXT2)

    def _show_tab_text(self):
        self._frame_bit.pack_forget()
        self._frame_txt.pack(fill="both", expand=True)
        self._tab_txt_btn.config(bg=ACCENT2, fg=BG)
        self._tab_bit_btn.config(bg=BG3,     fg=TEXT2)

    # ═══════════════════════════════════════════
    # ONGLET 1 — BIT UNIQUE
    # ═══════════════════════════════════════════

    def _build_input(self, parent):
        sec = LabeledSection(parent, "DONNÉES SOURCE", color=TEAL)
        sec.pack(fill="x", pady=(0, 4))
        row = tk.Frame(sec.body, bg=CARD)
        row.pack(fill="x", pady=2)
        tk.Label(row, text="Valeur :", font=FONT_BODY, bg=CARD, fg=TEXT2).pack(side="left")
        self.input_var = tk.StringVar(value="1011")
        entry = tk.Entry(row, textvariable=self.input_var, font=FONT_MONO,
                         bg=BG3, fg=ACCENT2, insertbackground=ACCENT2,
                         relief="flat", width=10, bd=0)
        entry.pack(side="left", padx=6, ipady=3)
        entry.bind("<Return>", lambda e: self._on_input_change())
        tk.Button(row, text="SIMULER →", font=FONT_SMALL,
                  bg=ACCENT, fg="white", relief="flat", cursor="hand2",
                  padx=8, pady=2, command=self._on_input_change).pack(side="right")
        self.input_info = tk.Label(sec.body, text="", font=FONT_SMALL, bg=CARD, fg=AMBER)
        self.input_info.pack(anchor="w", pady=1)
        bits_row = tk.Frame(sec.body, bg=CARD)
        bits_row.pack(anchor="w", pady=2)
        tk.Label(bits_row, text="Bits d1 d2 d3 d4 :", font=FONT_SMALL,
                 bg=CARD, fg=TEXT2, width=18, anchor="w").pack(side="left")
        self.data_cells = []
        for _ in range(4):
            c = BitCell(bits_row, value=0, style="data", size=44)
            c.pack(side="left", padx=2)
            self.data_cells.append(c)
        self.decimal_label = tk.Label(bits_row, text="= 11₁₀",
                                       font=FONT_MONO, bg=CARD, fg=TEAL)
        self.decimal_label.pack(side="left", padx=8)

    def _build_encoding(self, parent):
        sec = LabeledSection(parent, "ENCODAGE HAMMING(7,4)", color=PURPLE)
        sec.pack(fill="x", pady=(0, 4))
        self.parity_frame = tk.Frame(sec.body, bg=CARD)
        self.parity_frame.pack(fill="x", pady=2)
        word_row = tk.Frame(sec.body, bg=CARD)
        word_row.pack(anchor="w", pady=2)
        tk.Label(word_row, text="Mot émis x(7) :", font=FONT_SMALL,
                 bg=CARD, fg=TEXT2, width=18, anchor="w").pack(side="left")
        self.tx_cells = []
        col = tk.Frame(word_row, bg=CARD); col.pack(side="left")
        lr  = tk.Frame(col, bg=CARD); lr.pack()
        cr  = tk.Frame(col, bg=CARD); cr.pack()
        for i, lbl in enumerate(["p₁","p₂","d₁","p₃","d₂","d₃","d₄"]):
            st = "parity" if i in (0, 1, 3) else "data"
            tk.Label(lr, text=lbl, font=("Courier New", 8), bg=CARD,
                     fg=BIT_PARITY_FG if st=="parity" else BIT_DATA_FG,
                     width=4).pack(side="left", padx=2)
            c = BitCell(cr, value=0, style=st, size=44)
            c.pack(side="left", padx=2)
            self.tx_cells.append(c)
        tk.Label(sec.body, text="Rendement : 4/7 ≈ 57 %",
                 font=FONT_SMALL, bg=CARD, fg=TEXT3).pack(anchor="w", pady=1)

    def _build_channel(self, parent):
        sec = LabeledSection(parent, "CANAL SATELLITE", color=AMBER)
        sec.pack(fill="x", pady=(0, 4))
        params = tk.Frame(sec.body, bg=CARD)
        params.pack(fill="x", pady=2)
        for txt, val, col in [
            ("Distance :", "35 786 km", TEXT),
            ("Fréquence :", "14,25 GHz (Ku)", TEXT),
            ("Délai :", "≈ 119 ms", AMBER),
            ("FSPL :", "≈ 206 dB", RED),
            ("Eb/N₀ :", "6 dB", GREEN),
        ]:
            r = tk.Frame(params, bg=CARD); r.pack(side="left", padx=8)
            tk.Label(r, text=txt, font=FONT_SMALL, bg=CARD, fg=TEXT3).pack()
            tk.Label(r, text=val, font=("Courier New", 10, "bold"), bg=CARD, fg=col).pack()
        err_ctrl = tk.Frame(sec.body, bg=CARD)
        err_ctrl.pack(fill="x", pady=2)
        tk.Label(err_ctrl, text="Simuler erreur pos. :", font=FONT_BODY,
                 bg=CARD, fg=TEXT2).pack(side="left")
        self.error_pos_var = tk.IntVar(value=0)
        tk.Spinbox(err_ctrl, from_=0, to=7, textvariable=self.error_pos_var,
                   font=FONT_MONO, bg=BG3, fg=RED, buttonbackground=BG3,
                   relief="flat", width=3, command=self._on_error_change
                   ).pack(side="left", padx=6, ipady=2)
        tk.Label(err_ctrl, text="(0 = aucune)", font=FONT_SMALL,
                 bg=CARD, fg=TEXT3).pack(side="left")
        tk.Button(err_ctrl, text="Aléatoire", font=FONT_SMALL,
                  bg=BG3, fg=AMBER, relief="flat", cursor="hand2",
                  padx=6, command=self._random_error).pack(side="left", padx=6)
        rx_row = tk.Frame(sec.body, bg=CARD)
        rx_row.pack(anchor="w", pady=2)
        tk.Label(rx_row, text="Mot reçu y(7) :", font=FONT_SMALL,
                 bg=CARD, fg=TEXT2, width=18, anchor="w").pack(side="left")
        self.rx_cells = []
        for i in range(7):
            st = "parity" if i in (0, 1, 3) else "data"
            c = BitCell(rx_row, value=0, style=st, size=44)
            c.pack(side="left", padx=2)
            self.rx_cells.append(c)
        self.error_label = tk.Label(sec.body, text="Aucune erreur",
                                     font=FONT_SMALL, bg=CARD, fg=TEXT3)
        self.error_label.pack(anchor="w", pady=1)

    def _build_syndrome(self, parent):
        sec = LabeledSection(parent, "CALCUL DU SYNDROME", color=RED)
        sec.pack(fill="x", pady=(0, 4))
        self.syn_frame = tk.Frame(sec.body, bg=CARD)
        self.syn_frame.pack(fill="x", pady=2)
        res_row = tk.Frame(sec.body, bg=BG3)
        res_row.pack(fill="x", pady=2)
        self.syn_result = tk.Label(
            res_row, text="Syndrome = (0 0 0)₂ = 0 → Aucune erreur",
            font=FONT_BODY, bg=BG3, fg=GREEN, pady=4, padx=6)
        self.syn_result.pack(fill="x")

    def _build_correction(self, parent):
        sec = LabeledSection(parent, "CORRECTION & EXTRACTION", color=GREEN)
        sec.pack(fill="x", pady=(0, 4))
        corr_row = tk.Frame(sec.body, bg=CARD)
        corr_row.pack(anchor="w", pady=2)
        tk.Label(corr_row, text="Mot corrigé y :", font=FONT_SMALL,
                 bg=CARD, fg=TEXT2, width=18, anchor="w").pack(side="left")
        self.corr_cells = []
        for i in range(7):
            st = "parity" if i in (0, 1, 3) else "data"
            c = BitCell(corr_row, value=0, style=st, size=44)
            c.pack(side="left", padx=2)
            self.corr_cells.append(c)
        data_row = tk.Frame(sec.body, bg=CARD)
        data_row.pack(anchor="w", pady=2)
        tk.Label(data_row, text="Données extraites :", font=FONT_SMALL,
                 bg=CARD, fg=TEXT2, width=18, anchor="w").pack(side="left")
        self.out_cells = []
        for _ in range(4):
            c = BitCell(data_row, value=0, style="data", size=44)
            c.pack(side="left", padx=2)
            self.out_cells.append(c)
        self.corr_label = tk.Label(sec.body, text="", font=FONT_SMALL, bg=CARD, fg=TEXT3)
        self.corr_label.pack(anchor="w", pady=1)

    def _build_result(self, parent):
        sec = LabeledSection(parent, "RÉSULTAT FINAL", color=ACCENT2)
        sec.pack(fill="x", pady=(0, 4))
        rb = tk.Frame(sec.body, bg=BG3)
        rb.pack(fill="x", pady=2)
        self.result_big = tk.Label(rb, text="✓ MESSAGE INTACT",
                                    font=FONT_BIG, bg=BG3, fg=GREEN, pady=6)
        self.result_big.pack()
        row2 = tk.Frame(rb, bg=BG3)
        row2.pack(pady=(0, 6))
        self.orig_label = tk.Label(row2, text="Original    : 1011",
                                    font=FONT_MONO, bg=BG3, fg=TEXT2)
        self.orig_label.pack(side="left", padx=12)
        self.recon_label = tk.Label(row2, text="Reconstruit : 1011",
                                     font=FONT_MONO, bg=BG3, fg=ACCENT2)
        self.recon_label.pack(side="left", padx=12)

    def _build_controls(self, parent):
        sec = LabeledSection(parent, "CONTRÔLES", color=ACCENT)
        sec.pack(fill="x", pady=(0, 4))
        row = tk.Frame(sec.body, bg=CARD)
        row.pack(fill="x", pady=2)
        for text, cmd, color in [
            ("⟳ RESET",     self._reset,       TEXT3),
            ("⚡ ALÉATOIRE", self._random_demo, AMBER),
        ]:
            tk.Button(row, text=text, font=FONT_SMALL, bg=color, fg="white",
                      relief="flat", cursor="hand2", padx=10, pady=4,
                      command=cmd).pack(side="left", padx=4)
        speed_row = tk.Frame(sec.body, bg=CARD)
        speed_row.pack(fill="x", pady=2)
        tk.Label(speed_row, text="Vitesse :", font=FONT_SMALL,
                 bg=CARD, fg=TEXT2).pack(side="left")
        for lbl, val in [("Lente", 1), ("Normale", 2), ("Rapide", 3)]:
            tk.Radiobutton(speed_row, text=lbl, variable=self.speed_var, value=val,
                           font=FONT_SMALL, bg=CARD, fg=TEXT2, selectcolor=BG3,
                           activebackground=CARD,
                           command=self._update_speed).pack(side="left", padx=5)

    def _build_stats(self, parent):
        sec = LabeledSection(parent, "STATISTIQUES DE SESSION", color=TEXT3)
        sec.pack(fill="x", pady=(0, 4))
        self.stats = {"total": 0, "errors": 0, "corrected": 0}
        grid = tk.Frame(sec.body, bg=CARD)
        grid.pack(fill="x", pady=2)
        self.stat_labels = {}
        for col, (key, label, color) in enumerate([
            ("total",     "Transmissions", TEXT),
            ("errors",    "Erreurs",        RED),
            ("corrected", "Corrigées",      GREEN),
        ]):
            f = tk.Frame(grid, bg=BG3, padx=10, pady=2)
            f.grid(row=0, column=col, padx=3, sticky="ew")
            grid.columnconfigure(col, weight=1)
            tk.Label(f, text=label, font=FONT_SMALL, bg=BG3, fg=TEXT3).pack()
            lbl = tk.Label(f, text="0", font=("Courier New", 18, "bold"),
                           bg=BG3, fg=color)
            lbl.pack()
            self.stat_labels[key] = lbl

    # ═══════════════════════════════════════════
    # ONGLET 2 — TRANSMISSION TEXTE
    # ═══════════════════════════════════════════

    def _build_text_tab(self, parent):
        # Saisie
        sec_in = LabeledSection(parent, "MESSAGE TEXTE À TRANSMETTRE", color=TEAL)
        sec_in.pack(fill="x", pady=(0, 4))
        row = tk.Frame(sec_in.body, bg=CARD)
        row.pack(fill="x", pady=2)
        tk.Label(row, text="Texte :", font=FONT_BODY, bg=CARD, fg=TEXT2).pack(side="left")
        entry = tk.Entry(row, textvariable=self.text_input_var, font=FONT_MONO,
                         bg=BG3, fg=ACCENT2, insertbackground=ACCENT2,
                         relief="flat", width=30, bd=0)
        entry.pack(side="left", padx=6, ipady=3)
        entry.bind("<Return>", lambda e: self._run_text_simulation())
        noise_row = tk.Frame(sec_in.body, bg=CARD)
        noise_row.pack(fill="x", pady=2)
        tk.Label(noise_row, text="Taux d'erreur (BER) :",
                 font=FONT_SMALL, bg=CARD, fg=TEXT2).pack(side="left")
        tk.Scale(noise_row, variable=self.text_noise_var, from_=0.0, to=0.5,
                 resolution=0.01, orient="horizontal", length=180,
                 bg=CARD, fg=ACCENT2, troughcolor=BG3,
                 highlightthickness=0).pack(side="left", padx=6)
        self.ber_label = tk.Label(noise_row, text="15 %", font=FONT_SMALL,
                                   bg=CARD, fg=AMBER)
        self.ber_label.pack(side="left")
        self.text_noise_var.trace_add("write", self._update_ber_label)
        tk.Button(sec_in.body, text="  ▶  TRANSMETTRE  ", font=FONT_SMALL,
                  bg=ACCENT2, fg=BG, relief="flat", cursor="hand2",
                  padx=10, pady=4,
                  command=self._run_text_simulation).pack(anchor="w", pady=4)

        # Bandeau résumé
        self.txt_summary_frame = tk.Frame(parent, bg=BG3)
        self.txt_summary_frame.pack(fill="x", pady=(0, 4))
        self.txt_result_big = tk.Label(self.txt_summary_frame, text="—",
                                        font=FONT_BIG, bg=BG3, fg=TEXT3, pady=4)
        self.txt_result_big.pack(side="left", padx=12)
        self.txt_orig_lbl = tk.Label(self.txt_summary_frame, text="",
                                      font=FONT_MONO, bg=BG3, fg=TEXT2)
        self.txt_orig_lbl.pack(side="left", padx=6)
        self.txt_recon_lbl = tk.Label(self.txt_summary_frame, text="",
                                       font=FONT_MONO, bg=BG3, fg=ACCENT2)
        self.txt_recon_lbl.pack(side="left", padx=6)

        # Zone scrollable
        outer = tk.Frame(parent, bg=BG)
        outer.pack(fill="both", expand=True)
        self.txt_scroll_canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        vsb = tk.Scrollbar(outer, orient="vertical",
                           command=self.txt_scroll_canvas.yview)
        hsb = tk.Scrollbar(outer, orient="horizontal",
                           command=self.txt_scroll_canvas.xview)
        self.txt_scroll_canvas.configure(yscrollcommand=vsb.set,
                                          xscrollcommand=hsb.set)
        vsb.pack(side="right",  fill="y")
        hsb.pack(side="bottom", fill="x")
        self.txt_scroll_canvas.pack(side="left", fill="both", expand=True)
        self.txt_cards_frame = tk.Frame(self.txt_scroll_canvas, bg=BG)
        self.txt_scroll_canvas.create_window(
            (0, 0), window=self.txt_cards_frame, anchor="nw")
        self.txt_cards_frame.bind(
            "<Configure>",
            lambda e: self.txt_scroll_canvas.configure(
                scrollregion=self.txt_scroll_canvas.bbox("all")))
        self.txt_scroll_canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.txt_scroll_canvas.yview_scroll(
                -1*(e.delta//120), "units"))

    def _update_ber_label(self, *_):
        self.ber_label.config(text=f"{int(self.text_noise_var.get()*100)} %")

    def _run_text_simulation(self):
        text = self.text_input_var.get()
        if not text:
            return
        ber = self.text_noise_var.get()
        frames_encoded = encode_text(text)

        # Bruit aléatoire
        frames_received = []
        for ch, nib, data4, cw in frames_encoded:
            rx = cw[:]
            for i in range(7):
                if random.random() < ber:
                    rx[i] ^= 1
            frames_received.append((ch, nib, data4, cw, rx))

        # Décodage
        decoded_nibbles = []
        for ch, nib, data4, cw, rx in frames_received:
            corrected, syndrome, dec4 = decode_hamming(rx)
            s1, s2, s3 = compute_syndrome(rx)
            decoded_nibbles.append({
                "char_orig": ch, "nibble": nib,
                "data4": data4, "cw": cw, "rx": rx,
                "corrected": corrected, "syndrome": syndrome,
                "dec4": dec4, "s1": s1, "s2": s2, "s3": s3,
            })

        # Reconstitution du texte
        recon_chars = []
        for i in range(0, len(decoded_nibbles), 2):
            bits8 = decoded_nibbles[i]["dec4"] + decoded_nibbles[i+1]["dec4"]
            recon_chars.append(bits8_to_char(bits8))
        recon = ''.join(recon_chars)

        # Résumé
        ok = (recon == text)
        self.txt_orig_lbl.config(text=f"Original : {text}")
        self.txt_recon_lbl.config(text=f"→  Reçu : {recon}", fg=GREEN if ok else RED)
        if ok:
            self.txt_result_big.config(text="✓ TEXTE INTACT", fg=GREEN)
        else:
            diffs = sum(1 for a, b in zip(text, recon) if a != b)
            self.txt_result_big.config(text=f"⚠ {diffs} CAR. ALTÉRÉ(S)", fg=RED)

        # Effacer les anciennes cartes
        for w in self.txt_cards_frame.winfo_children():
            w.destroy()

        # Cartes détaillées
        POS_LBLS = ["p₁","p₂","d₁","p₃","d₂","d₃","d₄"]
        BS  = 34
        F8  = ("Courier New", 8)
        F8B = ("Courier New", 8, "bold")
        COLS = 4

        def make_bit_row(parent, label, bits_list, styles, size=BS):
            row = tk.Frame(parent, bg=CARD)
            row.pack(anchor="w", pady=1)
            tk.Label(row, text=label, font=F8, bg=CARD, fg=TEXT3,
                     width=14, anchor="w").pack(side="left")
            wrap = tk.Frame(row, bg=CARD); wrap.pack(side="left")
            cell_r = tk.Frame(wrap, bg=CARD); cell_r.pack()
            pos_r  = tk.Frame(wrap, bg=CARD); pos_r.pack()
            for i, (b, st) in enumerate(zip(bits_list, styles)):
                BitCell(cell_r, value=b, style=st, size=size).pack(side="left", padx=1)
                lc = (BIT_PARITY_FG if "parity" in st
                      else BIT_DATA_FG if "data" in st
                      else GREEN if st == "fixed" else TEXT3)
                tk.Label(pos_r, text=POS_LBLS[i], font=("Courier New", 7),
                         bg=CARD, fg=lc, width=4).pack(side="left", padx=1)

        for idx, nd in enumerate(decoded_nibbles):
            ch    = nd["char_orig"]
            nib   = nd["nibble"]
            cw    = nd["cw"]
            rx    = nd["rx"]
            corr  = nd["corrected"]
            syn   = nd["syndrome"]
            data4 = nd["data4"]
            dec4  = nd["dec4"]
            d1, d2, d3, d4 = data4
            p1, p2, p3     = cw[0], cw[1], cw[3]
            s1, s2, s3v    = nd["s1"], nd["s2"], nd["s3"]
            nib_ok = (dec4 == data4)
            ch_idx = idx // 2 + 1

            card = tk.Frame(self.txt_cards_frame, bg=CARD,
                            highlightbackground=BORDER, highlightthickness=1)
            card.grid(row=idx // COLS, column=idx % COLS,
                      padx=4, pady=4, sticky="n")

            # En-tête
            hdr_col = TEAL if nib == 0 else PURPLE
            hdr = tk.Frame(card, bg=hdr_col); hdr.pack(fill="x")
            tk.Label(hdr, text=f" #{ch_idx} '{ch}' ASC={ord(ch)}",
                     font=("Courier New", 9, "bold"), bg=hdr_col, fg=BG,
                     pady=2, padx=4).pack(side="left")
            tk.Label(hdr, text=f" {'HAUT' if nib==0 else 'BAS '} ",
                     font=("Courier New", 8), bg=hdr_col, fg=BG).pack(side="right")

            body = tk.Frame(card, bg=CARD, padx=5, pady=3)
            body.pack(fill="both")

            # ① Données
            tk.Label(body, text="① DONNÉES", font=F8B, bg=CARD, fg=TEAL).pack(anchor="w")
            sr = tk.Frame(body, bg=CARD); sr.pack(anchor="w")
            tk.Label(sr, text="d1 d2 d3 d4 :", font=F8, bg=CARD, fg=TEXT3,
                     width=14, anchor="w").pack(side="left")
            for b in data4:
                BitCell(sr, value=b, style="data", size=BS).pack(side="left", padx=1)
            tk.Label(sr, text=f"= {bits_to_decimal(data4)}",
                     font=F8B, bg=CARD, fg=TEAL).pack(side="left", padx=4)

            tk.Frame(body, bg=BORDER, height=1).pack(fill="x", pady=2)

            # ② Encodage
            tk.Label(body, text="② ENCODAGE", font=F8B, bg=CARD, fg=PURPLE).pack(anchor="w")
            for txt_f, val in [
                (f"p₁={d1}⊕{d2}⊕{d4}={p1}", p1==0),
                (f"p₂={d1}⊕{d3}⊕{d4}={p2}", p2==0),
                (f"p₃={d2}⊕{d3}⊕{d4}={p3}", p3==0),
            ]:
                FormulaLine(body, txt_f, result_ok=val).pack(fill="x", pady=0)
            make_bit_row(body, "Émis x(7) :", cw,
                         ["parity","parity","data","parity","data","data","data"])

            tk.Frame(body, bg=BORDER, height=1).pack(fill="x", pady=2)

            # ③ Canal
            tk.Label(body, text="③ CANAL", font=F8B, bg=CARD, fg=AMBER).pack(anchor="w")
            rx_styles = [
                "error" if rx[i] != cw[i]
                else ("parity" if i in (0,1,3) else "data")
                for i in range(7)
            ]
            make_bit_row(body, "Reçu y(7) :", rx, rx_styles)
            err_bits = [i+1 for i in range(7) if rx[i] != cw[i]]
            tk.Label(body,
                     text=f"⚠ pos {err_bits}" if err_bits else "✓ Sans erreur",
                     font=F8, bg=CARD,
                     fg=RED if err_bits else GREEN).pack(anchor="w")

            tk.Frame(body, bg=BORDER, height=1).pack(fill="x", pady=2)

            # ④ Syndrome
            tk.Label(body, text="④ SYNDROME", font=F8B, bg=CARD, fg=RED).pack(anchor="w")
            y = rx
            for txt_f, val in [
                (f"s₁=y₁⊕y₃⊕y₅⊕y₇={y[0]}⊕{y[2]}⊕{y[4]}⊕{y[6]}={s1}", s1==0),
                (f"s₂=y₂⊕y₃⊕y₆⊕y₇={y[1]}⊕{y[2]}⊕{y[5]}⊕{y[6]}={s2}", s2==0),
                (f"s₃=y₄⊕y₅⊕y₆⊕y₇={y[3]}⊕{y[4]}⊕{y[5]}⊕{y[6]}={s3v}", s3v==0),
            ]:
                FormulaLine(body, txt_f, result_ok=val).pack(fill="x", pady=0)
            if syn == 0:
                syn_txt, syn_col = f"({s3v}{s2}{s1})₂=0 → OK ✓", GREEN
            else:
                syn_txt, syn_col = f"({s3v}{s2}{s1})₂={syn} → pos {syn}", RED
            tk.Label(body, text=syn_txt, font=F8B, bg=BG3,
                     fg=syn_col, pady=2, padx=4).pack(fill="x", pady=1)

            tk.Frame(body, bg=BORDER, height=1).pack(fill="x", pady=2)

            # ⑤ Correction
            tk.Label(body, text="⑤ CORRECTION", font=F8B, bg=CARD, fg=GREEN).pack(anchor="w")
            corr_styles = [
                "fixed"  if i == syn-1 and syn != 0
                else "parity" if i in (0,1,3)
                else "data"
                for i in range(7)
            ]
            make_bit_row(body, "Corrigé ĉ :", corr, corr_styles)
            if syn != 0:
                tk.Label(body, text=f"Bit {syn}: {rx[syn-1]}→{corr[syn-1]} ✓",
                         font=F8, bg=CARD, fg=GREEN).pack(anchor="w")
            orw = tk.Frame(body, bg=CARD); orw.pack(anchor="w", pady=1)
            tk.Label(orw, text="Données d̂ :", font=F8, bg=CARD, fg=TEXT3,
                     width=14, anchor="w").pack(side="left")
            for b in dec4:
                BitCell(orw, value=b, style="data", size=BS).pack(side="left", padx=1)
            tk.Label(orw, text=f"= {bits_to_decimal(dec4)}",
                     font=F8B, bg=CARD, fg=TEAL).pack(side="left", padx=4)

            tk.Frame(body, bg=BORDER, height=1).pack(fill="x", pady=2)

            # ⑥ Verdict
            tk.Label(body,
                     text="✓ INTACT" if nib_ok else "✗ ALTÉRÉ",
                     font=("Courier New", 10, "bold"), bg=CARD,
                     fg=GREEN if nib_ok else RED, pady=2).pack(anchor="center")

    # ═══════════════════════════════════════════
    # LOGIQUE SIMULATION BIT UNIQUE
    # ═══════════════════════════════════════════

    def _update_speed(self):
        self.step_delay = {1: 900, 2: 500, 3: 150}[self.speed_var.get()]

    def _on_input_change(self):
        val = self.input_var.get().strip()
        bits, info = None, ""
        if len(val) == 4 and all(c in "01" for c in val):
            bits = [int(c) for c in val]
            info = f"Binaire : {val} = {bits_to_decimal(bits)} décimal"
        elif val.isdigit() and 0 <= int(val) <= 15:
            n = int(val)
            bits = decimal_to_bits4(n)
            info = f"Décimal {n} → binaire : {''.join(map(str, bits))}"
        elif len(val) == 1 and val.isalpha():
            bits = char_to_bits4(val)
            info = f"'{val.upper()}' ASCII={ord(val.upper())} → 4 LSB : {''.join(map(str, bits))}"
        else:
            self.input_info.config(text="Format non reconnu (ex: 1011, 7, ou A)", fg=RED)
            return
        self.input_info.config(text=info, fg=AMBER)
        self.data_bits = bits
        self._run_simulation()

    def _on_error_change(self):
        self._run_simulation()

    def _random_error(self):
        self.error_pos_var.set(random.randint(1, 7))
        self._run_simulation()

    def _random_demo(self):
        self.input_var.set(str(random.randint(0, 15)))
        self.error_pos_var.set(random.randint(1, 7))
        self._on_input_change()

    def _reset(self):
        self.input_var.set("1011")
        self.error_pos_var.set(0)
        self.stats = {"total": 0, "errors": 0, "corrected": 0}
        for lbl in self.stat_labels.values():
            lbl.config(text="0")
        self.input_info.config(text="")
        self._on_input_change()

    def _run_simulation(self):
        val = self.input_var.get().strip()
        if len(val) == 4 and all(c in "01" for c in val):
            self.data_bits = [int(c) for c in val]
        elif val.isdigit() and 0 <= int(val) <= 15:
            self.data_bits = decimal_to_bits4(int(val))
        elif len(val) == 1 and val.isalpha():
            self.data_bits = char_to_bits4(val)
        if hasattr(self, "speed_var"):
            self._update_speed()
        bits = self.data_bits
        err  = self.error_pos_var.get()
        cw   = encode_hamming(bits)
        rx   = introduce_error(cw, err)
        corrected, syndrome, decoded = decode_hamming(rx)
        s1, s2, s3 = compute_syndrome(rx)
        self.codeword       = cw
        self.received       = rx
        self.corrected_bits = corrected
        self.syndrome       = syndrome
        self.decoded        = decoded
        self._animate(bits, cw, rx, corrected, syndrome, decoded, s1, s2, s3, err)
        self.stats["total"] += 1
        if err != 0:
            self.stats["errors"] += 1
        if err != 0 and decoded == bits:
            self.stats["corrected"] += 1
        for k, lbl in self.stat_labels.items():
            lbl.config(text=str(self.stats[k]))

    def _animate(self, bits, cw, rx, corrected, syndrome,
                 decoded, s1, s2, s3, err):
        d = self.step_delay

        def step1():
            for i, b in enumerate(bits):
                self.data_cells[i].set(b, "data")
            self.decimal_label.config(text=f"= {bits_to_decimal(bits)}₁₀")
            self.after(d, step2)

        def step2():
            for w in self.parity_frame.winfo_children():
                w.destroy()
            p1, p2, p3 = cw[0], cw[1], cw[3]
            d1, d2, d3, d4 = bits
            for txt, ok in [
                (f"p₁ = d₁⊕d₂⊕d₄ = {d1}⊕{d2}⊕{d4} = {p1}", p1==0),
                (f"p₂ = d₁⊕d₃⊕d₄ = {d1}⊕{d3}⊕{d4} = {p2}", p2==0),
                (f"p₃ = d₂⊕d₃⊕d₄ = {d2}⊕{d3}⊕{d4} = {p3}", p3==0),
            ]:
                FormulaLine(self.parity_frame, txt, result_ok=ok).pack(fill="x", pady=1)
            for i, b in enumerate(cw):
                self.tx_cells[i].set(b, "parity" if i in (0,1,3) else "data")
            self.after(d, step3)

        def step3():
            for i, b in enumerate(rx):
                st = ("error" if err == i+1
                      else "parity" if i in (0,1,3) else "data")
                self.rx_cells[i].set(b, st)
            if err == 0:
                self.error_label.config(text="Signal transmis sans erreur ✓", fg=GREEN)
            else:
                self.error_label.config(
                    text=f"⚠ Erreur en position {err} : x[{err}]={cw[err-1]} → y[{err}]={rx[err-1]}",
                    fg=RED)
            self.after(d, step4)

        def step4():
            for w in self.syn_frame.winfo_children():
                w.destroy()
            y = rx
            for txt, ok in [
                (f"s₁ = y₁⊕y₃⊕y₅⊕y₇ = {y[0]}⊕{y[2]}⊕{y[4]}⊕{y[6]} = {s1}", s1==0),
                (f"s₂ = y₂⊕y₃⊕y₆⊕y₇ = {y[1]}⊕{y[2]}⊕{y[5]}⊕{y[6]} = {s2}", s2==0),
                (f"s₃ = y₄⊕y₅⊕y₆⊕y₇ = {y[3]}⊕{y[4]}⊕{y[5]}⊕{y[6]} = {s3}", s3==0),
            ]:
                FormulaLine(self.syn_frame, txt, result_ok=ok).pack(fill="x", pady=1)
            if syndrome == 0:
                self.syn_result.config(
                    text=f"Syndrome = ({s3} {s2} {s1})₂ = 0  →  Aucune erreur ✓",
                    fg=GREEN)
            else:
                self.syn_result.config(
                    text=f"Syndrome = ({s3} {s2} {s1})₂ = {syndrome}₁₀  →  Erreur position {syndrome}",
                    fg=RED)
            self.after(d, step5)

        def step5():
            for i, b in enumerate(corrected):
                if i == syndrome-1 and syndrome != 0:
                    st = "fixed"
                elif i in (0,1,3):
                    st = "parity"
                else:
                    st = "data"
                self.corr_cells[i].set(b, st)
            for i, b in enumerate(decoded):
                self.out_cells[i].set(b, "data")
            if syndrome != 0 and err != 0:
                self.corr_label.config(
                    text=f"Bit {syndrome} corrigé : {rx[syndrome-1]} → {corrected[syndrome-1]} ✓",
                    fg=GREEN)
            elif syndrome == 0:
                self.corr_label.config(text="Aucune correction nécessaire", fg=TEXT3)
            else:
                self.corr_label.config(text="Correction appliquée", fg=AMBER)
            self.after(d, step6)

        def step6():
            ok        = decoded == bits
            dec_orig  = bits_to_decimal(bits)
            dec_recon = bits_to_decimal(decoded)
            self.result_big.config(
                text="✓ MESSAGE INTACT" if ok else "✗ ERREUR NON CORRIGÉE",
                fg=GREEN if ok else RED)
            self.orig_label.config(
                text=f"Original    : {''.join(map(str,bits))} = {dec_orig}")
            self.recon_label.config(
                text=f"Reconstruit : {''.join(map(str,decoded))} = {dec_recon}",
                fg=GREEN if ok else RED)

        self.after(0, step1)


# ─────────────────────────────────────────────
# ENTRÉE PRINCIPALE
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app = HammingSatelliteApp()
    sw = app.winfo_screenwidth()
    sh = app.winfo_screenheight()
    w  = min(1200, int(sw * 0.94))
    h  = min(900,  int(sh * 0.94))
    x  = (sw - w) // 2
    y  = max(0, (sh - h) // 2 - 20)
    app.geometry(f"{w}x{h}+{x}+{y}")
    app.minsize(860, 580)
    app.mainloop()