#!/usr/bin/env python3

import argparse
import textgrid

def main():
    parser = argparse.ArgumentParser(
        description="Converte um arquivo Text Grid o formato JSON.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("input_textGrid", help="O caminho para o arquivo Text Grid de entrada.")
    parser.add_argument("output_json", help="O caminho para o arquivo .ass de saída.")

    args = parser.parse_args()

    print(f"Lendo arquivo de entrada: {args.input_textGrid}")
    tg = textgrid.TextGrid.fromFile(args.input_textGrid)

    # Construir a lista de dicionários
    result = []
    for interval in tg[0]:  # Primeira tier (geralmente palavras)
        if interval.mark.strip():  # Ignorar intervalos vazios
            result.append({
                'text': interval.mark,
                'start': round(interval.minTime, 3),
                'end': round(interval.maxTime, 3),
                'duration': round(interval.maxTime - interval.minTime, 3)
            })

    # Gerar o JSON no formato customizado
    with open(args.output_json, 'w', encoding='utf-8') as f:
        f.write('[\n')
        for i, item in enumerate(result):
            line = f'  {{  "text": "{item["text"]}", "start": {item["start"]}, "end": {item["end"]}, "duration": {item["duration"]} }}'
            if i < len(result) - 1:
                line += ','
            f.write(line + '\n')
        f.write(']\n')

    print(f'Convertido! {len(result)} segmentos encontrados.')

if __name__ == "__main__":
    main()
