# Copyright (C) 2026 Murilo Gomes Julio
# SPDX-License-Identifier: GPL-2.0-only

# Site: https://github.com/mugomes

import tkinter as tk
import ttkbootstrap as ttk

from ttkbootstrap.constants import *

def showWindow():
    frmAbout = ttk.Toplevel()
    frmAbout.title("Sobre - MiGetAuth")
    frmAbout.geometry("400x467")
    frmAbout.position_center()
    frmAbout.resizable(False, False)

    icon_image = tk.PhotoImage(file=r'./icon/migetauth.png')
    frmAbout.iconphoto(True, icon_image) 

    lblNameApp = ttk.Label(
        frmAbout, text='MiGetAuth', font=("", 12, "bold")
    )
    lblNameApp.pack(anchor="nw", padx=5, pady=(7, 3))

    lblVersion = ttk.Label(
        frmAbout, text='Version: 1.0.0', font=("", 12)
    )
    lblVersion.pack(anchor="nw", padx=5, pady=(7, 3))

    lblDeveloper = ttk.Label(
        frmAbout, text='Developed by: Murilo Gomes Julio', font=("", 12)
    )
    lblDeveloper.pack(anchor="nw", padx=5, pady=(7, 3))

    lblSite = ttk.Label(
        frmAbout, text='Site: https://github.com/mugomes/migetauth', font=("", 12)
    )
    lblSite.pack(anchor="nw", padx=5, pady=(7, 3))

    lblCopyright = ttk.Label(
        frmAbout, text='Copyright (C) 2026 Murilo Gomes Julio', font=("", 12)
    )
    lblCopyright.pack(anchor="nw", padx=5, pady=(7, 3))

    lblLicense = ttk.Label(
        frmAbout, text='License: GPL-2.0-only', font=("", 12)
    )
    lblLicense.pack(anchor="nw", padx=5, pady=(7, 3))

    frame = tk.Frame(frmAbout)
    frame.pack(expand=True, fill="both", padx=5, pady=(7,3))
    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side="right", fill="y")
    txtLicense = ttk.Text(frame, wrap='word', yscrollcommand=scrollbar.set)
    txtLicense.pack(anchor="nw", fill='both', expand=True)

    conteudo = '''MiGetAuth is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, only version 2 of the License.
    
MiGetAuth is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.'''

    txtLicense.insert('1.0', conteudo)
    txtLicense.config(state="disabled")

    # Carrega Janela
    return frmAbout
