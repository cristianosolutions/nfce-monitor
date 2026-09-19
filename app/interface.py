import os
import queue
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from app.excel_service import exportar_excel
from app.nfce_service import consultar_nfce
from app.xml_reader import ler_xml



def caminho_recurso(caminho_relativo):
    """Retorna o caminho correto de arquivos incluídos no executável."""
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent.parent

    return base / caminho_relativo


class VerificadorNFCeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NFC-e Monitor | MERCANTIL MEDEIROS LTDA")

        caminho_icone = caminho_recurso("assets/icone.ico")

        if caminho_icone.exists():
            self.root.iconbitmap(str(caminho_icone))

        self.root.geometry("1500x860")
        self.root.minsize(1100, 650)

        self.fila = queue.Queue()
        self.registros = []
        self.registros_por_item = {}
        self.consultando = False

        self.pasta_var = tk.StringVar()
        self.pfx_var = tk.StringVar()
        self.senha_var = tk.StringVar()
        self.busca_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Todos")
        self.situacao_sefaz_var = tk.StringVar(value="Todas")
        self.info_var = tk.StringVar(value="Selecione uma pasta com XMLs.")
        self.total_var = tk.StringVar(value="0")
        self.autorizadas_var = tk.StringVar(value="0")
        self.canceladas_var = tk.StringVar(value="0")
        self.nao_consultadas_var = tk.StringVar(value="0")
        self.outros_var = tk.StringVar(value="0")

        self._configurar_estilos()
        self._montar_interface()
        self.root.after(100, self._processar_fila)

    def _configurar_estilos(self):
        estilo = ttk.Style()
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 22, "bold"))
        estilo.configure("Subtitulo.TLabel", font=("Segoe UI", 10))
        estilo.configure("CardNumero.TLabel", font=("Segoe UI", 20, "bold"))
        estilo.configure("CardTexto.TLabel", font=("Segoe UI", 10))
        estilo.configure("Acao.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 7))
        estilo.configure("Treeview", rowheight=28, font=("Segoe UI", 9))
        estilo.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        estilo.configure(
    "NFCe.Horizontal.TProgressbar",
    background="#000000",    # progresso
    
    )

    def _montar_interface(self):
        cabecalho = ttk.Frame(self.root, padding=(18, 14))
        cabecalho.pack(fill="x")

        # =========================
        # LOGO
        # =========================

        caminho_logo = caminho_recurso("assets/logo.png")

        if caminho_logo.exists():
            self.logo_img = tk.PhotoImage(file=str(caminho_logo))

            logo_label = ttk.Label(
                cabecalho,
                image=self.logo_img
            )

            logo_label.pack(
                side="left",
                padx=(0, 12)
            )
            
        # =========================
        # TÍTULO
        # =========================

        bloco_titulo = ttk.Frame(cabecalho)
        bloco_titulo.pack(side="left")

        ttk.Label(
            bloco_titulo,
            text="NFC-e Monitor",
            style="Titulo.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            bloco_titulo,
            text="Monitoramento, conferência de XML e consulta fiscal na SEFAZ",
            style="Subtitulo.TLabel",
        ).pack(anchor="w")

        ttk.Separator(self.root, orient="horizontal").pack(fill="x")

        topo = ttk.LabelFrame(self.root, text="Arquivos XML", padding=10)
        topo.pack(fill="x", padx=10, pady=(10, 8))
        ttk.Label(topo, text="Pasta dos XMLs:").grid(row=0, column=0, sticky="w")
        ttk.Entry(topo, textvariable=self.pasta_var, width=80).grid(
            row=0, column=1, padx=6, sticky="ew"
        )
        ttk.Button(topo, text="Selecionar pasta", command=self.selecionar_pasta).grid(
            row=0, column=2, padx=4
        )
        self.btn_analisar = ttk.Button(
            topo, text="Analisar XMLs", command=self.analisar_xmls, style="Acao.TButton"
        )
        self.btn_analisar.grid(row=0, column=3, padx=4)
        topo.columnconfigure(1, weight=1)

        cert = ttk.LabelFrame(
            self.root, text="Consulta SEFAZ / Certificado A1", padding=10
        )
        cert.pack(fill="x", padx=10, pady=(0, 8))
        ttk.Label(cert, text="Certificado PFX:").grid(row=0, column=0, sticky="w")
        ttk.Entry(cert, textvariable=self.pfx_var, width=60).grid(
            row=0, column=1, padx=6, sticky="ew"
        )
        ttk.Button(cert, text="Selecionar PFX", command=self.selecionar_pfx).grid(
            row=0, column=2, padx=4
        )
        ttk.Label(cert, text="Senha:").grid(row=0, column=3, padx=(14, 4))
        ttk.Entry(cert, textvariable=self.senha_var, show="*", width=18).grid(
            row=0, column=4, padx=4
        )
        self.btn_consultar = ttk.Button(
            cert, text="Consultar SEFAZ", command=self.consultar_sefaz_selecionada, style="Acao.TButton"
        )
        self.btn_consultar.grid(row=0, column=5, padx=(10, 4))
        cert.columnconfigure(1, weight=1)

        resumo = ttk.Frame(self.root, padding=(10, 0, 10, 8))
        resumo.pack(fill="x")
        cards = [
            ("NFC-e carregadas", self.total_var),
            ("SEFAZ autorizadas", self.autorizadas_var),
            ("SEFAZ canceladas", self.canceladas_var),
            ("Não consultadas", self.nao_consultadas_var),
            ("Outros / erros", self.outros_var),
        ]
        for coluna, (titulo, variavel) in enumerate(cards):
            card = ttk.LabelFrame(resumo, padding=(18, 8))
            card.grid(row=0, column=coluna, padx=(0 if coluna == 0 else 5, 5), sticky="ew")
            ttk.Label(card, textvariable=variavel, style="CardNumero.TLabel").pack(anchor="w")
            ttk.Label(card, text=titulo, style="CardTexto.TLabel").pack(anchor="w")
            resumo.columnconfigure(coluna, weight=1)

        filtros = ttk.LabelFrame(self.root, text="Pesquisa e filtros", padding=10)
        filtros.pack(fill="x")
        ttk.Label(filtros, text="Pesquisar:").pack(side="left")
        busca = ttk.Entry(filtros, textvariable=self.busca_var, width=40)
        busca.pack(side="left", padx=6)
        busca.bind("<KeyRelease>", lambda _e: self.aplicar_filtros())

        ttk.Label(filtros, text="Status XML:").pack(side="left", padx=(15, 4))
        combo = ttk.Combobox(
            filtros, textvariable=self.status_var,
            values=["Todos", "AUTORIZADA", "CANCELADA", "DENEGADA",
                    "REJEITADA / OUTRO", "SEM PROTOCOLO"],
            state="readonly", width=20
        )
        combo.pack(side="left")
        combo.bind("<<ComboboxSelected>>", lambda _e: self.aplicar_filtros())

        ttk.Label(filtros, text="Situação SEFAZ:").pack(
            side="left", padx=(15, 4)
        )
        combo_sefaz = ttk.Combobox(
            filtros,
            textvariable=self.situacao_sefaz_var,
            values=[
                "Todas",
                "NÃO CONSULTADA",
                "AUTORIZADA",
                "CANCELADA",
                "NÃO CONSTA",
                "OUTRO",
                "ERRO",
            ],
            state="readonly",
            width=18,
        )
        combo_sefaz.pack(side="left")
        combo_sefaz.bind(
            "<<ComboboxSelected>>", lambda _e: self.aplicar_filtros()
        )

        ttk.Button(filtros, text="Limpar filtros", command=self.limpar_filtros).pack(
            side="left", padx=8
        )
        ttk.Button(filtros, text="Exportar Excel", command=self.exportar).pack(
            side="right"
        )

        quadro = ttk.Frame(self.root, padding=(10, 0, 10, 0))
        quadro.pack(fill="both", expand=True)
        colunas = (
            "numero", "serie", "data", "cnpj", "emitente", "valor",
            "status_xml", "situacao_sefaz", "cstat_sefaz", "protocolo", "chave"
        )
        self.tabela = ttk.Treeview(
            quadro, columns=colunas, show="headings", selectmode="browse"
        )
        titulos = {
            "numero": "Número", "serie": "Série", "data": "Emissão",
            "cnpj": "CNPJ", "emitente": "Emitente", "valor": "Valor",
            "status_xml": "Status XML", "situacao_sefaz": "Situação SEFAZ",
            "cstat_sefaz": "cStat", "protocolo": "Protocolo",
            "chave": "Chave de acesso",
        }
        larguras = {
            "numero": 85, "serie": 55, "data": 135, "cnpj": 135,
            "emitente": 220, "valor": 90, "status_xml": 125,
            "situacao_sefaz": 130, "cstat_sefaz": 60, "protocolo": 140,
            "chave": 330,
        }
        for coluna in colunas:
            self.tabela.heading(coluna, text=titulos[coluna])
            self.tabela.column(coluna, width=larguras[coluna], anchor="w")
        self.tabela.column("valor", anchor="e")

        sy = ttk.Scrollbar(quadro, orient="vertical", command=self.tabela.yview)
        sx = ttk.Scrollbar(quadro, orient="horizontal", command=self.tabela.xview)
        self.tabela.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        self.tabela.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")
        quadro.rowconfigure(0, weight=1)
        quadro.columnconfigure(0, weight=1)
        self.tabela.tag_configure("autorizada", background="#eaf7ee")
        self.tabela.tag_configure("cancelada", background="#fdecec")
        self.tabela.tag_configure("nao_consultada", background="#f5f5f5")
        self.tabela.tag_configure("outro", background="#fff4d6")
        self.tabela.bind("<Double-1>", self.abrir_xml_selecionado)

        rodape = ttk.Frame(self.root, padding=10)
        rodape.pack(fill="x")
        self.progresso = ttk.Progressbar(rodape, mode="determinate", style="NFCe.Horizontal.TProgressbar")
        self.progresso.pack(fill="x", side="left", expand=True)
        ttk.Label(rodape, textvariable=self.info_var).pack(side="left", padx=(12, 0))

    def selecionar_pasta(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta com os XMLs")
        if pasta:
            self.pasta_var.set(pasta)

    def selecionar_pfx(self):
        arquivo = filedialog.askopenfilename(
            title="Selecione o certificado A1",
            filetypes=[("Certificado PFX/P12", "*.pfx *.p12"), ("Todos", "*.*")]
        )
        if arquivo:
            self.pfx_var.set(arquivo)

    def analisar_xmls(self):
        pasta = self.pasta_var.get().strip()
        if not pasta or not os.path.isdir(pasta):
            messagebox.showwarning("Pasta", "Selecione uma pasta válida com XMLs.")
            return
        self.btn_analisar.config(state="disabled")
        self.info_var.set("Localizando arquivos XML...")
        self.progresso["value"] = 0
        threading.Thread(
            target=self._worker_analisar, args=(pasta,), daemon=True
        ).start()

    def _worker_analisar(self, pasta):
        try:
            arquivos = list(Path(pasta).rglob("*.xml"))
            total = len(arquivos)
            self.fila.put(("inicio_analise", total))
            notas, eventos = {}, []

            for indice, caminho in enumerate(arquivos, 1):
                resultado = ler_xml(caminho)
                if resultado.get("tipo") == "NFCE":
                    resultado["caminho"] = str(caminho)
                    resultado.update({
                        "situacao_sefaz": "NÃO CONSULTADA",
                        "cstat_sefaz": "", "motivo_sefaz": "",
                        "protocolo_sefaz": "", "data_consulta_sefaz": "",
                    })
                    chave = resultado.get("chave", "")
                    if chave and chave not in notas:
                        notas[chave] = resultado
                elif resultado.get("tipo") == "EVENTO":
                    eventos.append(resultado)

                if indice == total or indice % 100 == 0:
                    self.fila.put(("progresso", indice, total))

            for evento in eventos:
                chave = evento.get("chave", "")
                if (chave in notas and evento.get("tipo_evento") == "110111"
                        and evento.get("cstat") == "135"):
                    notas[chave]["status"] = "CANCELADA"
                    notas[chave]["motivo"] = evento.get("motivo", "")
                    notas[chave]["protocolo"] = evento.get("protocolo", "")

            self.fila.put(
                ("analise_concluida", list(notas.values()), total, len(eventos))
            )
        except Exception as erro:
            self.fila.put(("erro_analise", str(erro)))

    def _processar_fila(self):
        try:
            while True:
                msg = self.fila.get_nowait()
                tipo = msg[0]
                if tipo == "inicio_analise":
                    self.progresso["maximum"] = max(msg[1], 1)
                    self.info_var.set(f"{msg[1]} XML(s) encontrado(s).")
                elif tipo == "progresso":
                    self.progresso["value"] = msg[1]
                    self.info_var.set(f"Analisando {msg[1]} de {msg[2]} XML(s)...")
                elif tipo == "analise_concluida":
                    self.registros = msg[1]
                    self._atualizar_resumo()
                    self.aplicar_filtros()
                    self.btn_analisar.config(state="normal")
                    self.info_var.set(
                        f"{len(self.registros)} NFC-e única(s) | "
                        f"{msg[2]} XML(s) | {msg[3]} evento(s)"
                    )
                elif tipo == "erro_analise":
                    self.btn_analisar.config(state="normal")
                    messagebox.showerror("Erro", msg[1])
                elif tipo == "consulta_ok":
                    item_id, resultado = msg[1], msg[2]
                    reg = self.registros_por_item.get(item_id)
                    if reg:
                        reg["situacao_sefaz"] = resultado.get("status", "")
                        reg["cstat_sefaz"] = resultado.get("cstat", "")
                        reg["motivo_sefaz"] = resultado.get("motivo", "")
                        reg["protocolo_sefaz"] = resultado.get("protocolo", "")
                        reg["data_consulta_sefaz"] = datetime.now().strftime(
                            "%d/%m/%Y %H:%M:%S"
                        )
                        self._atualizar_linha(item_id, reg)
                        self._atualizar_resumo()
                    self.consultando = False
                    self.btn_consultar.config(state="normal")
                    self.info_var.set(
                        f"SEFAZ: {resultado.get('status', '')} - "
                        f"{resultado.get('motivo', '')}"
                    )
                    messagebox.showinfo(
                        "Consulta SEFAZ",
                        f"Situação: {resultado.get('status', '')}\n"
                        f"cStat: {resultado.get('cstat', '')}\n"
                        f"Motivo: {resultado.get('motivo', '')}\n"
                        f"Protocolo: {resultado.get('protocolo', '')}"
                    )
                elif tipo == "consulta_erro":
                    item_id, erro_texto = msg[1], msg[2]
                    reg = self.registros_por_item.get(item_id)
                    if reg:
                        reg["situacao_sefaz"] = "ERRO"
                        reg["cstat_sefaz"] = ""
                        reg["motivo_sefaz"] = erro_texto
                        reg["data_consulta_sefaz"] = datetime.now().strftime(
                            "%d/%m/%Y %H:%M:%S"
                        )
                        self._atualizar_linha(item_id, reg)
                        self._atualizar_resumo()
                    self.consultando = False
                    self.btn_consultar.config(state="normal")
                    self.info_var.set(f"SEFAZ: ERRO - {erro_texto}")
                    messagebox.showerror("Consulta SEFAZ", erro_texto)
        except queue.Empty:
            pass
        self.root.after(100, self._processar_fila)

    def _atualizar_resumo(self):
        total = len(self.registros)
        autorizadas = sum(
            1 for r in self.registros
            if r.get("situacao_sefaz") == "AUTORIZADA"
        )
        canceladas = sum(
            1 for r in self.registros
            if r.get("situacao_sefaz") == "CANCELADA"
        )
        nao_consultadas = sum(
            1 for r in self.registros
            if r.get("situacao_sefaz", "NÃO CONSULTADA") == "NÃO CONSULTADA"
        )
        outros = sum(
            1 for r in self.registros
            if r.get("situacao_sefaz", "NÃO CONSULTADA")
            not in ("NÃO CONSULTADA", "AUTORIZADA", "CANCELADA")
        )
        self.total_var.set(f"{total:,}".replace(",", "."))
        self.autorizadas_var.set(f"{autorizadas:,}".replace(",", "."))
        self.canceladas_var.set(f"{canceladas:,}".replace(",", "."))
        self.nao_consultadas_var.set(f"{nao_consultadas:,}".replace(",", "."))
        self.outros_var.set(f"{outros:,}".replace(",", "."))

    def aplicar_filtros(self):
        busca = self.busca_var.get().strip().lower()
        status = self.status_var.get()
        situacao_sefaz_filtro = self.situacao_sefaz_var.get()
        self.tabela.delete(*self.tabela.get_children())
        self.registros_por_item.clear()

        for reg in self.registros:
            if status != "Todos" and reg.get("status", "") != status:
                continue

            situacao_atual = reg.get("situacao_sefaz", "NÃO CONSULTADA")
            if (
                situacao_sefaz_filtro != "Todas"
                and situacao_atual != situacao_sefaz_filtro
            ):
                continue

            texto = " ".join(str(reg.get(c, "")) for c in (
                "numero", "serie", "chave", "cnpj", "cnpj_formatado",
                "emitente", "fantasia", "status", "situacao_sefaz"
            )).lower()
            if busca and busca not in texto:
                continue
            situacao = reg.get("situacao_sefaz", "NÃO CONSULTADA")
            tag = ""
            if situacao == "AUTORIZADA":
                tag = "autorizada"
            elif situacao == "CANCELADA":
                tag = "cancelada"
            elif situacao == "NÃO CONSULTADA":
                tag = "nao_consultada"
            elif situacao in ("OUTRO", "ERRO", "NÃO CONSTA"):
                tag = "outro"
            item = self.tabela.insert(
                "", "end", values=self._valores_linha(reg),
                tags=(tag,) if tag else ()
            )
            self.registros_por_item[item] = reg

    def limpar_filtros(self):
        self.busca_var.set("")
        self.status_var.set("Todos")
        self.situacao_sefaz_var.set("Todas")
        self.aplicar_filtros()

    def _valores_linha(self, reg):
        valor = float(reg.get("valor", 0) or 0)
        valor_txt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return (
            reg.get("numero", ""), reg.get("serie", ""),
            reg.get("data_emissao", ""),
            reg.get("cnpj_formatado", reg.get("cnpj", "")),
            reg.get("fantasia") or reg.get("emitente", ""), valor_txt,
            reg.get("status", ""), reg.get("situacao_sefaz", "NÃO CONSULTADA"),
            reg.get("cstat_sefaz", ""),
            reg.get("protocolo_sefaz") or reg.get("protocolo", ""),
            reg.get("chave", ""),
        )

    def _atualizar_linha(self, item, reg):
        if self.tabela.exists(item):
            situacao = reg.get("situacao_sefaz", "NÃO CONSULTADA")
            tag = (
                "autorizada" if situacao == "AUTORIZADA"
                else "cancelada" if situacao == "CANCELADA"
                else "nao_consultada" if situacao == "NÃO CONSULTADA"
                else "outro" if situacao in ("OUTRO", "ERRO", "NÃO CONSTA")
                else ""
            )
            self.tabela.item(
                item, values=self._valores_linha(reg),
                tags=(tag,) if tag else ()
            )

    def consultar_sefaz_selecionada(self):
        if self.consultando:
            return
        selecao = self.tabela.selection()
        if not selecao:
            messagebox.showwarning("Consulta SEFAZ", "Selecione uma NFC-e na tabela.")
            return
        pfx, senha = self.pfx_var.get().strip(), self.senha_var.get()
        if not pfx or not os.path.isfile(pfx):
            messagebox.showwarning("Certificado", "Selecione um PFX/P12 válido.")
            return
        item = selecao[0]
        reg = self.registros_por_item.get(item)
        if not reg:
            return
        self.consultando = True
        self.btn_consultar.config(state="disabled")
        self.info_var.set(f"Consultando SEFAZ: {reg.get('chave', '')}...")
        threading.Thread(
            target=self._worker_consultar,
            args=(item, reg.get("chave", ""), pfx, senha),
            daemon=True
        ).start()

    def _worker_consultar(self, item, chave, pfx, senha):
        try:
            self.fila.put(("consulta_ok", item, consultar_nfce(chave, pfx, senha)))
        except Exception as erro:
            self.fila.put(
                ("consulta_erro", item, f"{type(erro).__name__}: {erro}")
            )

    def abrir_xml_selecionado(self, _evento=None):
        selecao = self.tabela.selection()
        if not selecao:
            return
        reg = self.registros_por_item.get(selecao[0])
        if not reg:
            return
        caminho = reg.get("caminho", "")
        if caminho and os.path.isfile(caminho):
            try:
                os.startfile(caminho)
            except AttributeError:
                subprocess.Popen(["xdg-open", caminho])

    def exportar(self):
        if not self.registros:
            messagebox.showwarning("Exportar", "Não há dados para exportar.")
            return
        destino = filedialog.asksaveasfilename(
            title="Salvar relatório Excel", defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")]
        )
        if destino:
            try:
                exportar_excel(self.registros, destino)
                messagebox.showinfo("Exportar", f"Relatório salvo em:\n{destino}")
            except Exception as erro:
                messagebox.showerror("Exportar", str(erro))


def iniciar_interface():
    root = tk.Tk()
    VerificadorNFCeApp(root)
    root.mainloop()
