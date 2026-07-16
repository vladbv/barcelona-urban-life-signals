# IRIS quality notes

Source file: `data/raw/2025_IRIS_Peticions_Ciutadanes_OpenData.csv`

## Duplicate `FITXA_ID` review

| metric                                              | value |
| --------------------------------------------------- | ----- |
| rows with duplicated FITXA_ID                       | 6786  |
| distinct duplicated FITXA_ID values                 | 3393  |
| max rows for one FITXA_ID                           | 2     |
| repeated FITXA_ID values after exact de-duplication | 0     |

### Example duplicated rows

| FITXA_ID | TIPUS      | AREA                               | ELEMENT                    | DETALL                       | DISTRICTE    | BARRI             | SUPORT | registration_date | closure_date |
| -------- | ---------- | ---------------------------------- | -------------------------- | ---------------------------- | ------------ | ----------------- | ------ | ----------------- | ------------ |
| 38770989 | CONSULTA   | Portal de tràmits                  | Relacions amb l'Ajuntament | Portal de tràmits            |              |                   | WEB    | 2025-01-02        | 2025-01-03   |
| 38770993 | INCIDENCIA | Manteniment de l'espai urbà        | Pilones                    | Pilones incidències          | Gràcia       | la Vila de Gràcia | MÒBIL  | 2025-01-02        | 2025-01-03   |
| 38771132 | INCIDENCIA | Recollida i neteja de l'espai urbà | Neteja carrers i/o places  | Objectes a netejar / retirar | Ciutat Vella | el Raval          | MÒBIL  | 2025-01-02        | 2025-01-03   |
| 38770999 | CONSULTA   | Portal de tràmits                  | Relacions amb l'Ajuntament | Portal de tràmits            |              |                   | WEB    | 2025-01-02        | 2025-01-03   |
| 38771126 | CONSULTA   | Portal de tràmits                  | Relacions amb l'Ajuntament | Portal de tràmits            |              |                   | WEB    | 2025-01-02        | 2025-01-03   |
| 38770989 | CONSULTA   | Portal de tràmits                  | Relacions amb l'Ajuntament | Portal de tràmits            |              |                   | WEB    | 2025-01-02        | 2025-01-03   |
| 38770999 | CONSULTA   | Portal de tràmits                  | Relacions amb l'Ajuntament | Portal de tràmits            |              |                   | WEB    | 2025-01-02        | 2025-01-03   |
| 38771126 | CONSULTA   | Portal de tràmits                  | Relacions amb l'Ajuntament | Portal de tràmits            |              |                   | WEB    | 2025-01-02        | 2025-01-03   |
| 38771132 | INCIDENCIA | Recollida i neteja de l'espai urbà | Neteja carrers i/o places  | Objectes a netejar / retirar | Ciutat Vella | el Raval          | MÒBIL  | 2025-01-02        | 2025-01-03   |
| 38770993 | INCIDENCIA | Manteniment de l'espai urbà        | Pilones                    | Pilones incidències          | Gràcia       | la Vila de Gràcia | MÒBIL  | 2025-01-02        | 2025-01-03   |

## Registration and closure timing

| metric                            | value  |
| --------------------------------- | ------ |
| rows                              | 287304 |
| registration before closure year  | 5284   |
| registration in closure year      | 282020 |
| negative closure-registration lag | 0      |
| min lag days                      | 0      |
| median lag days                   | 4      |
| 95th percentile lag days          | 34     |
| max lag days                      | 580    |

### Registration years inside this export

| registration_year | rows   | percent |
| ----------------- | ------ | ------- |
| 2023              | 2      | 0.0     |
| 2024              | 5282   | 1.84    |
| 2025              | 282020 | 98.16   |

### Top request types among records registered before their closure year

| TIPUS             | rows | percent |
| ----------------- | ---- | ------- |
| INCIDENCIA        | 2574 | 48.71   |
| QUEIXA            | 1491 | 28.22   |
| SUGGERIMENT       | 533  | 10.09   |
| CONSULTA          | 425  | 8.04    |
| PETICIO DE SERVEI | 236  | 4.47    |
| AGRAIMENT         | 16   | 0.3     |
| COMPLAINT         | 6    | 0.11    |
| ISSUE             | 2    | 0.04    |
| QUERY             | 1    | 0.02    |

### Oldest registration examples in this export

| FITXA_ID | TIPUS       | AREA                                    | ELEMENT                                    | DETALL                                      | DISTRICTE   | BARRI                                        | SUPORT             | registration_date | closure_date |
| -------- | ----------- | --------------------------------------- | ------------------------------------------ | ------------------------------------------- | ----------- | -------------------------------------------- | ------------------ | ----------------- | ------------ |
| 43871936 | INCIDENCIA  | Manteniment de l'espai urbà             | Senyals informatius                        | Senyal informatiu incidències               | Sant Andreu | la Trinitat Vella                            | WEB                | 2023-10-25        | 2025-05-02   |
| 38966896 | INCIDENCIA  | Informació  tràmits i atenció ciutadana | Incidències instàncies i fulls de queixes  | No ha rebut resposta                        |             |                                              | RECLAMACIÓ INTERNA | 2023-12-14        | 2025-03-10   |
| 39385940 | INCIDENCIA  | Manteniment de l'espai urbà             | Estructures vials                          | Element singular incidències                | Nou Barris  | la Guineueta                                 | RECLAMACIÓ INTERNA | 2024-01-23        | 2025-02-19   |
| 43872088 | SUGGERIMENT | Manteniment de l'espai urbà             | Lavabo públic                              | Lavabo públic automàtic nou / canvi de lloc | Sant Martí  | Diagonal Mar i el Front Marítim del Poblenou | TELÈFON            | 2024-02-27        | 2025-06-11   |
| 38756773 | QUEIXA      | Prevenció i seguretat                   | Incompliment d'ordenances a l'espai privat | Convivència veïnal                          | Sant Andreu | Sant Andreu                                  | WEB                | 2024-03-14        | 2025-02-10   |
| 46573061 | COMPLAINT   | Informació  tràmits i atenció ciutadana | Oficina per la No-Discriminació            | Oficina per la No-Discriminació             |             |                                              | WEB                | 2024-03-15        | 2025-10-16   |
| 38756860 | INCIDENCIA  | Informació  tràmits i atenció ciutadana | Incidències instàncies i fulls de queixes  | No ha rebut resposta                        |             |                                              | TELÈFON            | 2024-03-21        | 2025-02-26   |
| 38756508 | INCIDENCIA  | Informació  tràmits i atenció ciutadana | Incidències instàncies i fulls de queixes  | No ha rebut resposta                        |             |                                              | TELÈFON            | 2024-03-22        | 2025-01-21   |
| 43872126 | SUGGERIMENT | Manteniment de l'espai urbà             | Calçada                                    | Calçada petició pavimentació                | Sant Martí  | Diagonal Mar i el Front Marítim del Poblenou | RECLAMACIÓ INTERNA | 2024-03-27        | 2025-06-19   |
| 43872089 | SUGGERIMENT | Manteniment de l'espai urbà             | Lavabo públic                              | Lavabo públic automàtic nou / canvi de lloc | Sant Martí  | Provençals del Poblenou                      | TELÈFON            | 2024-04-02        | 2025-06-11   |

## Working interpretation

- The 2025 CSV appears to be organised by closure year, not purely by registration year. That explains why some records were opened before 2025 but closed during 2025.

- For first analysis, date choice must be explicit: registration date is better for demand/reporting rhythm; closure date is better for council resolution timing.

- The duplicate rows currently look safe to remove only as exact duplicates, because repeated `FITXA_ID` values disappear after exact de-duplication. This should be encoded as a reproducible cleaning rule in Milestone 2.
