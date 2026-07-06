# Copyright (C) 2026 Murilo Gomes Julio
# SPDX-License-Identifier: GPL-2.0-only

# Site: https://github.com/mugomes

import threading, time, webbrowser, frmAbout, frmSyncClient
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox, simpledialog, ttk, Menu, PhotoImage
from core import *

class AuthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MiGetAuth")
        self.root.geometry("600x400")
        self.root.position_center()
        self.root.resizable(False, False)

        icon_image = PhotoImage(file=r'./icon/migetauth.png')
        self.root.iconphoto(True, icon_image) 

        self.selected_id = None # Guardar o ID da conta selecionada
        self.selected_secret = None
        self.accounts = []

        self.setup_ui()
        self.load_accounts()
        self.update_token_loop()

        barmenuMain = Menu(self.root)
        self.root.config(menu=barmenuMain)

        mnuTools = Menu(barmenuMain, tearoff=0)
        barmenuMain.add_cascade(label="Ferramentas", menu=mnuTools)
        mnuTools.add_command(label="Sincronizar com PC", command=self.showSyncClient)

        mnuAbout = Menu(barmenuMain, tearoff=0)
        barmenuMain.add_cascade(label="Sobre", menu=mnuAbout)
        mnuAbout.add_command(label="Verificar Atualizações", command=self.checkUpdate)
        mnuAbout.add_separator()
        mnuAbout.add_command(label="Apoie MiGetAuth", command=self.supportApp)
        mnuAbout.add_separator()
        mnuAbout.add_command(label="Sobre MiGetAuth", command=self.showAbout)

    def checkUpdate(self):
        webbrowser.open(url="https://github.com/mugomes/migetauth/releases")

    def supportApp(self):
        webbrowser.open(url="https://github.com/mugomes/migetauth")

    def showAbout(self):
        frmAbout.showWindow()

    def showSyncClient(self):
        frmSyncClient.showWindow()

    def setup_ui(self):
        main_frame = tb.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        # Treeview para contas
        self.tree = ttk.Treeview(main_frame, show="tree", height=15)
        self.tree.pack(side="left", fill="y", padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Área direita
        right_frame = tb.Frame(main_frame)
        right_frame.pack(side="right", expand=True, fill="both", padx=10)

        # Token
        self.token_label = tb.Label(
            right_frame,
            text="------",
            font=("Helvetica", 32)
        )
        self.token_label.pack(pady=30)

        # Nome da conta
        self.name_label = tb.Label(right_frame, text="Selecione uma conta", font=("Helvetica", 12))
        self.name_label.pack(pady=5)

        # Container para botões de ação
        btn_frame = tb.Frame(right_frame)
        btn_frame.pack(pady=20)

        # Botão Adicionar
        add_btn = tb.Button(btn_frame, text="Novo", bootstyle=SUCCESS, command=self.add_account_dialog, width=10)
        add_btn.grid(row=0, column=0, padx=5)

        # Botão Editar
        self.edit_btn = tb.Button(btn_frame, text="Editar", bootstyle=INFO, command=self.edit_account_dialog, width=10, state=DISABLED)
        self.edit_btn.grid(row=0, column=1, padx=5)

        # Botão Excluir
        self.del_btn = tb.Button(btn_frame, text="Excluir", bootstyle=DANGER, command=self.delete_account, width=10, state=DISABLED)
        self.del_btn.grid(row=0, column=2, padx=5)

    def load_accounts(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.accounts = get_accounts()
        for acc in self.accounts:
            self.tree.insert("", "end", iid=str(acc[0]), text=acc[1])
        
        # Limpa seleção após recarregar
        self.selected_id = None
        self.selected_secret = None
        self.token_label.config(text="------")
        self.token_label.bind("<Button-1>", self.copy_click)
        self.name_label.config(text="Selecione uma conta")
        self.edit_btn.config(state=DISABLED)
        self.del_btn.config(state=DISABLED)

    def copy_click(self, event):
        texto = self.token_label.cget("text")
    
        self.root.clipboard_clear()
        self.root.clipboard_append(texto)
        self.root.update()
    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        item_id = selected[0]
        for acc in self.accounts:
            if str(acc[0]) == item_id:
                self.selected_id = acc[0]
                self.selected_secret = decrypt(acc[2])
                self.name_label.config(text=acc[1])
                
                # Habilita botões de edição e exclusão
                self.edit_btn.config(state=NORMAL)
                self.del_btn.config(state=NORMAL)
                break

    def update_token_loop(self):
        def loop():
            while True:
                if self.selected_secret:
                    try:
                        token = generate_token(self.selected_secret)
                        self.token_label.config(text=token)
                    except:
                        self.token_label.config(text="ERRO")
                time.sleep(1)

        threading.Thread(target=loop, daemon=True).start()

    def add_account_dialog(self):
        name = simpledialog.askstring("Novo", "Nome da Conta (ex: GitHub):")
        secret = simpledialog.askstring("Novo", "Chave secreta (Secret):")

        if name and secret:
            add_account(name, secret)
            self.load_accounts()

    def edit_account_dialog(self):
        if not self.selected_id: return
        
        current_name = self.name_label.cget("text")
        new_name = simpledialog.askstring("Editar", f"Novo nome para '{current_name}':", initialvalue=current_name)
        
        if new_name:
            # Chama a função de update no seu core.py
            update_account(self.selected_id, new_name)
            self.load_accounts()

    def delete_account(self):
        if not self.selected_id: return
        
        confirm = messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja remover esta conta?")
        if confirm:
            delete_account_db(self.selected_id)
            self.load_accounts()

if __name__ == "__main__":
    init_db()
    app = tb.Window(themename="darkly")
    AuthApp(app)
    app.mainloop()