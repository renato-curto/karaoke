#!/usr/bin/env python3

import sys
import re
import string

from praatio import textgrid
from pathlib import Path

ass = """[Script Info]
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

def format_time(seconds): # From seconds to H:MM:SS.cc
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def load_textgrid_words(textgrid_file):
  tg = textgrid.openTextgrid(textgrid_file, includeEmptyIntervals=True)
  tier = tg._tierDict["words"]
  words = list(tier)

  if words[0].label.strip() == "":
    words.pop(0)
  return words

def load_reference_lines(file):
  with open(file, 'r', encoding='utf-8') as f:
    return [line.strip() for line in f if line.strip()]

def main():
  global ass

  if len(sys.argv) != 4:
    print("Uso: textgrid2ass.py input.TextGrid reference.txt output.ass")
    return

  textGrid = Path(sys.argv[1])
  tg_words = load_textgrid_words(textGrid)

  tg_words = [(round(start, 2), round(end, 2), mark) for start, end, mark in tg_words]

  #for start, end, mark in tg_words:
  #  print(start, end, mark)

  reference = Path(sys.argv[2])
  lines = load_reference_lines(reference)

  ref_words = []

  for line in lines:
    #print(line)
    words = re.findall(r'\S+', line)
    #print(words)
    ref_words.append(words)

  if sum(len(line) for line in ref_words) != sum(1 for (_, _, mark) in tg_words if mark != ""):
    print("Erro: o número de palavras no TextGrid não bate com o reference.txt.")
    return

  tg_words_nonempty = [(start, end, mark) for (start, end, mark) in tg_words if mark.strip() != ""]

  index = 0
  for l, line in enumerate(ref_words):
    for w, word in enumerate(line):
      #print(word)
      word = word.lower().translate(str.maketrans('', '', string.punctuation))
      start, end, mark = tg_words_nonempty[index]
      mark = mark.lower()
      index += 1

      if word != mark:
        print(f"'{sys.argv[2]}', linha {l + 1}, palavra {w + 1}: '{word}'")
        print(f"'{sys.argv[1]}', start {start}, end {end}: '{mark}'")
        return

  dialogues = []

  index = 0
  preview = 100

  start = format_time(0)
  end = format_time(max(0, tg_words[index][0] - preview/100))

  ass += f"Dialogue: 0,{start},{end},Credits,,0,0,0,,César Menotti & Fabiano - Nóis Bebe é Guaraná\n"
  ass += f"Dialogue: 0,{start},{end},Credits,,0,0,0,,Legendado por Renato Curto Rodrigues\n"

  for line in ref_words:
    #print(line)
    dialogue = ""
    length = len(line)
    start = format_time(max(0, tg_words[index][0] - preview/100))

    for i, word in enumerate(line):
      xmin, xmax, text = tg_words[index]

      if i + 1 < length:
        if tg_words[index + 1][2].strip() == "":
          index += 1
          xmax = tg_words[index][1]
      else:
        end = format_time(tg_words[index][1])
        if index + 1 < len(tg_words) and tg_words[index + 1][2].strip() == "":
          index += 1

      #print(f"{xmax} {xmin}")
      k = int(round(100*(xmax - xmin)))
      index += 1

      dialogue += f"{{\\k{k}}}{word} "

    dialogue = f"Dialogue: 0,{start},{end},Default,,0,0,0,,{{\\k{preview}}}{dialogue}\n"
    #print(dialogue)
    ass += dialogue

  try:
    with open(sys.argv[3], 'w', encoding='utf-8') as file:
      file.write(ass)
  except IOError as e:
    print(f"Erro: não foi possível escrever no arquivo '{sys.argv[3]}'.")
    print(f"Detalhe: {e}")

if __name__ == "__main__":
    main()
