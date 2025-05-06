import json
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

ARQUIVO_TAREFAS = "tarefas.json"

def salvar_tarefas_em_arquivo(tarefas, nome_arquivo=ARQUIVO_TAREFAS):
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(tarefas, f, indent=4, ensure_ascii=False)

def carregar_tarefas_de_arquivo(nome_arquivo=ARQUIVO_TAREFAS):
    try:
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

tarefas = carregar_tarefas_de_arquivo()

def obter_frequencia_tk(valor_inicial="nenhuma"):
    opcoes_validas = ["nenhuma", "diária", "semanal", "anual"]

    while True:
        frequencia = simpledialog.askstring("Frequência", "Digite a frequência (nenhuma, diária, semanal, anual):",
                                            initialvalue=valor_inicial, parent=root)
        if frequencia is None:  
            return valor_inicial
        frequencia = frequencia.strip()

        if frequencia in opcoes_validas:
            return frequencia
        else:
            messagebox.showerror("Erro", "Entrada inválida! Escolha apenas entre: nenhuma, diária, semanal ou anual.")
            
def obter_data_tk(titulo="Data da Tarefa", valor_inicial=""):
    while True:
        data_str = simpledialog.askstring(titulo, "Digite a data (dd/mm/aaaa hh:mm):", initialvalue=valor_inicial, parent=root)
        if data_str is None:
            return None
        try:
            return datetime.strptime(data_str, "%d/%m/%Y %H:%M").strftime("%d/%m/%Y %H:%M")
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido. Tente novamente.")

def adicionar_tarefa_tk():
    descricao = simpledialog.askstring("Adicionar Tarefa", "Descrição da tarefa:", parent=root)
    if not descricao:
        return

    data_hora = obter_data_tk("Data da tarefa")  
    if not data_hora:
        return

    frequencia = obter_frequencia_tk()
    lembrete = messagebox.askyesno("Lembrete", "Deseja receber lembrete?", parent=root)

    tarefa = {
        "descricao": descricao.capitalize(),
        "concluida": False,
        "data_hora": data_hora,
        "frequencia": frequencia,
        "lembrete": lembrete
    }

    tarefas.append(tarefa)
    salvar_tarefas_em_arquivo(tarefas)
    messagebox.showinfo("Sucesso", "Tarefa adicionada com sucesso!", parent=root)  

    listar_tarefas_tk()

def listar_tarefas_tk(filtro="pendentes"):
    lista.delete(0, tk.END)

    tarefas_ordenadas = sorted(tarefas, key=lambda t: datetime.strptime(t["data_hora"], "%d/%m/%Y %H:%M"))

    for tarefa in tarefas_ordenadas:
        if filtro == "pendentes" and not tarefa["concluida"]:
            lista.insert(tk.END, f"{tarefa['data_hora']} - {tarefa['descricao']}")
        elif filtro == "concluidas" and tarefa["concluida"]:
            lista.insert(tk.END, f"{tarefa['data_hora']} - {tarefa['descricao']}")

def editar_tarefa_tk():
    selecionado = lista.curselection()
    if not selecionado:
        messagebox.showwarning("Aviso", "Selecione uma tarefa para editar.")
        return
    
    texto_selecionado = lista.get(selecionado[0])
    descricao_tarefa = texto_selecionado.split(" - ", 1)[1]

    tarefa = next((t for t in tarefas if t["descricao"] == descricao_tarefa), None)

    if not tarefa:
        messagebox.showerror("Erro", "Tarefa não encontrada!")
        return

    nova_desc = simpledialog.askstring("Editar", "Nova descrição:", initialvalue=tarefa["descricao"], parent=root)
    if nova_desc:
        tarefa["descricao"] = nova_desc

    nova_data = obter_data_tk("Nova data", tarefa["data_hora"])
    if nova_data:
        tarefa["data_hora"] = nova_data

    nova_freq = obter_frequencia_tk(tarefa["frequencia"])
    if nova_freq:
        tarefa["frequencia"] = nova_freq

    lembrete = messagebox.askyesno("Lembrete", "Deseja ativar lembrete?", parent=root)
    tarefa["lembrete"] = lembrete

    if tarefa["concluida"] and nova_data:
        tarefa["concluida"] = False

    salvar_tarefas_em_arquivo(tarefas)
    listar_tarefas_tk()
    messagebox.showinfo("Editado", "Tarefa editada com sucesso!")

def remover_tarefa_tk():
    selecionado = lista.curselection()
    if not selecionado:
        messagebox.showwarning("Aviso", "Selecione uma tarefa para remover.")
        return
    
    texto_selecionado = lista.get(selecionado[0])
    descricao_tarefa = texto_selecionado.split(" - ", 1)[1]

    tarefa = next((t for t in tarefas if t["descricao"] == descricao_tarefa), None)

    if not tarefa:
        messagebox.showerror("Erro", "Tarefa não encontrada!")
        return

    confirm = messagebox.askyesno("Remover", f"Tem certeza que deseja remover a tarefa '{tarefa['descricao']}'?")
    if confirm:
        tarefas.remove(tarefa)  
        salvar_tarefas_em_arquivo(tarefas)
        listar_tarefas_tk()
        messagebox.showinfo("Removida", "Tarefa removida com sucesso!")

def verificar_tarefas_automaticamente():
    root.after(300000, verificar_tarefas_automaticamente)
    agora = datetime.now()
    alterado = False

    for tarefa in tarefas:
        try:
            data_tarefa = datetime.strptime(tarefa["data_hora"], "%d/%m/%Y %H:%M")
        except ValueError:
            continue
                
        if tarefa.get("lembrete") and not tarefa["concluida"]:
            diferenca = (data_tarefa - agora).total_seconds()
            if 0 < diferenca <= 600:
                messagebox.showinfo("Lembrete", f"🔔 Tarefa '{tarefa['descricao']}' ocorre em menos de 10 minutos!")
        
        if not tarefa["concluida"] and data_tarefa < agora:
            if tarefa.get("frequencia") == "diária":
                nova_data = data_tarefa + timedelta(days=1)  
            elif tarefa.get("frequencia") == "semanal":
                nova_data = data_tarefa + timedelta(weeks=1)  
            elif tarefa.get("frequencia") == "anual":
                nova_data = data_tarefa.replace(year=data_tarefa.year + 1)  
            else:  
                tarefa["concluida"] = True
                alterado = True
                continue

            tarefa["data_hora"] = nova_data.strftime("%d/%m/%Y %H:%M")
            alterado = True

    if alterado:
        salvar_tarefas_em_arquivo(tarefas)

root = tk.Tk()
root.title("EasyTask")
root.geometry("500x400")

frame = tk.Frame(root)
frame.pack(pady=10)

btn_add = tk.Button(frame, text="Adicionar", command=adicionar_tarefa_tk)
btn_edit = tk.Button(frame, text="Editar", command=editar_tarefa_tk)
btn_del = tk.Button(frame, text="Remover", command=remover_tarefa_tk)

btn_add.pack(side="left", padx=5)
btn_edit.pack(side="left", padx=5)
btn_del.pack(side="left", padx=5)

lista = tk.Listbox(root, width=60)
lista.pack(pady=20)

filtro_frame = tk.Frame(root)
filtro_frame.pack(pady=5)

tk.Button(filtro_frame, text="Pendentes", command=lambda: listar_tarefas_tk("pendentes")).pack(side="left", padx=5)
tk.Button(filtro_frame, text="Concluídas", command=lambda: listar_tarefas_tk("concluidas")).pack(side="left", padx=5)

verificar_tarefas_automaticamente()
listar_tarefas_tk()

root.mainloop()
