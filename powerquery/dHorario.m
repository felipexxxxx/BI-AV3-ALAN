let
    Horas = List.Sort(List.Distinct(prfRecorte_Tratado[Hora])),
    T = Table.FromList(Horas, Splitter.SplitByNothing(), {"Hora"}),
    Tipos = Table.TransformColumnTypes(T, {{"Hora", Int64.Type}}),
    Rotulo = Table.AddColumn(Tipos, "FaixaHoraria", each if [Hora] = -1 then "Não informado" else Text.PadStart(Text.From([Hora]),2,"0") & ":00–" & Text.PadStart(Text.From([Hora]),2,"0") & ":59", type text)
in Rotulo
