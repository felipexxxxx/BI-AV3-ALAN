from pathlib import Path
import csv
import json

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'powerquery'
DEST.mkdir(exist_ok=True)
OUT=ROOT/'output'/'prf'

def col(name,kind='String',key=False,hidden=False,description=''):
    return dict(name=name,dataType=kind,sourceColumn=name,isKey=key,isHidden=hidden,
                summarizeBy='None',description=description)

RAWCOLS=['id','data_inversa','dia_semana','horario','uf','br','km','municipio',
 'causa_acidente','tipo_acidente','classificacao_acidente','fase_dia','sentido_via',
 'condicao_metereologica','tipo_pista','tracado_via','uso_solo','pessoas','mortos',
 'feridos_leves','feridos_graves','ilesos','ignorados','feridos','veiculos','latitude',
 'longitude','regional','delegacia','uop']

def mlist(items):
    return '{'+', '.join('"'+x.replace('"','""')+'"' for x in items)+'}'

sources={
 'pPastaPRF': '"'+str(ROOT/'data'/'raw'/'prf')+'" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]',
 'stgPRF_Bruta': '''let
    Anos = {2021..2025},
    Esperadas = '''+mlist(RAWCOLS)+''',
    LerAno = (ano as number) as table => let
        Nome = "datatran" & Text.From(ano) & ".csv",
        CSV = Csv.Document(File.Contents(pPastaPRF & "\\" & Nome), [Delimiter=";", Encoding=1252, QuoteStyle=QuoteStyle.Csv]),
        Cabecalhos = Table.PromoteHeaders(CSV, [PromoteAllScalars=true]),
        Verificada = if Table.ColumnNames(Cabecalhos) = Esperadas then Cabecalhos else error "Schema da fonte PRF alterado: " & Nome,
        Textos = Table.TransformColumnTypes(Verificada, List.Transform(Esperadas, each {_, type text})),
        Linha = Table.AddIndexColumn(Textos, "LinhaFonte", 2, 1, Int64.Type),
        Arquivo = Table.AddColumn(Linha, "ArquivoFonte", each Nome, type text),
        Ano = Table.AddColumn(Arquivo, "AnoArquivo", each ano, Int64.Type)
    in Ano,
    Combinada = Table.Combine(List.Transform(Anos, each LerAno(_)))
in Combinada''',
 'prfRecorte_Tratado': '''let
    Fonte = stgPRF_Bruta,
    Recorte = Table.SelectRows(Fonte, each Text.Upper(Text.Trim([uf])) = "CE" and List.Contains({"116", "222"}, Text.Trim([br]))),
    Limpa = Table.TransformColumns(Recorte, List.Transform(List.RemoveItems(Table.ColumnNames(Recorte), {"LinhaFonte", "AnoArquivo"}), each {_, (v) => if v = null then null else Text.Trim(Text.Clean(v)), type nullable text})),
    Numero = (v as any) as nullable number => try Number.FromText(Text.From(v), "pt-BR") otherwise null,
    Inteiro = (v as any) as nullable number => let n = Numero(v) in if n = null then null else if Number.Mod(n,1) = 0 then n else null,
    Data = (v as any) as nullable date => try Date.FromText(v, [Format="yyyy-MM-dd", Culture="en-US"]) otherwise null,
    Hora = (v as any) as nullable time => try Time.FromText(v, [Format="HH:mm:ss", Culture="en-US"]) otherwise null,
    Dim = (v as nullable text) as text => if v = null then "Não informado" else if List.Contains({"", "NA", "N/A", "NULL"}, Text.Upper(v)) then "Não informado" else v,
    CamposInteiros = {"id", "br", "pessoas", "mortos", "feridos_leves", "feridos_graves", "ilesos", "ignorados", "feridos", "veiculos"},
    CamposDecimais = {"km", "latitude", "longitude"},
    FlagConversao = Table.AddColumn(Limpa, "FlagConversao", each let r = _ in Data([data_inversa]) = null or Hora([horario]) = null or List.AnyTrue(List.Transform(CamposInteiros, (c) => Inteiro(Record.Field(r,c)) = null)) or List.AnyTrue(List.Transform(CamposDecimais, (c) => Numero(Record.Field(r,c)) = null)), type logical),
    Numeros = Table.TransformColumns(FlagConversao, List.Combine({List.Transform(CamposInteiros, each {_, Inteiro, Int64.Type}), List.Transform(CamposDecimais, each {_, Numero, type number})})),
    Datas = Table.TransformColumns(Numeros, {{"data_inversa", Data, type nullable date}}),
    Renomeada = Table.RenameColumns(Datas, {
        {"id","IDAcidente"},{"data_inversa","DataAcidente"},{"dia_semana","DiaSemanaFonte"},{"horario","HorarioAcidente"},
        {"uf","UF"},{"br","BRNumero"},{"km","Km"},{"municipio","Municipio"},{"causa_acidente","CausaOriginal"},
        {"tipo_acidente","TipoOriginal"},{"classificacao_acidente","ClassificacaoOriginal"},{"fase_dia","FaseDia"},
        {"sentido_via","SentidoVia"},{"condicao_metereologica","CondicaoMeteorologica"},{"tipo_pista","TipoPista"},
        {"tracado_via","TracadoVia"},{"uso_solo","UsoSoloFonte"},{"pessoas","Pessoas"},{"mortos","Mortos"},
        {"feridos_leves","FeridosLeves"},{"feridos_graves","FeridosGraves"},{"ilesos","Ilesos"},{"ignorados","Ignorados"},
        {"feridos","Feridos"},{"veiculos","Veiculos"},{"latitude","Latitude"},{"longitude","Longitude"},
        {"regional","RegionalPRF"},{"delegacia","DelegaciaPRF"},{"uop","UOP"}}),
    BR = Table.AddColumn(Renomeada, "Rodovia", each "BR-" & Text.PadStart(Text.From([BRNumero]),3,"0"), type text),
    Inicio = Table.AddColumn(BR, "KmInicial", each if [Km] = null then null else Number.RoundDown([Km]/10)*10, Int64.Type),
    Fim = Table.AddColumn(Inicio, "KmFinalExclusivo", each if [KmInicial] = null then null else [KmInicial]+10, Int64.Type),
    Trecho = Table.AddColumn(Fim, "Trecho", each if [KmInicial] = null then "Não informado" else [Rodovia] & " · km " & Text.From([KmInicial]) & " a <" & Text.From([KmFinalExclusivo]), type text),
    LocalKey = Table.AddColumn(Trecho, "LocalidadeKey", each Dim([UF]) & "|" & Dim([Municipio]), type text),
    TrechoKey = Table.AddColumn(LocalKey, "TrechoKey", each Dim([UF]) & "|" & [Rodovia] & "|" & (if [KmInicial] = null then "NI" else Text.PadStart(Text.From([KmInicial]),6,"0")), type text),
    TipoKey = Table.AddColumn(TrechoKey, "TipoKey", each Dim([TipoOriginal]), type text),
    CausaKey = Table.AddColumn(TipoKey, "CausaKey", each Dim([CausaOriginal]), type text),
    GravidadeKey = Table.AddColumn(CausaKey, "GravidadeKey", each Dim([ClassificacaoOriginal]), type text),
    UsoSolo = Table.AddColumn(GravidadeKey, "UsoSolo", each if [UsoSoloFonte] = "Sim" then "Urbano" else if [UsoSoloFonte] = "Não" then "Rural" else "Não informado", type text),
    CondicoesKey = Table.AddColumn(UsoSolo, "CondicoesViaKey", each Text.Combine(List.Transform({[FaseDia],[SentidoVia],[CondicaoMeteorologica],[TipoPista],[TracadoVia],[UsoSoloFonte]}, each Dim(_)), "|"), type text),
    HoraNumero = Table.AddColumn(CondicoesKey, "Hora", each let h = Hora([HorarioAcidente]) in if h = null then -1 else Time.Hour(h), Int64.Type),
    Graves = Table.AddColumn(HoraNumero, "FlagGraveFatal", each if [FeridosGraves] = null or [Mortos] = null then null else [FeridosGraves] > 0 or [Mortos] > 0, type nullable logical),
    Noite = Table.AddColumn(Graves, "FlagPlenaNoite", each [FaseDia] = "Plena Noite", type logical),
    Soma = Table.AddColumn(Noite, "PessoasEstadosFisicos", each List.Sum({[Mortos],[FeridosLeves],[FeridosGraves],[Ilesos],[Ignorados]}), Int64.Type),
    FlagPessoas = Table.AddColumn(Soma, "FlagPessoasDivergentes", each [Pessoas] <> [PessoasEstadosFisicos], type logical),
    FlagFeridos = Table.AddColumn(FlagPessoas, "FlagFeridosDivergentes", each [Feridos] <> [FeridosLeves]+[FeridosGraves], type logical),
    FlagClasse = Table.AddColumn(FlagFeridos, "FlagClassificacaoDivergente", each ([Mortos] > 0 and [ClassificacaoOriginal] <> "Com Vítimas Fatais") or ([Mortos] = 0 and [ClassificacaoOriginal] = "Com Vítimas Fatais"), type logical),
    FlagClasseAusente = Table.AddColumn(FlagClasse, "FlagClassificacaoAusente", each [GravidadeKey] = "Não informado", type logical),
    FlagData = Table.AddColumn(FlagClasseAusente, "FlagDataInvalida", each [DataAcidente] = null or Date.Year([DataAcidente]) <> [AnoArquivo], type logical),
    FlagGeo = Table.AddColumn(FlagData, "FlagCoordenadaInvalida", each [Latitude] = null or [Longitude] = null or Number.Abs([Latitude]) > 90 or Number.Abs([Longitude]) > 180 or ([Latitude] = 0 and [Longitude] = 0), type logical),
    FlagContagem = Table.AddColumn(FlagGeo, "FlagContagemInvalida", each List.AnyTrue(List.Transform({[Pessoas],[Mortos],[FeridosLeves],[FeridosGraves],[Ilesos],[Ignorados],[Feridos],[Veiculos]}, each _ = null or _ < 0)), type logical),
    FlagKm = Table.AddColumn(FlagContagem, "FlagKmInvalido", each [Km] = null or [Km] < 0, type logical),
    Qualidade = Table.AddColumn(FlagKm, "FlagQualidade", each [FlagConversao] or [FlagPessoasDivergentes] or [FlagFeridosDivergentes] or [FlagClassificacaoDivergente] or [FlagClassificacaoAusente] or [FlagDataInvalida] or [FlagCoordenadaInvalida] or [FlagContagemInvalida] or [FlagKmInvalido], type logical)
in Qualidade'''
}
FACTCOLS=[col('IDAcidente','Int64',True),col('DataAcidente','DateTime'),col('HorarioAcidente'),
 *[col(k,hidden=True) for k in ['LocalidadeKey','TrechoKey','TipoKey','CausaKey','GravidadeKey','CondicoesViaKey']],
 col('Hora','Int64',hidden=True),col('Km','Double'),
 *[col(k,'Int64') for k in ['Pessoas','Mortos','FeridosLeves','FeridosGraves','Ilesos','Ignorados','Feridos','Veiculos','PessoasEstadosFisicos']],
 col('Latitude','Double'),col('Longitude','Double'),
 *[col(k,'Boolean') for k in ['FlagGraveFatal','FlagPlenaNoite','FlagConversao','FlagPessoasDivergentes','FlagFeridosDivergentes','FlagClassificacaoDivergente','FlagClassificacaoAusente','FlagDataInvalida','FlagCoordenadaInvalida','FlagContagemInvalida','FlagKmInvalido','FlagQualidade']],
 col('ClassificacaoOriginal'),col('DiaSemanaFonte'),col('RegionalPRF'),col('DelegaciaPRF'),col('UOP'),
 col('AnoArquivo','Int64'),col('ArquivoFonte'),col('LinhaFonte','Int64')]
tables=[]
def table(name,expression,columns,description,hidden=False):
    (DEST/(name+'.m')).write_text(expression+'\n',encoding='utf-8')
    tables.append(dict(name=name,mExpression=expression,columns=columns,description=description,isHidden=hidden,mode='Import'))

table('fAcidentes','Table.SelectColumns(prfRecorte_Tratado, '+mlist([c['name'] for c in FACTCOLS])+')',FACTCOLS,
      'Uma linha por acidente registrado pela PRF. Escopo CE, BR 116 ou 222, 2021-2025. Chave IDAcidente globalmente unica na fotografia coletada. Nenhuma exclusao por qualidade. Valores e classificacoes originais preservados; flags nao corrigem a fonte.')

def dim(name,sourcecols,renames=None,description=''):
    renames=renames or []
    selected=mlist([x[0] for x in sourcecols])
    m='let Fonte = prfRecorte_Tratado, Selecionada = Table.SelectColumns(Fonte, '+selected+'), Unica = Table.Distinct(Selecionada)'
    if name=='dCausa':
        m='let Fonte = prfRecorte_Tratado, Selecionada = Table.SelectColumns(Fonte, '+selected+'), Unica = Table.Group(Selecionada, {"CausaKey"}, {}, GroupKind.Global, Comparer.OrdinalIgnoreCase)'
    cols=[col(n,t,key=i==0,hidden=i==0) for i,(n,t) in enumerate(sourcecols)]
    if renames:
        m+=', Renomeada = Table.RenameColumns(Unica, {'+', '.join('{"'+a+'", "'+b+'"}' for a,b in renames)+'})'
        mp=dict(renames)
        for c in cols:c['name']=c['sourceColumn']=mp.get(c['name'],c['name'])
        m+=' in Renomeada'
    else:m+=' in Unica'
    if len(cols)==1:cols[0]['isHidden']=False
    table(name,m,cols,description)

dim('dLocalidade',[('LocalidadeKey','String'),('UF','String'),('Municipio','String')],description='Municipio e UF do acidente. Nao equivale a regiao metropolitana. Chave UF|Municipio; nao usa regional PRF como geografia administrativa.')
dim('dTrecho',[('TrechoKey','String'),('UF','String'),('BRNumero','Int64'),('Rodovia','String'),('KmInicial','Int64'),('KmFinalExclusivo','Int64'),('Trecho','String')],description='Agrupamento analitico em intervalos de 10 km: limite inferior inclusivo e superior exclusivo. Chave UF|BR|KmInicial. Nao representa trecho administrativo oficial.')
dim('dTipoAcidente',[('TipoKey','String')],[('TipoKey','TipoAcidente')],'Tipo principal do acidente publicado no CSV por ocorrencia. Nao equivale a todos os eventos da dinamica do acidente.')
dim('dCausa',[('CausaKey','String')],[('CausaKey','CausaRegistrada')],'Causa principal registrada pela PRF; nao constitui comprovacao causal independente.')
dim('dGravidade',[('GravidadeKey','String')],[('GravidadeKey','ClassificacaoPRF')],'Classificacao original da PRF. Sentinela NA e apresentada como Nao informado; original preservado na fato. Indicador grave/fatal e definido pelas contagens, sem corrigir a classificacao da fonte.')
dim('dCondicoesVia',[('CondicoesViaKey','String'),('FaseDia','String'),('SentidoVia','String'),('CondicaoMeteorologica','String'),('TipoPista','String'),('TracadoVia','String'),('UsoSoloFonte','String'),('UsoSolo','String')],description='Dimensao de combinacoes observadas das circunstancias da ocorrencia. UsoSolo Sim=Urbano e Nao=Rural conforme dicionario PRF.')

table('dHorario','''let
    Horas = List.Sort(List.Distinct(prfRecorte_Tratado[Hora])),
    T = Table.FromList(Horas, Splitter.SplitByNothing(), {"Hora"}),
    Tipos = Table.TransformColumnTypes(T, {{"Hora", Int64.Type}}),
    Rotulo = Table.AddColumn(Tipos, "FaixaHoraria", each if [Hora] = -1 then "Não informado" else Text.PadStart(Text.From([Hora]),2,"0") & ":00–" & Text.PadStart(Text.From([Hora]),2,"0") & ":59", type text)
in Rotulo''',[col('Hora','Int64',True),col('FaixaHoraria')],'Hora civil da ocorrencia em intervalos de uma hora; -1 reserva eventuais valores invalidos, sem apagar a ocorrencia.')

cal='''let
    Datas = List.RemoveNulls(prfRecorte_Tratado[DataAcidente]),
    Inicio = Date.StartOfYear(List.Min(Datas)),
    Fim = Date.EndOfYear(List.Max(Datas)),
    Lista = List.Dates(Inicio, Duration.Days(Fim-Inicio)+1, #duration(1,0,0,0)),
    T = Table.FromList(Lista, Splitter.SplitByNothing(), {"Data"}),
    Tipada = Table.TransformColumnTypes(T, {{"Data", type date}}),
    Ano = Table.AddColumn(Tipada, "Ano", each Date.Year([Data]), Int64.Type),
    MesNumero = Table.AddColumn(Ano, "MesNumero", each Date.Month([Data]), Int64.Type),
    MesNome = Table.AddColumn(MesNumero, "Mes", each Date.MonthName([Data], "pt-BR"), type text),
    AnoMes = Table.AddColumn(MesNome, "AnoMes", each Date.ToText([Data], "yyyy-MM", "pt-BR"), type text),
    AnoMesOrdem = Table.AddColumn(AnoMes, "AnoMesOrdem", each [Ano]*100+[MesNumero], Int64.Type),
    MesInicio = Table.AddColumn(AnoMesOrdem, "MesInicio", each Date.StartOfMonth([Data]), type date),
    TrimestreNumero = Table.AddColumn(MesInicio, "TrimestreNumero", each Date.QuarterOfYear([Data]), Int64.Type),
    Trimestre = Table.AddColumn(TrimestreNumero, "Trimestre", each "T" & Text.From([TrimestreNumero]), type text),
    Dia = Table.AddColumn(Trimestre, "Dia", each Date.Day([Data]), Int64.Type),
    DiaSemanaNumero = Table.AddColumn(Dia, "DiaSemanaNumero", each Date.DayOfWeek([Data], Day.Monday)+1, Int64.Type),
    DiaSemana = Table.AddColumn(DiaSemanaNumero, "DiaSemana", each Date.DayOfWeekName([Data], "pt-BR"), type text),
    FimSemana = Table.AddColumn(DiaSemana, "FimDeSemana", each [DiaSemanaNumero]>=6, type logical)
in FimSemana'''
table('dCalendario',cal,[col('Data','DateTime',True),col('Ano','Int64'),col('MesNumero','Int64'),col('Mes'),col('AnoMes'),col('AnoMesOrdem','Int64'),col('MesInicio','DateTime'),col('TrimestreNumero','Int64'),col('Trimestre'),col('Dia','Int64'),col('DiaSemanaNumero','Int64'),col('DiaSemana'),col('FimDeSemana','Boolean')],
 'Calendario diario continuo de anos completos, governado por DataAcidente, unica data de negocio na fonte. Sem feriados presumidos e sem relacionamentos de outras datas inexistentes.')

audit='''let
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
in Atualizacao'''
table('auditoriaImportacao',audit,[col('AnoArquivo','Int64',True),col('ArquivoFonte'),*[col(k,'Int64') for k in ['LinhasFonteNacional','LinhasCE','LinhasRecorteAntes','LinhasTratadas','ComFlagQualidade','ForaEscopo','ExcluidasQualidade']],col('AtualizadoEmUTC','DateTime')],'Contagens rastreaveis por arquivo; reducao apenas por escopo; nenhuma exclusao por qualidade. AtualizadoEmUTC e a atualizacao do modelo, nao a data de revisao da PRF. Tabela tecnica sem relacionamento.',True)

for name,expression in sources.items():
    (DEST/(name+'.m')).write_text(expression+'\n',encoding='utf-8')

if __name__=='__main__':
    schema=[]
    for t in tables:
        for c in t['columns']:schema.append({'Tabela':t['name'],'Coluna':c['name'],'Tipo':c['dataType'],'Chave':c['isKey'],'Oculta':c['isHidden']})
    with (OUT/'dicionario_modelo.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(schema[0]));w.writeheader();w.writerows(schema)
    print(json.dumps({'expressions':[dict(name=k,kind='M',expression=v,description='Consulta rastreavel da fonte PRF; nao carregada como tabela do modelo.') for k,v in sources.items()], 'tables':tables},ensure_ascii=True))
