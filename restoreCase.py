#!/usr/bin/env python3

import argparse
import json
import re

def main():
    parser = argparse.ArgumentParser(
        description="Restaura o case e a pontuação original.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("input_reference", help="O caminho para o arquivo de referência.")
    parser.add_argument("input_json", help="O caminho para o arquivo json de entrada.")
    parser.add_argument("output_json", help="O caminho para o arquivo json de saída.")

    args = parser.parse_args()

# Ler texto original
    with open(args.input_reference, 'r') as f:
        original_lines = [line.strip() for line in f if line.strip()]

    # Ler resultado do MFA
    with open(args.input_json, 'r') as f:
        aligned_data = json.load(f)

    # Extrair tokens (palavras com possíveis pontuações atreladas)
    original_tokens = []
    for line in original_lines:
        # Agrupar palavras com pontuação que vierem juntas (ex: "Guaraná," ou "cuscuz.")
        tokens = re.findall(r'\w+[^\w\s]*', line, re.UNICODE)
        original_tokens.extend(tokens)

    # Substituir apenas os textos com os tokens do original
    aligned_index = 0
    for i, item in enumerate(aligned_data):
        if item['text'] == '<unk>':
            continue

        while aligned_index < len(original_tokens):
            token = original_tokens[aligned_index]
            # Comparar só a parte alfabética do token
            token_word = re.match(r'\w+', token)
            if token_word and token_word.group(0).lower() == item['text'].lower():
                aligned_data[i]['text'] = token  # substitui com case + pontuação
                aligned_index += 1
                break
            else:
                aligned_index += 1

    with open(args.output_json, 'w', encoding='utf-8') as f:
        f.write('[\n')
        i = 0
        aligned_len = len(aligned_data)
        token_index = 0

        # Contar quantos itens válidos (sem <unk>) existem
        total_valid = sum(1 for x in aligned_data if x['text'] != '<unk>')
        written = 0

        for line_num, line in enumerate(original_lines):
            tokens = re.findall(r'\w+[^\w\s]*', line, re.UNICODE)
            for _ in tokens:
                while i < aligned_len:
                    item = aligned_data[i]
                    i += 1
                    if item['text'] == '<unk>':
                        continue
                    json_str = json.dumps(item, ensure_ascii=False, separators=(', ', ': '))
                    f.write(json_str)
                    written += 1
                    if written < total_valid:
                        f.write(',\n')
                    else:
                        f.write('\n')
                    break
            # Adiciona quebra de linha *somente* se não for o último verso
            if line_num < len(original_lines) - 1:
                f.write('\n')

        f.write(']\n')

    print('Case e pontuação restaurados com sucesso!')

if __name__ == "__main__":
    main()
