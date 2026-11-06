let
    Anos = {2021..2025},
    Esperadas = {"id", "data_inversa", "dia_semana", "horario", "uf", "br", "km", "municipio", "causa_acidente", "tipo_acidente", "classificacao_acidente", "fase_dia", "sentido_via", "condicao_metereologica", "tipo_pista", "tracado_via", "uso_solo", "pessoas", "mortos", "feridos_leves", "feridos_graves", "ilesos", "ignorados", "feridos", "veiculos", "latitude", "longitude", "regional", "delegacia", "uop"},
    LerAno = (ano as number) as table => let
        Nome = "datatran" & Text.From(ano) & ".csv",
        CSV = Csv.Document(File.Contents(pPastaPRF & "\" & Nome), [Delimiter=";", Encoding=1252, QuoteStyle=QuoteStyle.Csv]),
        Cabecalhos = Table.PromoteHeaders(CSV, [PromoteAllScalars=true]),
        Verificada = if Table.ColumnNames(Cabecalhos) = Esperadas then Cabecalhos else error "Schema da fonte PRF alterado: " & Nome,
        Textos = Table.TransformColumnTypes(Verificada, List.Transform(Esperadas, each {_, type text})),
        Linha = Table.AddIndexColumn(Textos, "LinhaFonte", 2, 1, Int64.Type),
        Arquivo = Table.AddColumn(Linha, "ArquivoFonte", each Nome, type text),
        Ano = Table.AddColumn(Arquivo, "AnoArquivo", each ano, Int64.Type)
    in Ano,
    Combinada = Table.Combine(List.Transform(Anos, each LerAno(_)))
in Combinada
