# Copyright (C) 2026 Murilo Gomes Julio
# SPDX-License-Identifier: GPL-2.0-only

import threading
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from sync_client import ping, download, upload
from sync_server import start_server, obter_ip_local


class SyncClientWindow:
    def __init__(self):
        self._running = False
        self._sv_server = None
        self._sv_thread = None

    def show_window(self):
        self.win = ttk.Toplevel()
        self.win.title("Sincronizar com outro PC")
        self.win.geometry("520x620")
        self.win.position_center()
        self.win.resizable(False, False)

        main_frame = ttk.Frame(self.win, padding=20)
        main_frame.pack(fill="both", expand=True)

        # ── SERVIDOR LOCAL ──
        ttk.Label(main_frame, text="Servidor Local",
                  font=("Helvetica", 16, "bold")).pack(anchor="w")
        ttk.Separator(main_frame).pack(fill="x", pady=5)

        # IP local (auto)
        frame_ip = ttk.Frame(main_frame)
        frame_ip.pack(fill="x", pady=2)
        ttk.Label(frame_ip, text="IP:", width=5).pack(side="left")
        self.lb_sv_ip = ttk.Label(frame_ip, text=obter_ip_local(),
                                   font=("Helvetica", 10, "bold"), bootstyle=INFO)
        self.lb_sv_ip.pack(side="left")

        # Porta + Senha
        frame_sv = ttk.Frame(main_frame)
        frame_sv.pack(fill="x", pady=2)
        ttk.Label(frame_sv, text="Porta:", width=5).pack(side="left")
        self.sv_entry_port = ttk.Entry(frame_sv, width=8)
        self.sv_entry_port.insert(0, "5555")
        self.sv_entry_port.pack(side="left", padx=(0, 15))
        ttk.Label(frame_sv, text="Senha:", width=5).pack(side="left")
        self.sv_entry_pw = ttk.Entry(frame_sv, width=16, show="*")
        self.sv_entry_pw.insert(0, "migetauth")
        self.sv_entry_pw.pack(side="left", padx=(0, 5))
        self.btn_sv_show = ttk.Button(frame_sv, text="Mostrar", command=self._sv_toggle_pw)
        self.btn_sv_show.pack(side="left")

        # Botões servidor
        frame_sv_btn = ttk.Frame(main_frame)
        frame_sv_btn.pack(fill="x", pady=5)
        self.btn_sv_start = ttk.Button(frame_sv_btn, text="Iniciar Servidor",
                                        bootstyle=SUCCESS, command=self._sv_start)
        self.btn_sv_start.pack(side="left", padx=(0, 5))
        self.btn_sv_stop = ttk.Button(frame_sv_btn, text="Parar Servidor",
                                       bootstyle=DANGER, command=self._sv_stop, state=DISABLED)
        self.btn_sv_stop.pack(side="left")

        self.lb_sv_status = ttk.Label(main_frame, text="Parado", bootstyle=SECONDARY)
        self.lb_sv_status.pack(anchor="w", pady=(0, 5))

        # ── CLIENTE REMOTO ──
        ttk.Separator(main_frame).pack(fill="x", pady=10)
        ttk.Label(main_frame, text="Cliente Remoto",
                  font=("Helvetica", 16, "bold")).pack(anchor="w")
        ttk.Separator(main_frame).pack(fill="x", pady=5)

        # IP
        frame_ip2 = ttk.Frame(main_frame)
        frame_ip2.pack(fill="x", pady=2)
        ttk.Label(frame_ip2, text="IP do servidor:", width=16).pack(side="left")
        self.entry_ip = ttk.Entry(frame_ip2)
        self.entry_ip.insert(0, "192.168.1.")
        self.entry_ip.pack(side="left", fill="x", expand=True)

        # Porta
        frame_port = ttk.Frame(main_frame)
        frame_port.pack(fill="x", pady=2)
        ttk.Label(frame_port, text="Porta:", width=16).pack(side="left")
        self.entry_port = ttk.Entry(frame_port, width=10)
        self.entry_port.insert(0, "5555")
        self.entry_port.pack(side="left")

        # Senha
        frame_pw = ttk.Frame(main_frame)
        frame_pw.pack(fill="x", pady=2)
        ttk.Label(frame_pw, text="Senha:", width=16).pack(side="left")
        self.entry_pw = ttk.Entry(frame_pw, show="*")
        self.entry_pw.insert(0, "migetauth")
        self.entry_pw.pack(side="left", fill="x", expand=True)
        self.btn_cl_show = ttk.Button(frame_pw, text="Mostrar", command=self._cl_toggle_pw)
        self.btn_cl_show.pack(side="left", padx=(5, 0))

        # Status
        self.lb_status = ttk.Label(main_frame, text="Pronto", font=("Helvetica", 11))
        self.lb_status.pack(anchor="w", pady=(5, 0))

        # Botões cliente
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=(10, 5))

        self.btn_ping = ttk.Button(btn_frame, text="Testar Conexão",
                                    command=self._do_ping)
        self.btn_ping.pack(side="left", padx=(0, 5))

        self.btn_receber = ttk.Button(btn_frame, text="Receber",
                                       bootstyle=INFO, command=self._do_download)
        self.btn_receber.pack(side="left", padx=5)

        self.btn_enviar = ttk.Button(btn_frame, text="Enviar",
                                      bootstyle=SUCCESS, command=self._do_upload)
        self.btn_enviar.pack(side="left", padx=5)

        # Log
        ttk.Separator(main_frame).pack(fill="x", pady=10)
        ttk.Label(main_frame, text="Log:").pack(anchor="w")
        self.txt_log = tk.Text(main_frame, height=6, state="disabled",
                               bg="#1e1e1e", fg="#cccccc", relief="flat")
        self.txt_log.pack(fill="x", pady=(5, 0))

        self._sv_pw_visible = False
        self._cl_pw_visible = False

    # ── Helpers ──

    def _sv_toggle_pw(self):
        self._sv_pw_visible = not self._sv_pw_visible
        self.sv_entry_pw.config(show="" if self._sv_pw_visible else "*")
        self.btn_sv_show.config(text="Ocultar" if self._sv_pw_visible else "Mostrar")

    def _cl_toggle_pw(self):
        self._cl_pw_visible = not self._cl_pw_visible
        self.entry_pw.config(show="" if self._cl_pw_visible else "*")
        self.btn_cl_show.config(text="Ocultar" if self._cl_pw_visible else "Mostrar")

    def _log(self, msg):
        self.txt_log.config(state="normal")
        self.txt_log.insert("end", msg + "\n")
        self.txt_log.see("end")
        self.txt_log.config(state="disabled")

    # ── Servidor ──

    def _sv_start(self):
        try:
            port = int(self.sv_entry_port.get().strip())
        except ValueError:
            self.lb_sv_status.config(text="Porta inválida", bootstyle=DANGER)
            return
        password = self.sv_entry_pw.get().strip()
        if not password:
            self.lb_sv_status.config(text="Defina uma senha", bootstyle=DANGER)
            return

        self._sv_server, self._sv_thread, ip = start_server(port, password, self._log)
        self.lb_sv_ip.config(text=ip)
        self.lb_sv_status.config(text=f"Rodando em {ip}:{port}", bootstyle=SUCCESS)
        self.btn_sv_start.config(state=DISABLED)
        self.btn_sv_stop.config(state=NORMAL)
        self.sv_entry_port.config(state="disabled")
        self.sv_entry_pw.config(state="disabled")
        self._log(f"Servidor iniciado em {ip}:{port}")

    def _sv_stop(self):
        if self._sv_server:
            self._log("Parando servidor...")
            self._sv_server.shutdown()
            self._sv_server.server_close()
            self._sv_server = None
            self._sv_thread = None
        self.lb_sv_status.config(text="Parado", bootstyle=SECONDARY)
        self.btn_sv_start.config(state=NORMAL)
        self.btn_sv_stop.config(state=DISABLED)
        self.sv_entry_port.config(state="normal")
        self.sv_entry_pw.config(state="normal")
        self._log("Servidor parado.")

    # ── Cliente ──

    def _get_config(self):
        ip = self.entry_ip.get().strip()
        try:
            port = int(self.entry_port.get().strip())
        except ValueError:
            raise ValueError("Porta inválida")
        pw = self.entry_pw.get().strip()
        if not ip or not pw:
            raise ValueError("Preencha IP e senha")
        return ip, port, pw

    def _do_ping(self):
        try:
            ip, port, pw = self._get_config()
        except ValueError as e:
            self.lb_status.config(text=str(e), bootstyle=DANGER)
            return
        self.lb_status.config(text="Testando...", bootstyle=WARNING)

        def task():
            try:
                ok = ping(ip, port, pw)
                if ok:
                    self.win.after(0, lambda: self.lb_status.config(text="Conexão OK!", bootstyle=SUCCESS))
                    self.win.after(0, lambda: self._log(f"Conexão bem-sucedida com {ip}:{port}"))
                else:
                    self.win.after(0, lambda: self.lb_status.config(text="Falha na conexão", bootstyle=DANGER))
                    self.win.after(0, lambda: self._log(f"Falha ao conectar em {ip}:{port}"))
            except Exception as e:
                self.win.after(0, lambda: self.lb_status.config(text=f"Erro: {e}", bootstyle=DANGER))
                self.win.after(0, lambda: self._log(f"Erro: {e}"))

        threading.Thread(target=task, daemon=True).start()

    def _do_download(self):
        self._sync("download")

    def _do_upload(self):
        self._sync("upload")

    def _sync(self, direction):
        if self._running:
            return
        try:
            ip, port, pw = self._get_config()
        except ValueError as e:
            self.lb_status.config(text=str(e), bootstyle=DANGER)
            return

        self._running = True
        self.btn_ping.config(state=DISABLED)
        self.btn_receber.config(state=DISABLED)
        self.btn_enviar.config(state=DISABLED)
        lbl = "Recebendo..." if direction == "download" else "Enviando..."
        self.lb_status.config(text=lbl, bootstyle=WARNING)

        def task():
            try:
                if direction == "download":
                    download(ip, port, pw)
                    self.win.after(0, self._sync_ok, "Dados recebidos do PC!")
                else:
                    upload(ip, port, pw)
                    self.win.after(0, self._sync_ok, "Dados enviados para o PC!")
            except Exception as e:
                self.win.after(0, self._sync_err, str(e))

        threading.Thread(target=task, daemon=True).start()

    def _sync_ok(self, msg):
        self.lb_status.config(text=msg, bootstyle=SUCCESS)
        self._log(msg)
        self._sync_done()

    def _sync_err(self, msg):
        self.lb_status.config(text=f"Erro: {msg}", bootstyle=DANGER)
        self._log(f"Erro: {msg}")
        self._sync_done()

    def _sync_done(self):
        self._running = False
        self.btn_ping.config(state=NORMAL)
        self.btn_receber.config(state=NORMAL)
        self.btn_enviar.config(state=NORMAL)


_instancia = SyncClientWindow()


def showWindow():
    _instancia.show_window()
