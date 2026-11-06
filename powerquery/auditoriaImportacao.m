let
    Nacional = Table.Group(stgPRF_Bruta, {"AnoArquivo", "ArquivoFonte"}, {{"LinhasFonteNacional", each Table.RowCount(_), Int64.Type}}),
    CE = Table.Group(Table.SelectRows(stgPRF_Bruta, each Text.Trim([uf])="CE"), {"AnoArquivo"}, {{"LinhasCE", each Table.RowCount(_), Int64.Type}}),
    Recorte = Table.Group(prfRecorte_Tratado, {"AnoArquivo"}, {{"LinhasRecorteAntes", each Table.RowCount(_), Int64.Type}, {"LinhasTratadas", each Table.RowCount(_), Int64.Type}, {"ComFlagQualidade", each Table.RowCount(Table.SelectRows(_, each [FlagQualidade])), Int64.Type}}),
    J1 = Table.NestedJoin(Nacional,{"AnoArquivo"},CE,{"AnoArquivo"},"CE",JoinKind.LeftOuter),
    E1 = Table.ExpandTableColumn(J1,"CE",{"LinhasCE"}),
    J2 = Table.NestedJoin(E1,{"AnoArquivo"},Recorte,{"AnoArquivo"},"Recorte",JoinKind.LeftOuter),
    E2 = Table.ExpandTableColumn(J2,"Recorte",{"LinhasRecorteAntes","LinhasTratadas","ComFlagQualidade"}),
    ForaEscopo = Table.AddColumn(E2,"ForaEscopo",each [LinhasFonteNacional]-[LinhasRecorteAntes],Int64.Type),
    ExcluidasQualidade = Table.AddColumn(ForaEscopo,"ExcluidasQualidade",each 0,Int64.Type),
    Atualizacao = Table.AddColumn(ExcluidasQualidade,"AtualizadoEmUTC",each DateTimeZone.RemoveZone(DateTimeZone.FixedUtcNow()),type datetime)
in Atualizacao
