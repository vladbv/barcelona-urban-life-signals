# IRIS data profile

Generated from the locally downloaded Open Data BCN IRIS CSV.

## Source file

- Path: `data/raw/2025_IRIS_Peticions_Ciutadanes_OpenData.csv`

- Rows: 287,304

- Observed CSV columns: 25

- Derived profiling columns: 2

## Date coverage

| date_field        | valid_rows | missing_or_invalid_rows | min_date   | max_date   |
| ----------------- | ---------- | ----------------------- | ---------- | ---------- |
| registration_date | 287304     | 0                       | 2023-10-25 | 2025-12-31 |
| closure_date      | 287304     | 0                       | 2025-01-01 | 2025-12-31 |

## Duplicate indicators

| duplicate_type    | rows |
| ----------------- | ---- |
| exact_full_row    | 3393 |
| repeated_fitxa_id | 3393 |

## Geographic missingness

| column         | missing_rows | missing_percent |
| -------------- | ------------ | --------------- |
| CODI_DISTRICTE | 89852        | 31.27           |
| DISTRICTE      | 89852        | 31.27           |
| CODI_BARRI     | 90680        | 31.56           |
| BARRI          | 90680        | 31.56           |
| SECCIO_CENSAL  | 221906       | 77.24           |
| COORDENADA_X   | 90680        | 31.56           |
| COORDENADA_Y   | 90680        | 31.56           |
| LONGITUD       | 90680        | 31.56           |
| LATITUD        | 90680        | 31.56           |

## Main classification distributions

### Top `TIPUS` values

| TIPUS             | rows   | percent |
| ----------------- | ------ | ------- |
| INCIDENCIA        | 126669 | 44.09   |
| ISSUE             | 45349  | 15.78   |
| CONSULTA          | 34947  | 12.16   |
| QUEIXA            | 27175  | 9.46    |
| SUGGERIMENT       | 14703  | 5.12    |
| PETICIO DE SERVEI | 10679  | 3.72    |
| COMPLAINT         | 9586   | 3.34    |
| QUERY             | 8766   | 3.05    |
| SUGGESTION        | 5493   | 1.91    |
| SERVICE REQUEST   | 3406   | 1.19    |

### Top `AREA` values

| AREA                                    | rows  | percent |
| --------------------------------------- | ----- | ------- |
| Recollida i neteja de l'espai urbà      | 90030 | 31.34   |
| Manteniment de l'espai urbà             | 70675 | 24.6    |
| Portal de tràmits                       | 29914 | 10.41   |
| Informació  tràmits i atenció ciutadana | 17890 | 6.23    |
| Mobilitat                               | 13948 | 4.85    |
| Prevenció i seguretat                   | 13096 | 4.56    |
| Gestions municipals                     | 10880 | 3.79    |
| Urbanisme                               | 7823  | 2.72    |
| Sanitat i salut pública                 | 6430  | 2.24    |
| Serveis socials                         | 6416  | 2.23    |

### Top `ELEMENT` values

| ELEMENT                                   | rows  | percent |
| ----------------------------------------- | ----- | ------- |
| Neteja de l'espai públic                  | 33189 | 11.55   |
| Relacions amb l'Ajuntament                | 27026 | 9.41    |
| Pintades / cartells / pancartes           | 12632 | 4.4     |
| Arbrat                                    | 11265 | 3.92    |
| Voreres                                   | 10973 | 3.82    |
| Recollida i neteja de l'espai urbà        | 10188 | 3.55    |
| Recollida orgànic / rebuig                | 9298  | 3.24    |
| Recollida paper cartó/vidre/reciclables   | 8837  | 3.08    |
| Neteja carrers i/o places                 | 7206  | 2.51    |
| Incidències instàncies i fulls de queixes | 6636  | 2.31    |

### Top `DETALL` values

| DETALL                                              | rows  | percent |
| --------------------------------------------------- | ----- | ------- |
| Objectes a netejar / retirar                        | 33409 | 11.63   |
| Portal de tràmits                                   | 19921 | 6.93    |
| Netejar pintada  cartell o pancarta en espai públic | 12501 | 4.35    |
| Vorera incidències                                  | 9401  | 3.27    |
| contenidors de paper i cartó/vidre/reciclables      | 6449  | 2.24    |
| Arbrat incidències                                  | 5895  | 2.05    |
| Espai personal                                      | 5271  | 1.83    |
| Netejar / retirar objectes perillosos               | 4801  | 1.67    |
| Parcs jardins i zones verdes incidències            | 4666  | 1.62    |
| Contenidor rebuig / orgànic                         | 4490  | 1.56    |

### Top `DISTRICTE` values

| DISTRICTE           | rows  | percent |
| ------------------- | ----- | ------- |
| (missing)           | 89852 | 31.27   |
| Eixample            | 34652 | 12.06   |
| Sant Martí          | 32370 | 11.27   |
| Sants-Montjuïc      | 22006 | 7.66    |
| Horta-Guinardó      | 20127 | 7.01    |
| Ciutat Vella        | 19942 | 6.94    |
| Nou Barris          | 17021 | 5.92    |
| Sant Andreu         | 16386 | 5.7     |
| Gràcia              | 15005 | 5.22    |
| Sarrià-Sant Gervasi | 12891 | 4.49    |

### Top `BARRI` values

| BARRI                          | rows  | percent |
| ------------------------------ | ----- | ------- |
| (missing)                      | 90680 | 31.56   |
| la Dreta de l'Eixample         | 8730  | 3.04    |
| el Raval                       | 6979  | 2.43    |
| la Vila de Gràcia              | 6197  | 2.16    |
| la Nova Esquerra de l'Eixample | 6157  | 2.14    |
| Sant Antoni                    | 5678  | 1.98    |
| el Poblenou                    | 5640  | 1.96    |
| Sant Andreu                    | 5623  | 1.96    |
| Sants                          | 5583  | 1.94    |
| el Barri Gòtic                 | 5562  | 1.94    |

### Top `SUPORT` values

| SUPORT                       | rows   | percent |
| ---------------------------- | ------ | ------- |
| MÒBIL                        | 104136 | 36.25   |
| WEB                          | 86958  | 30.27   |
| TELÈFON                      | 76719  | 26.7    |
| RECLAMACIÓ INTERNA           | 9848   | 3.43    |
| INSTÀNCIA TELEMÀTICA         | 5168   | 1.8     |
| INSTÀNCIA                    | 2107   | 0.73    |
| FULLS QUEIXES I SUGGERIMENTS | 1352   | 0.47    |
| ALTRES SUPORTS               | 350    | 0.12    |
| AUDIÈNCIA PÚBLICA            | 281    | 0.1     |
| CONSELL DE BARRI             | 172    | 0.06    |

## Generated outputs

- Daily registration counts: `data/processed/iris_daily_requests.csv`

## Interpretation notes

- These counts describe reported citizen activity, not every urban issue that occurred.

- Missing geography can reflect how a request was reported, classified, or published; it should not be treated as random without further checks.

- Duplicate rows are flagged for review. This report does not remove them.
