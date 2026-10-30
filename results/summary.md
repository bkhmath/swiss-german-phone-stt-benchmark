# Results


## asgdts  (n = 5750)

| model | condition | WER % ↓ [95% CI] | BLEU ↑ | number recall % ↑ [95% CI] | number precision % ↑ |
|---|---|---|---|---|---|
| whisper-small | wideband 16 kHz | 42.0 [40.5, 43.5] | 38.4 | 90.9 [87.4, 94.1] | 78.2 |
| whisper-small | G.711 phone | 46.4 [44.5, 48.1] | 34.6 | 88.8 [84.7, 92.7] | 77.4 |
| large-v3-turbo | wideband 16 kHz | 26.3 [25.2, 27.6] | 57.4 | 97.5 [95.7, 99.0] | 84.6 |
| large-v3-turbo | G.711 phone | 28.6 [27.2, 29.9] | 54.8 | 97.2 [95.1, 98.9] | 82.5 |
| large-v3-turbo | G.711 + 3% loss | 31.4 [29.7, 33.1] | 52.1 | 94.7 [91.9, 97.2] | 84.4 |
| large-v3 | wideband 16 kHz | 23.8 [22.7, 25.0] | 61.2 | 96.9 [94.9, 98.7] | 86.8 |
| large-v3 | G.711 phone | 25.8 [24.6, 27.0] | 58.7 | 95.6 [93.3, 97.8] | 86.2 |
| turbo-SG (MIT) | wideband 16 kHz | 24.9 [23.9, 26.0] | 59.0 | 99.1 [98.0, 100.0] | 88.3 |
| turbo-SG (MIT) | G.711 phone | 27.2 [26.1, 28.3] | 56.1 | 98.4 [96.7, 99.7] | 88.2 |
| turbo-SG (MIT) | G.711 + 3% loss | 28.0 [26.9, 29.2] | 55.1 | 97.2 [95.1, 98.9] | 86.4 |
| large-v3-SG (Flix) | wideband 16 kHz | 22.0 [21.0, 23.0] | 63.8 | 97.5 [95.5, 99.1] | 89.9 |
| large-v3-SG (Flix) | G.711 phone | 22.8 [21.8, 23.9] | 62.6 | 97.5 [95.4, 99.3] | 88.9 |

**Phone-line penalty (phone - wideband, paired bootstrap):**

| model | Δ WER pts [95% CI] | Δ number recall pts [95% CI] |
|---|---|---|
| whisper-small | 4.4 [3.6, 5.4] | -2.2 [-5.5, 0.9] |
| large-v3-turbo | 2.2 [1.8, 2.6] | -0.3 [-2.0, 1.4] |
| large-v3 | 2.0 [1.6, 2.3] | -1.2 [-2.8, 0.3] |
| turbo-SG (MIT) | 2.3 [2.0, 2.6] | -0.6 [-1.6, 0.0] |
| large-v3-SG (Flix) | 0.9 [0.6, 1.2] | 0.0 [-0.9, 0.9] |

**WER % by dialect region, G.711 phone line** (cantons with ≥ 100 clips):

| model | BE | ZH | SG | AG | BL | LU | TG | SO | ZG | VS | UR |
|---|---|---|---|---|---|---|---|---|---|---|---|
| whisper-small | 49.5 | 42.8 | 46.9 | 45.7 | 49.0 | 45.8 | 44.5 | 44.7 | 42.9 | 59.8 | 52.4 |
| large-v3-turbo | 29.8 | 25.7 | 27.8 | 29.1 | 30.2 | 27.4 | 29.2 | 30.4 | 28.1 | 41.4 | 30.0 |
| large-v3 | 26.6 | 23.8 | 25.8 | 26.4 | 27.3 | 25.0 | 24.6 | 27.4 | 26.2 | 34.9 | 25.7 |
| turbo-SG (MIT) | 27.2 | 25.3 | 27.9 | 27.4 | 28.4 | 26.7 | 28.4 | 30.9 | 27.5 | 34.2 | 27.4 |
| large-v3-SG (Flix) | 23.5 | 20.9 | 22.6 | 23.1 | 23.1 | 23.2 | 23.5 | 26.3 | 23.1 | 29.5 | 22.4 |

large-v3-SG (Flix), phone, SG: WER 22.6 [21.0, 24.2]

large-v3-SG (Flix), phone, ZH: WER 20.9 [19.5, 22.8]

large-v3-SG (Flix), phone, BE: WER 23.5 [21.2, 26.2]

large-v3-SG (Flix), phone, VS: WER 29.5 [23.2, 33.7]

**Number errors, large-v3-SG (Flix) on the phone line (sample):**

| dialect | reference | hypothesis | missed |
|---|---|---|---|
| BL | Es fanden sich neun Lehmziegel-Bauten, die um einen Platz gruppiert waren. | Es hat neue Lehnziegel gebaut, die um den Platz gruppiert wurden. | [9] |
| VS | Die Mitglieder der Akademie, die nicht ordiniert waren, saßen hinter den sieben Reihen. | Mitglieder der Akademie, die nicht ordiniert waren, saßen in einer siebenhänderen Reihe. | [7] |
| BE | In einer drei Tage dauernden Sitzung gelingt ihm ein erfolgreicher Abschluss. | In einer dreitagtauernden Sitzung gelingt ihm ein erfolgreicher Abschluss. | [3] |
| SG | Zehn von ihnen waren irische Nationalisten, die von der britischen Armee erschossen wurden. | Zwei von ihnen sind irische Nationalisten, die von der britischen Armee erschossen worden sind. | [10] |
| VS | Jahr gegen Null tendiert. | Georg Egon Hultendiert. | [0] |
| ZG | Kurz darauf unterzeichnete Robinson einen neuen Drei-Jahres-Vertrag. | Kurz darauf hat Robinson einen neuen Dreijahresvertrag unterzeichnet. | [3] |
| SO | Für die Disziplinen Weit-, Drei- und Stabhochsprung werden den Sprint-Spikes sehr ähnliche Schuhe verwendet. | Für die Disziplinen Weiz, Treu und Stabhochsprung werden Sprints sehr ähnlich in Schuhen verwendet. | [3] |
| BL | Sind gar drei Bits falsch, so kann nicht einmal mehr ein Fehler erkannt werden. | Sie geht ein bisschen falsch, so kann man nicht mehr einen Fehler erkennen. | [3] |

## spcr  (n = 384)

| model | condition | WER % ↓ [95% CI] | BLEU ↑ | number recall % ↑ [95% CI] | number precision % ↑ |
|---|---|---|---|---|---|
| whisper-small | wideband 16 kHz | 43.0 [39.8, 46.7] | 44.2 | 75.7 [71.2, 80.1] | 68.3 |
| whisper-small | G.711 phone | 44.4 [41.8, 47.3] | 41.1 | 69.5 [64.3, 75.5] | 85.5 |
| large-v3-turbo | wideband 16 kHz | 22.7 [20.8, 24.7] | 68.3 | 81.3 [75.9, 86.2] | 73.1 |
| large-v3-turbo | G.711 phone | 22.6 [21.1, 24.1] | 66.6 | 82.9 [78.9, 87.0] | 93.2 |
| large-v3 | wideband 16 kHz | 18.5 [16.9, 20.3] | 75.0 | 80.0 [73.8, 85.7] | 94.4 |
| large-v3 | G.711 phone | 19.9 [18.0, 21.9] | 72.7 | 81.0 [75.8, 85.8] | 72.0 |
| turbo-SG (MIT) | wideband 16 kHz | 17.6 [16.3, 18.8] | 73.7 | 78.2 [73.0, 83.4] | 83.6 |
| turbo-SG (MIT) | G.711 phone | 18.2 [17.1, 19.3] | 72.6 | 79.2 [75.2, 83.1] | 84.1 |
| large-v3-SG (Flix) | wideband 16 kHz | 27.0 [25.0, 28.7] | 63.2 | 79.1 [74.4, 84.1] | 91.8 |
| large-v3-SG (Flix) | G.711 phone | 32.8 [31.0, 34.4] | 56.0 | 73.1 [67.4, 78.7] | 89.1 |

**Phone-line penalty (phone - wideband, paired bootstrap):**

| model | Δ WER pts [95% CI] | Δ number recall pts [95% CI] |
|---|---|---|
| whisper-small | 1.4 [-1.5, 3.9] | -6.2 [-10.1, -2.0] |
| large-v3-turbo | -0.1 [-1.8, 1.3] | 1.7 [-1.1, 4.6] |
| large-v3 | 1.4 [-0.1, 2.9] | 1.0 [-1.5, 3.5] |
| turbo-SG (MIT) | 0.6 [-0.2, 1.3] | 1.0 [-1.7, 3.9] |
| large-v3-SG (Flix) | 5.8 [4.4, 7.3] | -5.9 [-10.2, -1.8] |

(45 of 429 segments with French references excluded.)

**What goes wrong with numbers on the phone line** (% of reference numbers, token alignment):

| error type | whisper-small | large-v3-turbo | large-v3 | turbo-SG (MIT) | large-v3-SG (Flix) |
|---|---|---|---|---|---|
| lost in a skipped passage (≥ 5 words) | 14.6 | 8.9 | 12.0 | 5.3 | 17.3 |
| other wrong value | 8.0 | 3.5 | 3.1 | 4.4 | 5.6 |
| replaced by non-number words | 5.0 | 3.0 | 1.4 | 3.5 | 2.3 |
| dropped locally | 3.6 | 2.2 | 2.6 | 3.2 | 2.6 |
| malformed number words (e.g. 'dreitausendsebhundert') | 0.3 | 0.1 | 0.0 | 3.4 | 0.0 |
| year shortened (2025 -> 25) | 0.4 | 0.5 | 0.3 | 0.9 | 0.1 |
| wrong year (2021 -> 2020) | 0.4 | 0.4 | 0.0 | 1.0 | 0.3 |
| split into digit groups (14800 -> 14 ...) | 0.5 | 0.0 | 0.0 | 0.0 | 0.0 |
| **all number errors** | **32.8** | **18.6** | **19.4** | **21.7** | **28.2** |

**Number-specific error rate on the phone line** (excluding skipped passages; paired bootstrap vs. the base model):

| model | error % ↓ [95% CI] | vs. base | Δ pts [95% CI] |
|---|---|---|---|
| whisper-small | 21.3 [17.2, 25.9] | | |
| large-v3-turbo | 10.6 [7.9, 13.6] | | |
| large-v3 | 8.4 [5.5, 11.7] | | |
| turbo-SG (MIT) | 17.3 [13.7, 20.6] | large-v3-turbo | 6.7 [3.3, 9.9] |
| large-v3-SG (Flix) | 13.1 [9.6, 16.6] | large-v3 | 4.8 [1.4, 8.0] |

**Number errors, large-v3-SG (Flix) on the phone line (sample):**

| dialect | reference | hypothesis | missed |
|---|---|---|---|
| BE-parliament | Ihr hättet den Punkt angenommen als Motion mit 149 Ja, bei 2 Nein und 0 Enthaltungen. Wir kommen zur Abschreibung von Punkt 2. Wer Punkt 2 abschreiben will, stimmt Ja. Wer es ablehnt, stimmt Nein. | Sie haben den Punkt A als Motion mit 150 Ja- bei 2 Nein-Stimmen und 1 Enthaltung. Wir kommen zur Abschreibung von Punkt 2. Wer Punkt 2 abschreiben will, stimmt Ja, wer es ablehnt, stimmt Nein. | [0, 149] |
| BE-parliament | Für das Protokoll war ein Ja zur Ziffer 1. Wir sind bei der Abschreibung. Wer die Ziffer 1 abschreiben will, stimmt Ja. Wer das nicht will, stimmt Nein. | Wer die Ziffer 1 abschreiben will, stimmt Ja, wer dies nicht will, stimmt Nein. | [1] |

## Latency (batch size 1, G.711 clips, NVIDIA GeForce RTX 5070)

| model | mean clip s | p50 ms ↓ | p90 ms ↓ | p99 ms ↓ | RTF ↓ |
|---|---|---|---|---|---|
| whisper-small | 8.2 | 242 | 301 | 346 | 0.029 |
| large-v3-turbo | 8.2 | 172 | 214 | 247 | 0.021 |
| large-v3 | 8.2 | 440 | 600 | 710 | 0.055 |
| turbo-SG (MIT) | 8.2 | 200 | 249 | 304 | 0.024 |
| large-v3-SG (Flix) | 8.2 | 454 | 591 | 797 | 0.056 |
