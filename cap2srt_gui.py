import tkinter as tk
from tkinter import filedialog, Frame, ttk
import tkinter.font as tkfont
from tkmacosx import Button
from fileinput import filename
import os
import json
import re
import logging

logging.basicConfig(filename='app_extrair-legenda.log', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

try:
    root = tk.Tk()
    root.title("Extrator de Legenda")

    pasta_saida = tk.StringVar()
    nome_projeto = tk.StringVar()


    def list_dir():
        caminho = os.path.expanduser('~') + '/Movies/CapCut/User Data/Projects/com.lveditor.draft/'
        lista_projetos = os.listdir(caminho)
        lista_projetos.sort()

        lista_removidos = []
        for item in lista_projetos:
            nao_proj = re.search(r'(\..*)|(.*\.json)', item)
            if nao_proj:
                lista_removidos.append(nao_proj.group())

        opcoes_projeto['values'] = [item for item in lista_projetos if item not in lista_removidos]


    def output_file():
        caminho_saida = filedialog.askdirectory()

        if filename:
            label_output['text'] = caminho_saida
            label_output['anchor'] = "e"
            pasta_saida.set(caminho_saida)


    def extract(path):
        with open(path, 'r') as file:
            return json.load(file)


    def write(data, nome_arq):
        caminho = pasta_saida.get()
        arquivo = os.path.join(caminho, nome_arq)

        with open(arquivo, 'w') as file:
            file.write(data)


    def ms_to_srt(time_in_ms):
        convert_ms = int(time_in_ms / 1000)
        ms = convert_ms % 1000
        total_seconds = (convert_ms - ms) / 1000
        seconds = int(total_seconds % 60)
        total_minutes = (total_seconds - seconds) / 60
        minutes = int(total_minutes % 60)
        hour = int((total_minutes - minutes) / 60)

        return f'{hour:02}:{minutes:02}:{seconds:02},{ms:03}'


    def scrap_subs(content):
        subtitles_info = []
        materials = content['materials']
        sub_timing = content['tracks'][1]['segments']

        for m in materials['texts']:
            content = re.search(r'text.*.$', m['content']).group(0)
            sanitize_content = content.replace('text":"', '').replace('"}', '')

            segment = next(seg for seg in sub_timing if seg['material_id'] == m['id'])
            start = segment['target_timerange']['start']
            end = start + segment['target_timerange']['duration']
            timestamp = f'{ms_to_srt(start)} --> {ms_to_srt(end)}'
            index = len(subtitles_info) + 1

            subtitles_info.append({
                'index': index,
                'timestamp': timestamp,
                'content': sanitize_content
            })

        return subtitles_info


    def extrair_legenda():
        draft = os.path.expanduser(
            '~') + '/Movies/CapCut/User Data/Projects/com.lveditor.draft/' + nome_projeto.get() + '/draft_info.json'
        subtitles = scrap_subs(extract(draft))

        output = ''.join([f'{s["index"]}\n{s["timestamp"]}\n{s["content"]}\n\n' for s in subtitles])
        write(output, 'legenda.srt')

        btn_extrair['text'] = "Legenda Extraída!"
        btn_extrair['anchor'] = "e"


    # Estilo
    corpo_fonte = tkfont.Font(font="Calibri", size=10)
    bg_botoes = '#2563eb'

    main_frame = Frame(root, padx=10, pady=10)
    main_frame.pack()

    # Escolher Projeto
    top_frame = Frame(main_frame)
    top_frame.pack(fill="both")

    projeto_wrapper = tk.LabelFrame(top_frame, text="Selecione o projeto do CapCut ", font=corpo_fonte,
                                    labelanchor="nw")
    projeto_wrapper.pack(fill="x", padx=10, pady=10)

    inner_projeto = tk.Frame(projeto_wrapper)
    inner_projeto.pack(fill="both", padx=10, pady=10)

    opcoes_projeto = ttk.Combobox(inner_projeto, textvariable=nome_projeto, font=corpo_fonte, state="readonly")
    opcoes_projeto.pack(fill="both", ipady=3, ipadx=3)

    list_dir()
    opcoes_projeto.bind('<<ComboboxSelected>>', nome_projeto.get())

    # Pasta de saída
    mid_frame = Frame(main_frame)
    mid_frame.pack(fill="both")

    output_wrapper = tk.LabelFrame(mid_frame, text="Salvar legenda em... ", font=corpo_fonte, labelanchor="nw")
    output_wrapper.pack(fill="x", padx=10, pady=10)

    inner_output = tk.Frame(output_wrapper)
    inner_output.pack(fill="both", padx=10, pady=10)

    label_output = tk.Label(inner_output, width=24, text="-- Selecione a pasta --", anchor="w",
                            font='Calibri 12 italic')
    label_output.pack(side="left")

    btn_output = Button(inner_output, text="Procurar", font=corpo_fonte, pady=4, relief='solid', bg=bg_botoes,
                           fg="white", command=output_file)
    btn_output.pack(side="top")

    # Área do Botão
    bottom_frame = Frame(main_frame, padx=10, pady=10)
    bottom_frame.pack(fill="both")

    btn_extrair = Button(bottom_frame, text="Extrair Legenda", font='Calibri 13 bold', anchor="center",
                         pady=6, padx=32, relief='solid', bg=bg_botoes, fg="white", command=extrair_legenda)
    btn_extrair.pack(fill="both")

    # Loop tkinter
    root.mainloop()

except Exception as e:
   logging.exception("Aconteceu um erro:")
