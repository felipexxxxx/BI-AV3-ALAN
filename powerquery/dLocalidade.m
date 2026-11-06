let Fonte = prfRecorte_Tratado, Selecionada = Table.SelectColumns(Fonte, {"LocalidadeKey", "UF", "Municipio"}), Unica = Table.Distinct(Selecionada) in Unica
