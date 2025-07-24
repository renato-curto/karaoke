#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import argparse
import re
import os

preview = 100

def format_ass_time(seconds: float) -> str:
    """Converte segundos para o formato de tempo do .ass (H:MM:SS.cs)."""
    h = int(seconds / 3600)
    m = int((seconds % 3600) / 60)
    s = int(seconds % 60)
    cs = int((seconds - int(seconds)) * 100)
    return f"{h}:{m:02}:{s:02}.{cs:02}"

def process_groups_from_file(file_path: str) -> list:
    """
    Lê um arquivo de texto que se parece com JSON, mas usa linhas em branco
    para separar grupos de objetos. Retorna uma lista de listas de objetos.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Erro: O arquivo de entrada '{file_path}' não foi encontrado.")
        return []
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")
        return []

    # Divide o conteúdo em blocos separados por uma ou mais linhas em branco.
    # Uma linha em branco é representada por duas ou mais novas linhas,
    # possivelmente com espaços em branco entre elas.
    text_blocks = re.split(r'\n\s*\n', content)

    all_groups = []
    for block in text_blocks:
        # Pula blocos que estão vazios ou contêm apenas espaços em branco.
        if not block.strip():
            continue

        # Para cada bloco, encontre todos os objetos {...}
        # Esta regex é "non-greedy" e funciona para a estrutura plana do JSON.
        json_objects_str = re.findall(r'\{[^{}]*\}', block)

        if not json_objects_str:
            continue

        # Junta os objetos encontrados com vírgulas e envolve em colchetes
        # para formar uma string de array JSON válida.
        json_array_str = '[' + ','.join(json_objects_str) + ']'

        try:
            group = json.loads(json_array_str)
            if group:  # Adiciona apenas se o grupo não estiver vazio
                all_groups.append(group)
        except json.JSONDecodeError as e:
            print(f"Aviso: Não foi possível analisar um bloco de texto.")
            print(f"Bloco com erro: \"{block.strip()}\"")
            print(f"Erro de JSON: {e}")

    return all_groups

def create_ass_file(groups: list, output_path: str):
    """Gera o conteúdo do arquivo .ass a partir dos grupos de palavras."""
    
    # Cabeçalho padrão para arquivos .ass
    header = """[Script Info]
; Script gerado por IA
Title: Legendas Convertidas
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,21,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,20,1
Style: Credits,Arial,21,&H0000FFFF,&H000000FF,&H00000000,&H99000000,-1,0,0,0,100,100,0,0,1,2,2,5,10,10,20,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    try:
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            f.write(header)
            credits = True

            for group in groups:
                if not group:
                    continue

                start_time = format_ass_time(max(0, group[0]['start'] - preview/100))
                end_time = format_ass_time(group[-1]['end'])

                karaoke_text_parts = []
                for word_data in group:
                    # Usamos a duração da própria palavra (em centissegundos) para a tag \k.
                    # Ex: "duration": 0.28 -> {\k28}
                    duration_cs = int(word_data.get('duration', 0) * 100)
                    text = word_data.get('text', '').strip()
                    if text:
                        karaoke_text_parts.append(f"{{\\k{duration_cs}}}{text}")
                
                # Junta as partes com um espaço.
                full_karaoke_text = " ".join(karaoke_text_parts)

                if credits:
                    music = f"Dialogue: 0,0:00:00.00,{start_time},Credits,,0,0,0,,César Menotti & Fabiano - Nóis Bebe é Guaraná\n"
                    f.write(music)

                    creator = f"Dialogue: 0,0:00:00.00,{start_time},Credits,,0,0,0,,Legendado por Renato Curto Rodrigues\n"
                    f.write(creator)

                    credits = False

                dialogue_line = f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{{\\k{preview}}}{full_karaoke_text}\n"
                f.write(dialogue_line)

        print(f"\nArquivo '{output_path}' criado com sucesso!")

    except IOError as e:
        print(f"Erro: Não foi possível escrever no arquivo de saída '{output_path}'.")
        print(f"Detalhe: {e}")


def main():
    """Função principal para executar o script a partir da linha de comando."""
    parser = argparse.ArgumentParser(
        description="Converte um arquivo JSON de transcrição de palavras para o formato de legenda .ass com efeito de karaokê.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("input_json", help="O caminho para o arquivo JSON de entrada.")
    parser.add_argument("output_ass", help="O caminho para o arquivo .ass de saída.")

    args = parser.parse_args()

    print(f"Lendo arquivo de entrada: {args.input_json}")
    word_groups = process_groups_from_file(args.input_json)
    
    if word_groups:
        print(f"Encontrados {len(word_groups)} grupos de diálogo.")
        create_ass_file(word_groups, args.output_ass)

if __name__ == "__main__":
    main()
