# IRIS data profile

Generated from the locally downloaded Open Data BCN IRIS CSV.

## Source file

- Path: `data/raw/2026_IRIS_Peticions_Ciutadanes_OpenData_2026-10-02.csv`

- Rows: 72,326

- Observed CSV columns: 25

- Derived profiling columns: 2

## Date coverage

| date_field        | valid_rows | missing_or_invalid_rows | min_date   | max_date   |
| ----------------- | ---------- | ----------------------- | ---------- | ---------- |
| registration_date | 72326      | 0                       | 2025-02-13 | 2026-03-31 |
| closure_date      | 72326      | 0                       | 2026-01-01 | 2026-03-31 |

## Duplicate indicators

| duplicate_type    | rows |
| ----------------- | ---- |
| exact_full_row    | 1452 |
| repeated_fitxa_id | 1452 |

## Geographic missingness

| column         | missing_rows | missing_percent |
| -------------- | ------------ | --------------- |
| CODI_DISTRICTE | 24052        | 33.25           |
| DISTRICTE      | 24052        | 33.25           |
| CODI_BARRI     | 24203        | 33.46           |
| BARRI          | 24203        | 33.46           |
| SECCIO_CENSAL  | 57730        | 79.82           |
| COORDENADA_X   | 24203        | 33.46           |
| COORDENADA_Y   | 24203        | 33.46           |
| LONGITUD       | 24203        | 33.46           |
| LATITUD        | 24203        | 33.46           |

## Main classification distributions

### Top `TIPUS` values

| TIPUS             | rows  | percent |
| ----------------- | ----- | ------- |
| INCIDÈNCIA        | 43396 | 60.0    |
| CONSULTA          | 11274 | 15.59   |
| QUEIXA            | 8275  | 11.44   |
| SUGGERIMENT       | 5949  | 8.23    |
| PETICIO DE SERVEI | 3303  | 4.57    |
| AGRAIMENT         | 129   | 0.18    |

### Top `AREA` values

| AREA                                    | rows  | percent |
| --------------------------------------- | ----- | ------- |
| Recollida i neteja de l'espai urbà      | 21119 | 29.2    |
| Manteniment de l'espai urbà             | 19404 | 26.83   |
| Portal de tràmits                       | 7890  | 10.91   |
| Informació, tràmits i atenció ciutadana | 5448  | 7.53    |
| Mobilitat                               | 3520  | 4.87    |
| Gestions municipals                     | 2645  | 3.66    |
| Prevenció i seguretat                   | 2507  | 3.47    |
| Urbanisme                               | 2253  | 3.12    |
| Serveis socials                         | 1954  | 2.7     |
| Cultura                                 | 1408  | 1.95    |

### Top `ELEMENT` values

| ELEMENT                                 | rows | percent |
| --------------------------------------- | ---- | ------- |
| Neteja de l'espai públic                | 8506 | 11.76   |
| Relacions amb l'Ajuntament              | 7183 | 9.93    |
| Pintades / cartells / pancartes         | 3219 | 4.45    |
| Voreres                                 | 3196 | 4.42    |
| Arbrat                                  | 2866 | 3.96    |
| Recollida i neteja de l'espai urbà      | 2513 | 3.47    |
| Oficina Virtual de Tràmits              | 2429 | 3.36    |
| Recollida paper cartó/vidre/reciclables | 2274 | 3.14    |
| Recollida orgànic / rebuig              | 2265 | 3.13    |
| Recollida d'objectes perillosos         | 2150 | 2.97    |

### Top `DETALL` values

| DETALL                                              | rows | percent |
| --------------------------------------------------- | ---- | ------- |
| Objectes a netejar / retirar                        | 7327 | 10.13   |
| Portal de tràmits                                   | 4646 | 6.42    |
| Netejar pintada, cartell o pancarta en espai públic | 3197 | 4.42    |
| Vorera incidències                                  | 2774 | 3.84    |
| Netejar / retirar objectes perillosos               | 2150 | 2.97    |
| Espai personal                                      | 1888 | 2.61    |
| contenidors de paper i cartó/vidre/reciclables      | 1662 | 2.3     |
| Arbrat incidències                                  | 1568 | 2.17    |
| Calçada incidències                                 | 1479 | 2.04    |
| Incidències al portal de tràmits                    | 1264 | 1.75    |

### Top `DISTRICTE` values

| DISTRICTE           | rows  | percent |
| ------------------- | ----- | ------- |
| (missing)           | 24052 | 33.25   |
| Eixample            | 8527  | 11.79   |
| Sant Martí          | 7994  | 11.05   |
| Sants-Montjuïc      | 5385  | 7.45    |
| Horta-Guinardó      | 5111  | 7.07    |
| Ciutat Vella        | 4318  | 5.97    |
| Sant Andreu         | 3917  | 5.42    |
| Gràcia              | 3859  | 5.34    |
| Nou Barris          | 3641  | 5.03    |
| Sarrià-Sant Gervasi | 3623  | 5.01    |

### Top `BARRI` values

| BARRI                          | rows  | percent |
| ------------------------------ | ----- | ------- |
| (missing)                      | 24203 | 33.46   |
| la Dreta de l'Eixample         | 2242  | 3.1     |
| la Vila de Gràcia              | 1749  | 2.42    |
| el Raval                       | 1636  | 2.26    |
| la Nova Esquerra de l'Eixample | 1510  | 2.09    |
| Sant Andreu                    | 1379  | 1.91    |
| Sants                          | 1364  | 1.89    |
| la Sagrada Família             | 1329  | 1.84    |
| el Poblenou                    | 1312  | 1.81    |
| Sant Antoni                    | 1298  | 1.79    |

### Top `SUPORT` values

| SUPORT                       | rows  | percent |
| ---------------------------- | ----- | ------- |
| MÒBIL                        | 27749 | 38.37   |
| WEB                          | 22289 | 30.82   |
| TELÈFON                      | 18184 | 25.14   |
| RECLAMACIÓ INTERNA           | 1816  | 2.51    |
| INSTÀNCIA TELEMÀTICA         | 1225  | 1.69    |
| INSTÀNCIA                    | 554   | 0.77    |
| FULLS QUEIXES I SUGGERIMENTS | 279   | 0.39    |
| CONSELL DE BARRI             | 56    | 0.08    |
| AUDIÈNCIA PÚBLICA            | 53    | 0.07    |
| ALTRES SUPORTS               | 51    | 0.07    |

## Generated outputs

- Daily registration counts: `data/processed/iris_2026_daily_raw.csv`

## Interpretation notes

- These counts describe reported citizen activity, not every urban issue that occurred.

- Missing geography can reflect how a request was reported, classified, or published; it should not be treated as random without further checks.

- Duplicate rows are flagged for review. This report does not remove them.
