from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import csv
import hashlib
import io
import urllib.request
import urllib.parse
import zipfile
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw' / 'prf'
OUT = ROOT / 'output' / 'prf'
RAW.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
FILES = {
    2021: '12xH8LX9aN2gObR766YN3cMcuycwyCJDz',
    2022: '1PRQjuV5gOn_nn6UNvaJyVURDIfbSAK4-',
    2023: '1-WO3SfNrwwZ5_l7fRTiwBKRw7mi1-HUq',
    2024: '14lB0vqMFkaZj8HZ44b0njYgxs9nAN8KO',
    2025: '1-G3MdmHBt6CprDwcW99xxC4BZ2DU5ryR',
}
PAGE = 'https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf'
NUMERIC = ['id', 'br', 'km', 'pessoas', 'mortos', 'feridos_leves', 'feridos_graves',
           'ilesos', 'ignorados', 'feridos', 'veiculos', 'latitude', 'longitude']
COUNTS = ['pessoas', 'mortos', 'feridos_leves', 'feridos_graves', 'ilesos', 'ignorados', 'feridos', 'veiculos']

def download(item):
    year, file_id = item
    url = 'https://drive.usercontent.google.com/download?' + urllib.parse.urlencode({'id': file_id, 'export': 'download', 'confirm': 't'})
    zip_path = RAW / f'datatran{year}.zip'
    if not zip_path.exists():
        with urllib.request.urlopen(url, timeout=60) as response:
            blob = response.read()
        if not zipfile.is_zipfile(io.BytesIO(blob)):
            raise ValueError(f'Resposta de {year} nao e um ZIP')
        zip_path.write_bytes(blob)
    with zipfile.ZipFile(zip_path) as archive:
        names = [n for n in archive.namelist() if n.lower().endswith('.csv')]
        if len(names) != 1:
            raise ValueError(f'Quantidade inesperada de CSVs em {year}: {names}')
        blob = archive.read(names[0])
    csv_path = RAW / f'datatran{year}.csv'
    csv_path.write_bytes(blob)
    raw = pd.read_csv(csv_path, sep=';', encoding='cp1252', dtype=str, keep_default_na=False)
    raw['AnoArquivo'] = year
    raw['ArquivoFonte'] = csv_path.name
    raw['LinhaFonte'] = range(2, len(raw) + 2)
    manifest = {'ano': year, 'arquivo_csv': csv_path.name, 'arquivo_zip': zip_path.name,
                'linhas': len(raw), 'colunas_fonte': len(raw.columns)-3,
                'fonte_oficial': PAGE, 'url_download': url,
                'sha256_csv': hashlib.sha256(blob).hexdigest(),
                'sha256_zip': hashlib.sha256(zip_path.read_bytes()).hexdigest(),
                'coletado_utc': datetime.now(timezone.utc).isoformat()}
    return raw, manifest

def profile():
    with ThreadPoolExecutor(max_workers=5) as pool:
        result = list(pool.map(download, FILES.items()))
    full = pd.concat([v[0] for v in result], ignore_index=True)
    manifests = [v[1] for v in result]
    with (RAW / 'manifesto_fontes.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(manifests[0]))
        writer.writeheader(); writer.writerows(manifests)
    for c in full.columns:
        if full[c].dtype == object:
            full[c] = full[c].str.strip()
    ce = full.loc[full.uf.eq('CE')].copy()
    selected = ce.loc[pd.to_numeric(ce.br, errors='coerce').isin([116, 222])].copy()
    d = selected.copy()
    for c in NUMERIC:
        d[c] = pd.to_numeric(d[c].str.replace(',', '.', regex=False), errors='coerce')
    dates = pd.to_datetime(d.data_inversa, format='%Y-%m-%d', errors='coerce')
    times = pd.to_datetime(d.horario, format='%H:%M:%S', errors='coerce')
    raw_columns = [c for c in selected if c not in ['AnoArquivo', 'ArquivoFonte', 'LinhaFonte']]
    quality = {}
    quality['DataInvalida'] = dates.isna()
    quality['HorarioInvalido'] = times.isna()
    quality['IDInvalido'] = d.id.isna() | d.id.le(0) | d.id.mod(1).ne(0)
    quality['IDDuplicado'] = d.id.duplicated(keep=False)
    quality['KmInvalido'] = d.km.isna() | d.km.lt(0)
    quality['CoordenadaInvalida'] = d.latitude.isna() | d.longitude.isna() | ~d.latitude.between(-90,90) | ~d.longitude.between(-180,180) | (d.latitude.eq(0) & d.longitude.eq(0))
    quality['ContagemInvalida'] = d[COUNTS].isna().any(axis=1) | d[COUNTS].lt(0).any(axis=1) | d[COUNTS].mod(1).ne(0).any(axis=1)
    quality['FeridosDivergentes'] = d.feridos.ne(d.feridos_leves + d.feridos_graves)
    quality['PessoasDivergentes'] = d.pessoas.ne(d.mortos+d.feridos_leves+d.feridos_graves+d.ilesos+d.ignorados)
    quality['AnoArquivoDivergente'] = dates.dt.year.ne(d.AnoArquivo)
    quality['GravidadeDivergente'] = (d.mortos.gt(0) & d.classificacao_acidente.ne('Com Vítimas Fatais')) | (d.mortos.eq(0) & d.classificacao_acidente.eq('Com Vítimas Fatais'))
    weekdays = ['segunda-feira','terça-feira','quarta-feira','quinta-feira','sexta-feira','sábado','domingo']
    expected_weekday = dates.dt.dayofweek.map(dict(enumerate(weekdays)))
    quality['DiaSemanaDivergente'] = d.dia_semana.str.casefold().ne(expected_weekday)
    q = pd.DataFrame(quality, index=d.index)
    quality_counts = q.sum().astype(int)
    qout = pd.concat([selected[['id','AnoArquivo','ArquivoFonte','LinhaFonte']],q],axis=1)
    qout.to_csv(OUT/'flags_qualidade_fonte.csv',index=False,encoding='utf-8-sig')
    for name,data in [('fonte_nacional',full),('ceara',ce),('recorte',selected)]:
        data.groupby('AnoArquivo').size().rename('Linhas').to_csv(OUT/f'linhas_{name}.csv',encoding='utf-8-sig')
    summaries = []
    for col in raw_columns:
        summaries.append({'Coluna':col,'Vazios':int(selected[col].eq('').sum()),
                          'Distintos':int(selected[col].nunique()),
                          'ErrosConversao':int((d[col].isna() & selected[col].ne('')).sum()) if col in NUMERIC else 0,
                          'TipoFonte':'texto CSV','TipoInterpretado':str(d[col].dtype)})
    pd.DataFrame(summaries).to_csv(OUT/'perfil_colunas.csv',index=False,encoding='utf-8-sig')
    d['Data'] = dates
    d['Mes'] = dates.dt.strftime('%Y-%m')
    d['AcidenteGraveFatal'] = d.feridos_graves.gt(0)|d.mortos.gt(0)
    d['PlenaNoite'] = d.fase_dia.eq('Plena Noite')
    control = d.groupby(['Mes','br','municipio','tipo_acidente','classificacao_acidente','fase_dia'],dropna=False).agg(
        Acidentes=('id','size'),Pessoas=('pessoas','sum'),Feridos=('feridos','sum'),Mortes=('mortos','sum'),
        GravesFatais=('AcidenteGraveFatal','sum'),PlenaNoite=('PlenaNoite','sum')).reset_index()
    control.to_csv(OUT/'controle_reconciliacao.csv',index=False,encoding='utf-8-sig')
    totals = {'Acidentes':len(d),'Pessoas':int(d.pessoas.sum()),'FeridosLeves':int(d.feridos_leves.sum()),
              'FeridosGraves':int(d.feridos_graves.sum()),'Feridos':int(d.feridos.sum()),'Mortes':int(d.mortos.sum()),
              'Ilesos':int(d.ilesos.sum()),'Ignorados':int(d.ignorados.sum()),'Veiculos':int(d.veiculos.sum()),
              'GravesFatais':int(d.AcidenteGraveFatal.sum()),'PlenaNoite':int(d.PlenaNoite.sum())}
    pd.DataFrame([totals]).to_csv(OUT/'totais_controle.csv',index=False,encoding='utf-8-sig')
    pbix = ROOT/'BI.pbix'
    if pbix.exists():
        (OUT/'pbix_original.sha256').write_text(hashlib.sha256(pbix.read_bytes()).hexdigest(),encoding='ascii')
    lines=['# Diagnostico inicial da base PRF', '', '## Escopo e fonte',
           'Projeto aberto: BI. Tema: frequencia e gravidade dos acidentes nas BRs 116 e 222 no Ceara, 2021-2025.',
           'Fonte: '+PAGE, 'Arquivos por ocorrencia, preservados sem alteracao em data/raw/prf.',
           '', '## Granularidade e reducao',
           f'Fonte nacional: {len(full):,} linhas; CE: {len(ce):,}; CE e BR 116/222: {len(selected):,}.',
           f'Colunas originais: {len(raw_columns)}. Uma linha por ocorrencia; chave candidata id.',
           f'IDs repetidos no recorte: {d.id.duplicated().sum()}; IDs repetidos na fonte nacional consolidada: {full.id.duplicated().sum()}.',
           f'Linhas inteiramente iguais no recorte (30 campos originais): {selected.duplicated(raw_columns).sum()}.',
           f'Periodo: {dates.min().date()} a {dates.max().date()}.',
           'Nenhuma exclusao por qualidade, nenhum preenchimento artificial de datas, nenhuma remocao de duplicidades.',
           'A reducao e apenas tematica/geografica: CE, BR 116 ou BR 222; nao restringe a Fortaleza ou regiao metropolitana.',
           '', '## Temporal e campos incompativeis com o prompt logistico',
           'data_inversa = data do acidente; horario = horario do acidente. Nao existem datas de pedido, promessa ou entrega.',
           'Entregas pendentes, OTIF, receita, frete, custo, CO2, transportadora, modal logistico e avaliacoes nao se aplicam.',
           'Nenhum valor financeiro existe ou pode ser repetido por item; a base nao tem itens de pedido.',
           '', '## Dimensoes sustentadas',
           'Calendario; municipio/UF; rodovia e trecho por faixas analiticas de 10 km; tipo; causa registrada; classificacao da gravidade; circunstancias (fase do dia, pista, clima, tracado, sentido e uso do solo); faixa horaria.',
           'As faixas de 10 km sao agrupamentos de analise, nao trechos administrativos oficiais.',
           '', '## Verificacoes de qualidade']
    lines += [f'- {k}: {int(v)}' for k,v in quality_counts.items()]
    lines += ['', '## Categorias observadas']
    for c in ['classificacao_acidente','fase_dia','tipo_acidente','tipo_pista','uso_solo']:
        lines.append(f'- {c}: {d[c].value_counts().to_dict()}')
    lines += ['', '## Totais independentes de controle']+[f'- {k}: {v}' for k,v in totals.items()]
    lines += ['', '## Tipos, ausencias e erros',
              'Os arquivos CSV nao declaram tipos. id e br serao identificadores; data e horario serao convertidos; km, latitude e longitude usam virgula decimal e cultura pt-BR; contagens serao inteiras.',
              'O arquivo perfil_colunas.csv documenta tipos interpretados, vazios e erros de conversao por coluna.',
              '', '## Limitacoes',
              'As vitimas sao pessoas. O arquivo nao informa especies ou animais mortos, fluxo de trafego, custos, acao preventiva implantada ou efeito causal.',
              'Causas sao as registradas pela PRF e nao autorizam atribuir causalidade ou decidir automaticamente por radar.',
              'Registrar esta fotografia da coleta e hashes; publicacoes anuais podem ser retificadas.']
    (OUT/'diagnostico_inicial.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('\n'.join(lines))
    print('VAZIOS',[(x['Coluna'],x['Vazios'],x['ErrosConversao']) for x in summaries if x['Vazios'] or x['ErrosConversao']])
    return d

if __name__ == '__main__':
    profile()
