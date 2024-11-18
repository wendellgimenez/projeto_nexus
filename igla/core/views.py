# Importa datetime para manipulação de datas e horas no Python.
from datetime import datetime
# Importa parsedate para processar datas em formatos de string, especialmente úteis ao trabalhar com datas em cabeçalhos HTTP.
from email.utils import parsedate
# Importa json para manipular dados em formato JSON (serializar e desserializar dados), comum em APIs.
import json
# Importa logging para registro de atividades (logs), útil para depuração e monitoramento do código em produção.
import logging
# Utiliza timezone do Django para lidar com fusos horários, especialmente ao armazenar e recuperar dados com informações de tempo.
from django.utils import timezone
# Importa render para renderizar templates HTML; redirect para redirecionar o usuário para outra página; e get_object_or_404 para retornar um objeto ou exibir um erro 404 se o objeto não existir.
from django.shortcuts import render, redirect, get_object_or_404
# Funções de autenticação do Django:
# - auth_login: permite o login de um usuário autenticado.
# - authenticate: valida as credenciais do usuário.
# - logout: realiza o logout do usuário atual.
from django.contrib.auth import login as auth_login, authenticate, logout
# Decorador que exige autenticação para acessar determinadas views, garantindo que o usuário esteja logado.
from django.contrib.auth.decorators import login_required
# Decorador para desabilitar a proteção contra CSRF em uma view específica.
from django.views.decorators.csrf import csrf_exempt
# Decorador para definir que uma view aceita apenas requisições POST, útil para restringir métodos HTTP.
from django.views.decorators.http import require_POST
# Importa messages para exibir mensagens de feedback para o usuário, como alertas e confirmações.
from django.contrib import messages
# Importa Paginator para dividir grandes conjuntos de dados em páginas, útil para listas extensas de informações.
from django.core.paginator import Paginator
# Importa formulários personalizados definidos no projeto:
# - CustomUserCreationForm: formulário de criação de usuário.
# - EscritorioForm, MatrizReceitasForm, MetasEscritorioForm: formulários personalizados para outras entidades do sistema.
from .forms import CustomUserCreationForm, EscritorioForm, MatrizReceitasForm, MetasEscritorioForm
# Importa modelos específicos da aplicação:
# - LogEntry, Profile, Escritorio, MetasEscritorio, MatrizReceitas: modelos para armazenar e gerenciar dados específicos da aplicação.
from .models import LogEntry, Profile, Escritorio, MetasEscritorio, MatrizReceitas
# Importa o modelo User padrão do Django, que representa usuários do sistema.
from django.contrib.auth.models import User
# JsonResponse permite o retorno de respostas JSON, frequentemente usado em APIs e endpoints AJAX.
from django.http import JsonResponse
# Importa Decimal e InvalidOperation para manipulação de números decimais com precisão e tratamento de erros.
from decimal import Decimal, InvalidOperation, ROUND_DOWN
# Importa connection para interagir diretamente com o banco de dados, usado em consultas SQL customizadas.
from django.db import connection
# settings fornece acesso às configurações globais do projeto Django, como variáveis e configurações de ambiente.
from django.conf import settings
# quote é usado para codificar URLs, útil ao lidar com strings de URL que precisam ser codificadas.
from urllib.parse import quote
# template é usado para carregar e manipular templates em Python.
from django import template
# psycopg2 é uma biblioteca para conectar-se a bancos de dados PostgreSQL no Python.
import psycopg2
# uuid é usado para gerar identificadores únicos universais (UUIDs), comuns em identificação de dados de forma única.
import uuid
#API para dados do mercado em tempo real
import yfinance as yf
#formatação brasileira de valores em R$
from locale import setlocale, LC_ALL

# View para renderizar a página inicial da aplicação
def index(request):
    """Renderiza a página inicial (index) da aplicação."""
    return render(request, 'core/index.html', {'is_index_page': True})

# View para renderizar a página principal do sistema
def home(request):
    """Renderiza a página principal do sistema."""
    return render(request, 'core/home.html')

def market_data(request):
    symbols = {
        "dolar": "BRL=X",
        "bitcoin": "BTC-USD",
        "ibov": "^BVSP",
        "sp500": "^GSPC",
    }

    top_brazilian_stocks = [
        "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC3.SA", "BBDC4.SA",
        "AMER3.SA", "MGLU3.SA", "GGBR4.SA", "SUZB3.SA", "LREN3.SA"
    ]

    top_world_stocks = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"
    ]

    data = {}

    def calcular_variacao(close_price, open_price):
        if open_price and open_price != 0:
            return ((close_price - open_price) / open_price) * 100
        return 0

    def obter_dados_ativo(symbol):
        try:
            stock = yf.Ticker(symbol)
            # Pegando dados do dia atual
            hist = stock.history(period="1d", interval="1d")
            
            if not hist.empty:
                open_price = hist['Open'].iloc[0]     # Preço de abertura
                close_price = hist['Close'].iloc[0]   # Preço atual/fechamento
                
                variation = calcular_variacao(close_price, open_price)
                
                print(f"{symbol}: Abertura={open_price}, Atual={close_price}, Variação={variation}%")  # Debug
                
                return {
                    "valor": round(close_price, 2),
                    "variacao": round(variation, 2)
                }
            else:
                print(f"{symbol}: Sem dados disponíveis")
                return {
                    "valor": 0.00,
                    "variacao": 0.00
                }
        except Exception as e:
            print(f"Erro ao processar {symbol}: {str(e)}")
            return {
                "valor": 0.00,
                "variacao": 0.00
            }

    # Processar mercados principais
    for name, symbol in symbols.items():
        result = obter_dados_ativo(symbol)
        if result:
            data[name] = result

    # Processar ações brasileiras
    for symbol in top_brazilian_stocks:
        result = obter_dados_ativo(symbol)
        if result:
            data[symbol] = result

    # Processar ações internacionais
    for symbol in top_world_stocks:
        result = obter_dados_ativo(symbol)
        if result:
            data[symbol] = result

    return JsonResponse(data)

# Mapeamento de meses em português para inglês
meses_map = {
    "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, 
    "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8, 
    "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
}

setlocale(LC_ALL, 'pt_BR.UTF-8')  # Configura a formatação brasileira

@login_required
def metas(request):
    conn = psycopg2.connect(
        dbname='postgres',
        user='postgres_sa',
        password='$72}AG49fIw3',
        host='superbase.c4p9rq34tafz.sa-east-1.rds.amazonaws.com',
        port=5432
    )

    with conn.cursor() as cursor:
        # Buscar valores únicos para os dropdowns
        cursor.execute("SELECT DISTINCT senioridade FROM dev_igla.comissoes_metas")
        senioridades = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT abrangencia FROM dev_igla.comissoes_metas")
        abrangencias = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT indicador FROM dev_igla.comissoes_metas")
        indicadores = [row[0] for row in cursor.fetchall()]

        # Buscar cargos e períodos únicos para popular os dropdowns
        cursor.execute("SELECT DISTINCT cargo FROM dev_igla.comissoes_metas")
        cargos = [row[0] for row in cursor.fetchall()]

        # Buscar períodos únicos para dropdown, ordenados do mais recente ao mais antigo
        cursor.execute("SELECT DISTINCT data_referencia FROM dev_igla.comissoes_metas ORDER BY data_referencia DESC")
        periodos = [row[0] for row in cursor.fetchall()]

        # Formatar os períodos no formato "Outubro 2024"
        periodos_formatados = [
            f"{list(meses_map.keys())[list(meses_map.values()).index(periodo.month)]} {periodo.year}"
            for periodo in periodos
        ]

        # Filtrar dados da tabela, caso cargo e período sejam selecionados
        cargo_selecionado = request.GET.get('cargo')
        periodo_selecionado = request.GET.get('periodo')

        # Conversão e formatação do período selecionado
        if periodo_selecionado:
            try:
                # Tenta separar o mês e o ano
                mes_nome, ano = periodo_selecionado.split(" ")
                mes = meses_map.get(mes_nome, None)  # Obtém o número do mês a partir do nome em português
                if mes:
                    # Cria a data no formato 'yyyy-mm-01'
                    periodo_selecionado = f"{ano}-{mes:01d}-01"
                    # Agora formata para o formato "Outubro 2024"
                    periodo_selecionado_formatado = datetime.strptime(periodo_selecionado, "%Y-%m-%d").strftime("%B %Y")
                    # Traduz o nome do mês para português
                    periodo_selecionado_formatado = periodo_selecionado_formatado.replace("January", "Janeiro").replace("February", "Fevereiro").replace("March", "Março").replace("April", "Abril").replace("May", "Maio").replace("June", "Junho").replace("July", "Julho").replace("August", "Agosto").replace("September", "Setembro").replace("October", "Outubro").replace("November", "Novembro").replace("December", "Dezembro")
                else:
                    periodo_selecionado = None
            except ValueError:
                periodo_selecionado = None
        else:
            periodo_selecionado_formatado = None

        if cargo_selecionado and periodo_selecionado:
            cursor.execute("""
                SELECT senioridade, abrangencia, indicador, valor_meta
                FROM dev_igla.comissoes_metas
                WHERE cargo = %s AND data_referencia = %s
            """, (cargo_selecionado, periodo_selecionado))
            rows = cursor.fetchall()
        else:
            rows = []

    conn.close()

    data = [
        {
            "senioridade": row[0],
            "abrangencia": row[1],
            "indicador": row[2],
            "valor_meta": f'R$ {Decimal(row[3]):,.2f}'.replace('.', 'X').replace(',', '.').replace('X', ','),  # Formatação brasileira
        }
        for row in rows
    ]

    context = {
        'data': data,
        'cargos': cargos,
        'periodos': periodos_formatados,
        'cargo_selecionado': cargo_selecionado,
        'periodo_selecionado': periodo_selecionado_formatado,
        'senioridades': senioridades,
        'abrangencias': abrangencias,
        'indicadores': indicadores,
    }
    return render(request, 'core/metas.html', context)

@login_required
def atualizar_meta(request):
    if request.method == "POST":
        try:
            # Carrega os dados do request
            data = json.loads(request.body.decode('utf-8'))
            print("Dados recebidos no backend:", data)

            # Extrai os valores do JSON
            senioridade = data.get('senioridade')
            abrangencia = data.get('abrangencia')
            indicador = data.get('indicador')
            valor_meta = data.get('valor_meta')
            
            # Valores originais
            senioridade_original = data.get('senioridade_original')
            abrangencia_original = data.get('abrangencia_original')
            indicador_original = data.get('indicador_original')
            valor_meta_original = data.get('valor_meta_original')

            # Verifica e converte valor_meta
            try:
                valor_meta = Decimal(valor_meta.replace(',', '.'))
                valor_meta_original = Decimal(valor_meta_original.replace(',', '.'))
            except InvalidOperation:
                return JsonResponse({"status": "error", "message": "Valor meta inválido."})

            # Conexão com o banco de dados
            conn = psycopg2.connect(
                dbname='postgres',
                user='postgres_sa',
                password='$72}AG49fIw3',
                host='superbase.c4p9rq34tafz.sa-east-1.rds.amazonaws.com',
                port=5432
            )

            with conn.cursor() as cursor:
                # Verifica a existência do registro original com todos os valores originais
                check_query = """
                    SELECT senioridade, abrangencia, indicador, valor_meta FROM dev_igla.comissoes_metas
                    WHERE senioridade = %s AND abrangencia = %s AND indicador = %s AND valor_meta = %s
                """
                print("Valores usados na verificação:", senioridade_original, abrangencia_original, indicador_original, valor_meta_original)
                cursor.execute(check_query, (senioridade_original, abrangencia_original, indicador_original, valor_meta_original))
                row = cursor.fetchone()
                print("Resultado da verificação:", row)

                # Atualiza se o registro original for encontrado
                if row:
                    update_query = """
                        UPDATE dev_igla.comissoes_metas
                        SET valor_meta = %s,
                            senioridade = %s,
                            abrangencia = %s,
                            indicador = %s
                        WHERE senioridade = %s
                          AND abrangencia = %s
                          AND indicador = %s
                          AND valor_meta = %s
                    """
                    cursor.execute(update_query, (
                        valor_meta, senioridade, abrangencia, indicador,
                        senioridade_original, abrangencia_original, indicador_original, valor_meta_original
                    ))
                    conn.commit()
                    print("Meta atualizada com sucesso")
                    result = {"status": "success", "message": "Meta atualizada com sucesso!"}
                else:
                    print("Nenhuma linha encontrada para atualizar.")
                    result = {"status": "error", "message": "Nenhuma linha encontrada para atualizar."}

            conn.close()
            return JsonResponse(result)

        except Exception as e:
            print(f"Erro durante a atualização: {str(e)}")
            return JsonResponse({"status": "error", "message": f"Erro ao atualizar meta: {str(e)}"})
    else:
        return JsonResponse({"status": "error", "message": "Método não permitido"})

# View para a página "ACD Liberta"
def acd_liberta(request):
    """Renderiza a página 'ACD Liberta'."""
    return render(request, 'core/acd_liberta.html')

# View para a página de alocação de produtos
def alocacao_produtos(request):
    """Renderiza a página de alocação de produtos."""
    return render(request, 'core/alocacao_produtos.html')

# View para a página "Assessoria Comercial"
def assessoria_comercial(request):
    """Renderiza a página 'Assessoria Comercial'."""
    return render(request, 'core/assessoria_comercial.html')

# View para a página de atendimento DGT
def atendimento_dgt(request):
    """Renderiza a página de atendimento DGT."""
    return render(request, 'core/atendimento_dgt.html')

# Função auxiliar para formatar uma data para o formato YYYY-MM-DD
def format_date(date_str):
    """Formata uma data fornecida para o formato 'YYYY-MM-DD'.
    
    Args:
        date_str (str): A data como string, nos formatos 'DD/MM/YYYY' ou 'YYYY-MM-DD'.
        
    Returns:
        str: A data formatada para 'YYYY-MM-DD'.
    
    Raises:
        ValueError: Se a data não corresponder aos formatos especificados.
    """
    for fmt in ('%d/%m/%Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    raise ValueError("Data no formato incorreto. Use DD/MM/YYYY ou YYYY-MM-DD.")

# Decorador para garantir que apenas usuários autenticados possam acessar essa view.
@login_required
def gerencial_assessoria(request):
    # Inicializa variáveis para armazenar os formulários que serão utilizados na view.
    # Esses formulários representam diferentes entidades: escritório, matriz de receitas e metas de escritório.
    escritorio_form = None
    matriz_receitas_form = None
    metas_escritorio_form = None

    # Verifica se a requisição é do tipo POST, indicando que há dados enviados pelo usuário para serem processados.
    if request.method == 'POST':
        # Verifica se o formulário submetido foi o de "Escritório".
        if 'escritorio_form' in request.POST:
            # Inicializa o formulário "EscritorioForm" com os dados enviados.
            escritorio_form = EscritorioForm(request.POST)
            # Valida o formulário, verificando se os dados estão corretos e completos.
            if escritorio_form.is_valid():
                # Salva o objeto escritório no banco de dados.
                escritorio = escritorio_form.save()
                
                # Registra a criação de um novo escritório no log, com o usuário que realizou a ação.
                LogEntry.objects.create(
                    user=request.user, # Usuário atual que realizou a ação.
                    action='Criação de Escritório', # Tipo de ação registrada.
                    details=f'Escritório criado. Valores: {{nome: {escritorio.nome}}}.', # Detalhes sobre o novo escritório criado.
                    timestamp=timezone.now() # Hora da ação registrada.
                )
                
                # Exibe uma mensagem de sucesso ao usuário indicando que o escritório foi cadastrado.
                messages.success(request, 'Escritório cadastrado com sucesso.')
                # Redireciona o usuário de volta à página gerencial.
                return redirect('gerencial_assessoria')

        # Caso o formulário enviado seja o de "Matriz de Receitas".
        elif 'matriz_receitas_form' in request.POST:
            # Inicializa o formulário "MatrizReceitasForm" com os dados enviados.
            matriz_receitas_form = MatrizReceitasForm(request.POST)
            # Valida o formulário para garantir que os dados estejam corretos.
            if matriz_receitas_form.is_valid():
                # Salva o objeto matriz de receitas no banco de dados.
                matriz_receitas_form.save()
                # Exibe uma mensagem de sucesso ao usuário.
                messages.success(request, 'Matriz de Receitas cadastrada com sucesso.')
                # Redireciona o usuário de volta à página gerencial.
                return redirect('gerencial_assessoria')
        
        # Caso o formulário submetido seja o de "Metas de Escritório".
        elif 'metas_escritorio_form' in request.POST:
            # Inicializa o formulário "MetasEscritorioForm" com os dados enviados.
            metas_escritorio_form = MetasEscritorioForm(request.POST)
            # Valida o formulário para verificar a completude e correção dos dados.
            if metas_escritorio_form.is_valid():
                # Salva a meta de escritório, mas sem confirmá-la no banco ainda.
                meta = metas_escritorio_form.save(commit=False)
                # Verifica se é uma atualização (meta já existe) ou uma criação (meta nova).
                # Se a meta já existe, define o usuário como atualizador; caso contrário, como criador.
                if meta.pk:
                    meta.updated_by = request.user
                else:
                    meta.created_by = request.user
                # Salva a meta com as informações do usuário criador ou atualizador.
                meta.save()

                # Se o período da meta começa com "dez/", cria metas para todos os meses do ano seguinte.
                if meta.periodo.startswith('dez/'):
                    # Extrai o ano atual do período.
                    ano_atual = int(meta.periodo.split('/')[1])
                    # Define o ano seguinte.
                    ano_proximo = ano_atual + 1
                    # Gera uma meta para cada mês do ano seguinte.
                    for mes in range(1, 13):
                        # Cria o período para cada mês (e.g., "jan/2025").
                        periodo = f"{['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'][mes-1]}/{ano_proximo}"
                        # Verifica se uma meta para o período já existe para evitar duplicação.
                        if not MetasEscritorio.objects.filter(periodo=periodo).exists():
                            # Cria uma nova meta para o mês, com valores iniciais.
                            MetasEscritorio.objects.create(
                                periodo=periodo,
                                meta_roa=0.00, # Valor inicial para meta ROA.
                                meta_nps=0.00, # Valor inicial para meta NPS.
                                created_by=request.user, # Usuário criador.
                                updated_by=request.user # Usuário atualizador.
                            )

                # Cria uma entrada de log para registrar a criação ou atualização da meta.
                LogEntry.objects.create(
                    user=request.user, # Usuário que realizou a ação.
                    action='Criação/Atualização de Meta de Escritório', # Ação realizada.
                    details=f'Meta de escritório {"criada" if not meta.pk else "atualizada"}. Valores: {{periodo: {meta.periodo}, meta_roa: {meta.meta_roa}, meta_nps: {meta.meta_nps}}}.', # Detalhes da meta criada ou atualizada.
                    timestamp=timezone.now() # Hora da ação.
                )

                # Exibe uma mensagem de sucesso indicando que a meta foi cadastrada ou atualizada.
                messages.success(request, 'Meta cadastrada/atualizada com sucesso.')
                # Redireciona o usuário de volta à página gerencial.
                return redirect('gerencial_assessoria')
        
        # Caso o formulário submetido seja para "Gerar metas para o próximo ano".
        elif 'gerar_ano' in request.POST:
            # Define o ano atual e o próximo ano com base na data e hora atual.
            ano_atual = timezone.now().year
            ano_proximo = ano_atual + 1
            # Filtra metas existentes do ano atual que começam com "jan/", indicando que o ano já possui metas definidas.
            metas_ano_atual = MetasEscritorio.objects.filter(periodo__startswith=f'jan/{ano_atual}')
            
            # Verifica se há metas do ano atual para possivelmente copiar para o próximo ano.
            if metas_ano_atual.exists():
                # Obtém a decisão do usuário sobre copiar metas do ano atual (com valor 'sim' ou 'nao').
                copiar_metas = request.POST.get('copiar_metas', 'nao') == 'sim'
                
                # Itera sobre os 12 meses para criar metas para cada um no próximo ano.
                for mes in range(1, 13):
                    # Define o período em formato "mês/ano" para cada mês do próximo ano.
                    periodo = f"{['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'][mes-1]}/{ano_proximo}"

                    # Verifica se uma meta para o período já existe, para evitar duplicação.
                    if not MetasEscritorio.objects.filter(periodo=periodo).exists():
                        # Se o usuário optou por copiar as metas do ano atual, obtém a meta correspondente do ano atual.
                        if copiar_metas:
                            # Busca a meta para o mesmo mês no ano atual.
                            meta_antiga = MetasEscritorio.objects.filter(periodo=f"{['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'][mes-1]}/{ano_atual}").first()
                            # Define os valores de ROA e NPS com base na meta antiga, ou 0.00 caso a meta antiga não exista.
                            meta_roa = meta_antiga.meta_roa if meta_antiga else 0.00
                            meta_nps = meta_antiga.meta_nps if meta_antiga else 0.00
                        else:
                            # Caso não copie as metas, inicializa os valores de ROA e NPS como 0.00.
                            meta_roa = 0.00
                            meta_nps = 0.00

                        # Cria uma nova meta para o próximo ano com os valores definidos.
                        MetasEscritorio.objects.create(
                            periodo=periodo,
                            meta_roa=meta_roa,
                            meta_nps=meta_nps,
                            created_by=request.user, # Usuário que criou a meta.
                            updated_by=request.user # Usuário que atualizou a meta.
                        )

                # Cria uma entrada de log registrando a criação das metas para o próximo ano.
                LogEntry.objects.create(
                    user=request.user, # Usuário que realizou a ação.
                    action='Geração de Metas para o Próximo Ano', # Ação registrada.
                    details=f'Metas para o ano {ano_proximo} foram criadas por {request.user.username}.', # Detalhes da ação.
                    timestamp=timezone.now() # Hora da ação.
                )

                # Exibe uma mensagem de sucesso informando que as metas para o próximo ano foram criadas.
                messages.success(request, 'Metas do próximo ano criadas com sucesso.')
            else:
                # Informa ao usuário que não há metas para o ano atual que possam ser copiadas.
                messages.info(request, 'Não há metas para o ano atual para copiar.')

            # Redireciona o usuário de volta para a página de gerenciamento.
            return redirect('gerencial_assessoria')
    
    # Caso a requisição não seja do tipo POST, inicializa formulários vazios para exibição na página.
    else:
        # Formulário para criação de um novo escritório.
        escritorio_form = EscritorioForm()
        # Formulário para criação de uma nova matriz de receitas.
        matriz_receitas_form = MatrizReceitasForm()
        # Formulário para criação ou atualização de metas de escritório.
        metas_escritorio_form = MetasEscritorioForm()
    
    # Obtém todos os escritórios cadastrados no banco de dados.
    escritorios = Escritorio.objects.all()

    # Obtém o ano selecionado pelo usuário para filtrar as metas (recebido como parâmetro na URL).
    ano_selecionado = request.GET.get('ano', '')

    # Define a ordem dos meses, usada para exibir as metas na sequência correta.
    ordem_meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']

    # Filtra as metas com base no ano selecionado pelo usuário.
    if ano_selecionado:
        # Obtém apenas as metas que contém o ano selecionado no campo período.
        metas = MetasEscritorio.objects.filter(periodo__icontains=f'{ano_selecionado}')
    else:
        # Se nenhum ano for selecionado, obtém todas as metas.
        metas = MetasEscritorio.objects.all()

    # Ordena as metas por ano e mês
    metas = sorted(
        metas, 
        key=lambda x: (
            int(x.periodo.split('/')[1]),  # Converte o ano (parte após a barra) para inteiro.
            ordem_meses.index(x.periodo.split('/')[0]) # Obtém o índice do mês na lista 'ordem_meses'.
        )
    )
    # Limita a lista a 12 metas, correspondendo a uma para cada mês.
    metas = metas[:12]

    # Obtém os anos distintos presentes nas metas cadastradas no banco de dados.
    anos = MetasEscritorio.objects.values_list('periodo', flat=True).distinct()
    # Extrai os anos das datas e os organiza em ordem crescente.
    anos = sorted(set(ano.split('/')[1] for ano in anos))

    # Extrai os filtros dos parâmetros de consulta GET enviados na URL.
    search_query = request.GET.get('search', '') # Pesquisa geral.
    filtro_xp = request.GET.get('filtro_xp', '') # Filtro para relatórios XP.
    filtro_categoria = request.GET.get('filtro_categoria', '') # Categoria de produto.
    filtro_linha_receita = request.GET.get('filtro_linha_receita', '') # Linha de receita.
    filtro_classe_ativo = request.GET.get('filtro_classe_ativo', '') # Classe do ativo.
    filtro_subclasse_ativo = request.GET.get('filtro_subclasse_ativo', '') # Subclasse do ativo.
    filtro_receita_comissoes = request.GET.get('filtro_receita_comissoes', '') # Receita de comissões.
    filtro_receita_ai = request.GET.get('filtro_receita_ai', '') # Receita AI.
    filtro_receita_escritorio = request.GET.get('filtro_receita_escritorio', '') # Receita do escritório.
    filtro_periodo = request.GET.get('filtro_periodo', '') # Período da receita.

    # Inicializa listas para armazenar as opções de filtros disponíveis.
    receitas = []
    opcoes_xp = []
    opcoes_categoria = []
    opcoes_linha_receita = []
    opcoes_classe_ativo = []
    opcoes_subclasse_ativo = []
    opcoes_receita_comissoes = []
    opcoes_receita_ai = []
    opcoes_receita_escritorio = []
    opcoes_periodo = []

    # Estabelece conexão com o banco de dados para coletar dados relevantes.
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres_sa',
            password='$72}AG49fIw3',
            host='superbase.c4p9rq34tafz.sa-east-1.rds.amazonaws.com',
            port=5432
        )
        cursor = conn.cursor()

        # Recupera a data mais recente de receitas para usar como referência padrão.
        cursor.execute("SELECT MAX(data_referencia) FROM dev_igla.linha_de_receita")
        data_mais_atual = cursor.fetchone()[0]
        
        # Coleta as opções distintas para cada filtro aplicável.
        cursor.execute("SELECT DISTINCT relatorio_xp FROM dev_igla.linha_de_receita")
        opcoes_xp = sorted([row[0] for row in cursor.fetchall()])

        cursor.execute("SELECT DISTINCT produto_categoria FROM dev_igla.linha_de_receita")
        opcoes_categoria = sorted([row[0] for row in cursor.fetchall()])

        cursor.execute("SELECT DISTINCT linha_de_receita FROM dev_igla.linha_de_receita")
        opcoes_linha_receita = sorted([row[0] for row in cursor.fetchall()])

        cursor.execute("SELECT DISTINCT classe_do_ativo FROM dev_igla.linha_de_receita")
        opcoes_classe_ativo = sorted([row[0] for row in cursor.fetchall()])

        cursor.execute("SELECT DISTINCT subclasse_do_ativo FROM dev_igla.linha_de_receita")
        opcoes_subclasse_ativo = sorted([row[0] for row in cursor.fetchall()])

        cursor.execute("SELECT DISTINCT receita_comissoes FROM dev_igla.linha_de_receita")
        opcoes_receita_comissoes = sorted([row[0] for row in cursor.fetchall()])

        cursor.execute("SELECT DISTINCT receita_ai FROM dev_igla.linha_de_receita")
        opcoes_receita_ai = sorted([row[0] for row in cursor.fetchall()])

        cursor.execute("SELECT DISTINCT receita_escritorio FROM dev_igla.linha_de_receita")
        opcoes_receita_escritorio = sorted([row[0] for row in cursor.fetchall()])

        cursor.execute("SELECT DISTINCT data_referencia FROM dev_igla.linha_de_receita ORDER BY data_referencia DESC")
        opcoes_periodo = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT DISTINCT produto_categoria_xp FROM dev_igla.repasses_contratuais")
        opcoes_produto_categoria_xp = [row[0] for row in cursor.fetchall()]

        # Recupera a data mais recente de referência nos repasses contratuais para validações adicionais.
        cursor.execute("SELECT MAX(data_referencia) FROM dev_igla.repasses_contratuais")
        data_referencia_mais_atual = cursor.fetchone()[0]

        # Ajusta o formato da data para o período, ou usa a data mais recente se não fornecida.
        if filtro_periodo:
            try:
                filtro_periodo = format_date(filtro_periodo)
            except ValueError:
                filtro_periodo = data_mais_atual.strftime('%Y-%m-%d')  # Se a data não for válida, use a mais atual

        # Monta a consulta SQL para buscar receitas com base nos filtros.
        query = """
            SELECT data_referencia, relatorio_xp, produto_categoria, linha_de_receita, 
                classe_do_ativo, subclasse_do_ativo, receita_comissoes, 
                receita_ai, receita_escritorio 
            FROM dev_igla.linha_de_receita
            WHERE (relatorio_xp ILIKE %s 
            OR produto_categoria ILIKE %s 
            OR linha_de_receita ILIKE %s 
            OR classe_do_ativo ILIKE %s 
            OR subclasse_do_ativo ILIKE %s)
            AND (%s = '' OR relatorio_xp = %s)
            AND (%s = '' OR produto_categoria = %s)
            AND (%s = '' OR linha_de_receita = %s)
            AND (%s = '' OR classe_do_ativo = %s)
            AND (%s = '' OR subclasse_do_ativo = %s)
            AND (%s = '' OR receita_comissoes = %s)
            AND (%s = '' OR receita_ai = %s)
            AND (%s = '' OR receita_escritorio = %s)
        """

        # Adiciona um filtro para a data de referência, com a data mais atual como padrão se não especificada.
        if filtro_periodo:
            query += " AND data_referencia = %s"
        else:
            filtro_periodo = data_mais_atual.strftime('%Y-%m-%d')
            query += " AND data_referencia = %s"

        # Define os parâmetros de busca, com o termo de pesquisa geral aplicado a múltiplos campos.
        search_param = f'%{search_query}%'
        params = [search_param] * 5 + [filtro_xp, filtro_xp, filtro_categoria, filtro_categoria,
                                        filtro_linha_receita, filtro_linha_receita, filtro_classe_ativo,
                                        filtro_classe_ativo, filtro_subclasse_ativo, filtro_subclasse_ativo,
                                        filtro_receita_comissoes, filtro_receita_comissoes, filtro_receita_ai, filtro_receita_ai,
                                        filtro_receita_escritorio, filtro_receita_escritorio, filtro_periodo]
        # Executa a consulta e armazena os resultados em 'receitas'.
        cursor.execute(query, params)
        receitas = cursor.fetchall()

        # Fecha o cursor e a conexão após a execução da consulta.
        cursor.close()
        conn.close()
    
    # Captura e exibe erros de conexão ou consulta para fins de depuração.
    except Exception as e:
        print(f"Erro ao buscar receitas: {e}")

    # Formulário para editar escritórios, instanciado com o formulário EscritorioForm
    editar_escritorios_form = EscritorioForm()

    # Configuração do paginador para dividir a exibição das receitas em páginas de 20 itens
    paginator = Paginator(receitas, 20)
    page_number = request.GET.get('page') # Obtém o número da página da URL
    page_obj = paginator.get_page(page_number) # Obtém a página correspondente ao número fornecido

    # Variável para armazenar o filtro de período para repasses (recebido da URL como parâmetro GET)
    filtro_periodo_repasse = request.GET.get('filtro_periodo_repasse', '')

    # Conexão ao banco de dados para obter opções de períodos de repasse
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres_sa',
            password='$72}AG49fIw3',
            host='superbase.c4p9rq34tafz.sa-east-1.rds.amazonaws.com',
            port=5432
        )
        cursor = conn.cursor()

        # Seleciona todos os períodos de referência disponíveis na tabela de repasses contratuais
        cursor.execute("SELECT DISTINCT data_referencia FROM dev_igla.repasses_contratuais ORDER BY data_referencia DESC")
        opcoes_periodo_repasse = [row[0] for row in cursor.fetchall()] # Lista de períodos disponíveis

        # Define o período mais recente como padrão se não houver filtro especificado
        if not filtro_periodo_repasse and opcoes_periodo_repasse:
            filtro_periodo_repasse = opcoes_periodo_repasse[0]

        # Fecha o cursor e a conexão com o banco de dados
        cursor.close()
        conn.close()
    except Exception as e:
        # Em caso de erro, imprime uma mensagem para facilitar o debug
        print(f"Erro ao buscar opções de período para repasses: {e}")

    # Lista para armazenar os dados dos repasses que serão consultados com base no filtro de período
    repasses = []
    try:
        # Nova conexão com o banco de dados para buscar dados de repasses
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres_sa',
            password='$72}AG49fIw3',
            host='superbase.c4p9rq34tafz.sa-east-1.rds.amazonaws.com',
            port=5432
        )
        cursor = conn.cursor()

        # Consulta SQL para buscar repasses filtrados pelo período selecionado
        query_repasses = """
            SELECT data_referencia, produto_categoria_xp, repasse_bruto, fee_fixo, fee_fixo_ex_rv 
            FROM dev_igla.repasses_contratuais
            WHERE data_referencia = %s
            ORDER BY data_referencia, produto_categoria_xp  -- Ordena pela data e categoria do produto
        """
        cursor.execute(query_repasses, [filtro_periodo_repasse]) # Executa a consulta com o filtro de período
        repasses = cursor.fetchall() # Recupera todos os resultados da consulta

        # Fecha o cursor e a conexão com o banco de dados
        cursor.close()
        conn.close()
    except Exception as e:
        # Em caso de erro, imprime uma mensagem para facilitar o debug
        print(f"Erro ao buscar repasses contratuais: {e}")

    # Chamada para atualização automática dos escritórios (detalhes da função não incluídos aqui)
    auto_update_escritorios()

    # Lista para armazenar os dados dos escritórios que serão consultados com base no filtro de período
    escritorios = []
    filtro_periodo_escritorio = request.GET.get('filtro_periodo_escritorio', '') # Filtro de período de escritórios
    try:
        # Nova conexão com o banco de dados para buscar dados dos escritórios
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres_sa',
            password='$72}AG49fIw3',
            host='superbase.c4p9rq34tafz.sa-east-1.rds.amazonaws.com',
            port=5432
        )
        cursor = conn.cursor()

        # Consulta para obter todos os períodos disponíveis de escritórios, ordenados do mais recente para o mais antigo
        cursor.execute("SELECT DISTINCT data_referencia FROM dev_igla.escritorios ORDER BY data_referencia DESC")
        opcoes_periodo_escritorio = [row[0] for row in cursor.fetchall()] # Lista de períodos disponíveis

        # Define o período mais recente como padrão se não houver filtro
        if not filtro_periodo_escritorio and opcoes_periodo_escritorio:
            filtro_periodo_escritorio = opcoes_periodo_escritorio[0]
        elif not opcoes_periodo_escritorio:
            # Define o primeiro dia do mês atual como padrão se não houver períodos disponíveis
            filtro_periodo_escritorio = datetime.now().replace(day=1).date()

        # Consulta para buscar escritórios com base no período selecionado
        cursor.execute("""
            SELECT e.data_referencia, e.codigo_escritorio, e.nome_escritorio, e.imposto,
                e.data_criacao, u.username
            FROM dev_igla.escritorios e
            LEFT JOIN dados_igla.auth_user u ON e.usuario_id = u.id
            WHERE e.data_referencia = %s
            ORDER BY e.codigo_escritorio
        """, [filtro_periodo_escritorio])
        escritorios = cursor.fetchall() # Armazena os escritórios obtidos na lista

        # Fecha o cursor e a conexão com o banco de dados
        cursor.close()
        conn.close()
    except Exception as e:
        # Em caso de erro, imprime uma mensagem para facilitar o debug
        print(f"Erro ao buscar escritórios: {e}")
        escritorios = [] # Em caso de erro, define a lista de escritórios como vazia
        opcoes_periodo_escritorio = [] # Em caso de erro, define as opções de período como vazia

    # Renderiza o template HTML com todos os dados e variáveis necessários para a exibição na página
    return render(request, 'core/gerencial_assessoria.html', {
        'receitas': receitas,
        'repasses': repasses,
        'escritorio_form': escritorio_form,
        'matriz_receitas_form': matriz_receitas_form,
        'metas_escritorio_form': metas_escritorio_form,
        'editar_escritorios_form': editar_escritorios_form,
        'escritorios': escritorios,
        'opcoes_periodo_escritorio': opcoes_periodo_escritorio,
        'filtro_periodo_escritorio': filtro_periodo_escritorio,
        'metas': metas,
        'page_obj': page_obj,
        'search_query': search_query,
        'opcoes_xp': opcoes_xp,
        'opcoes_categoria': opcoes_categoria,
        'opcoes_linha_receita': opcoes_linha_receita,
        'opcoes_classe_ativo': opcoes_classe_ativo,
        'opcoes_subclasse_ativo': opcoes_subclasse_ativo,
        'opcoes_receita_comissoes': opcoes_receita_comissoes,
        'opcoes_receita_ai': opcoes_receita_ai,  
        'opcoes_receita_escritorio': opcoes_receita_escritorio,
        'opcoes_periodo': opcoes_periodo,
        'opcoes_produto_categoria_xp': opcoes_produto_categoria_xp,
        'data_referencia_mais_atual': data_referencia_mais_atual,
        'opcoes_periodo_repasse': opcoes_periodo_repasse,
        'filtro_periodo_repasse': filtro_periodo_repasse,
        'filtro_periodo': filtro_periodo,
        'filtro_xp': filtro_xp,
        'filtro_categoria': filtro_categoria,
        'filtro_linha_receita': filtro_linha_receita,
        'filtro_classe_ativo': filtro_classe_ativo,
        'filtro_subclasse_ativo': filtro_subclasse_ativo,
        'filtro_receita_comissoes': filtro_receita_comissoes,
        'filtro_receita_ai': filtro_receita_ai,
        'filtro_receita_escritorio': filtro_receita_escritorio,
        'anos': anos,
        'ano_selecionado': ano_selecionado
    })

# Decorador para garantir que o usuário esteja logado antes de acessar a função
@login_required
# Decorador para exigir que a requisição seja do tipo POST
@require_POST
def editar_repasse(request):
    try:
        # Carrega os dados recebidos no corpo da requisição, que devem estar em formato JSON
        data = json.loads(request.body)
        
        # Extrai os dados específicos do JSON
        data_referencia = data['data_referencia'] # Data de referência do repasse
        produto_categoria_xp = data['produto_categoria_xp'] # Categoria do produto XP
        repasse_bruto = float(data['repasse_bruto']) # Valor bruto do repasse, convertido para float
        
        # Tratamento dos valores para as colunas fee_fixo e fee_fixo_ex_rv, garantindo que sejam 0 ou 1
        fee_fixo = 1 if data['fee_fixo'] == 1 else 0 # Se 'fee_fixo' for 1, define como 1; caso contrário, define como 0
        fee_fixo_ex_rv = 1 if data['fee_fixo_ex_rv'] == 1 else 0 # Se 'fee_fixo_ex_rv' for 1, define como 1; caso contrário, define como 0

        # Exibe no console os valores de fee_fixo e fee_fixo_ex_rv para depuração
        print(f'Fee Fixo: {fee_fixo}, Fee Fixo Ex RV: {fee_fixo_ex_rv}')  # Depuração para ver o que está sendo convertido

        # Inicia uma transação de atualização no banco de dados usando um cursor
        with connection.cursor() as cursor:
            # Executa a instrução SQL para atualizar o repasse no banco de dados
            cursor.execute(""" 
                UPDATE dev_igla.repasses_contratuais 
                SET produto_categoria_xp = %s, repasse_bruto = %s, fee_fixo = %s, fee_fixo_ex_rv = %s 
                WHERE data_referencia = %s 
                AND produto_categoria_xp = %s
            """, [produto_categoria_xp, repasse_bruto, fee_fixo, fee_fixo_ex_rv, data_referencia, produto_categoria_xp])

        # Registra uma entrada de log para a ação de edição
        LogEntry.objects.create(
            user=request.user, # Usuário que fez a modificação
            action='Edição de Repasse Contratual', # Descrição da ação
            details=f'Repasse contratual de {data_referencia} e categoria {produto_categoria_xp} editado.', # Detalhes adicionais
            timestamp=timezone.now() # Marca de tempo do registro
        )

        # Retorna uma resposta JSON indicando que a operação foi bem-sucedida
        return JsonResponse({'success': True})
    except Exception as e:
        # Em caso de erro, captura a exceção e retorna uma resposta JSON com os detalhes do erro
        import traceback # Importa módulo para exibir a pilha de chamadas em caso de exceção
        return JsonResponse({'success': False, 'error': str(e), 'traceback': traceback.format_exc()})

# Decorador para garantir que o usuário esteja logado antes de acessar a função
@login_required
# Decorador para exigir que a requisição seja do tipo POST
@require_POST
def excluir_repasse(request):
    # Carrega os dados enviados no corpo da requisição em formato JSON
    data = json.loads(request.body)
    
    # Separa os valores dos campos 'data_referencia' e 'produto_categoria_xp' a partir do valor recebido
    # Esses valores são passados juntos em um único campo e separados pelo caractere '|'
    data_referencia, produto_categoria_xp = data['data_referencia'].split('|')
    
    try:
        # Abre uma transação com o banco de dados usando um cursor para executar a operação SQL
        with connection.cursor() as cursor:
            # Executa a instrução SQL para excluir o registro no banco de dados
            # com base nos valores de 'data_referencia' e 'produto_categoria_xp' fornecidos
            cursor.execute("""
                DELETE FROM dev_igla.repasses_contratuais
                WHERE data_referencia = %s
                AND produto_categoria_xp = %s
            """, [data_referencia, produto_categoria_xp])

        # Cria uma entrada de log para registrar a exclusão do repasse
        LogEntry.objects.create(
            user=request.user, # Usuário que realizou a exclusão
            action='Exclusão de Repasse Contratual', # Tipo de ação para o log
            details=f'Repasse contratual de {data_referencia} e categoria {produto_categoria_xp} excluído.', # Detalhes da ação
            timestamp=timezone.now() # Marca de tempo do registro
        )

        # Retorna uma resposta JSON indicando que a operação foi bem-sucedida
        return JsonResponse({'success': True})
    except Exception as e:
        # Em caso de erro, captura a exceção e retorna uma resposta JSON com os detalhes do erro
        return JsonResponse({'success': False, 'error': str(e)})

# Decorador para garantir que o usuário esteja logado antes de acessar a função
@login_required
@require_POST
# Decorador para exigir que a requisição seja do tipo POST
def cadastrar_repasse(request):
    try:
        # Carrega os dados enviados no corpo da requisição em formato JSON
        data = json.loads(request.body)

        # Extrai os dados específicos do JSON para os campos do banco de dados
        data_referencia = data['data_referencia'] # Data de referência do repasse
        produto_categoria_xp = data['produto_categoria_xp'] # Categoria do produto XP
        repasse_bruto = float(data['repasse_bruto']) # Valor bruto do repasse, convertido para float
        fee_fixo = int(data['fee_fixo']) # Valor do campo fee_fixo, convertido para inteiro
        fee_fixo_ex_rv = int(data['fee_fixo_ex_rv']) # Valor do campo fee_fixo_ex_rv, convertido para inteiro

        # Inicia uma transação de inserção no banco de dados usando um cursor
        with connection.cursor() as cursor:
            # Executa a instrução SQL para inserir um novo registro no banco de dados
            cursor.execute("""
                INSERT INTO dev_igla.repasses_contratuais 
                (data_referencia, produto_categoria_xp, repasse_bruto, fee_fixo, fee_fixo_ex_rv)
                VALUES (%s, %s, %s, %s, %s)
            """, [data_referencia, produto_categoria_xp, repasse_bruto, fee_fixo, fee_fixo_ex_rv])

        # Cria uma entrada de log para registrar a adição do novo repasse
        LogEntry.objects.create(
            user=request.user, # Usuário que realizou o cadastro
            action='Cadastro de Repasse Contratual', # Tipo de ação para o log
            details=f'Repasse contratual de {data_referencia} e categoria {produto_categoria_xp} cadastrado.', # Detalhes da ação
            timestamp=timezone.now() # Marca de tempo do registro
        )

        # Retorna uma resposta JSON indicando que a operação foi bem-sucedida
        return JsonResponse({'success': True})
    except Exception as e:
        # Em caso de erro, captura a exceção e retorna uma resposta JSON com os detalhes do erro
        return JsonResponse({'success': False, 'error': str(e)})

# Registro de uma nova biblioteca de templates do Django
register = template.Library()

# Definição de um filtro customizado para multiplicar dois valores em templates do Django
@register.filter
def multiply(value, arg):
    try:
        # Tenta converter os argumentos para float e retorna o produto dos valores
        return float(value) * float(arg)
    except (ValueError, TypeError):
        # Se a conversão falhar, retorna o valor original inalterado
        return value

# Decorador para garantir que o usuário esteja autenticado
@login_required
# Decorador para desabilitar a proteção CSRF, permitindo requisições sem token CSRF (necessário apenas se houver motivos para ignorar CSRF)
@csrf_exempt
# Decorador para exigir que a requisição seja do tipo POST
@require_POST
def editar_receita(request, data_referencia):
    try:
        # Remove espaços extras ao redor de 'data_referencia' para evitar erros de formato
        data_referencia = data_referencia.strip()
        try:
            # Converte 'data_referencia' para o formato de data, validando o formato esperado
            data_referencia_formatada = datetime.strptime(data_referencia, '%Y-%m-%d').date()
        except ValueError as e:
            # Retorna erro caso a data esteja em formato incorreto
            return JsonResponse({'status': 'error', 'message': f'Formato de data inválido: {str(e)}'}, status=400)

        try:
            # Carrega o JSON enviado na requisição
            request_data = json.loads(request.body)
            # Obtém os dados atualizados e os dados originais para comparação
            data = request_data.get('data', {})
            original_data = request_data.get('originalData', {})
        except json.JSONDecodeError as e:
            # Retorna erro caso o JSON esteja mal formatado
            return JsonResponse({'status': 'error', 'message': f'Erro ao decodificar JSON: {str(e)}'}, status=400)

        # Verifica se os dados necessários estão presentes
        if not data or not original_data:
            return JsonResponse({'status': 'error', 'message': 'Dados ausentes no corpo da requisição.'}, status=400)

        # Conecta ao banco de dados e inicia uma transação com o cursor
        with connection.cursor() as cursor:
            # Executa uma consulta para verificar se a linha original existe no banco
            cursor.execute("""SELECT COUNT(*) FROM dev_igla.linha_de_receita
                              WHERE data_referencia = %s
                                AND relatorio_xp = %s
                                AND produto_categoria = %s
                                AND linha_de_receita = %s
                                AND classe_do_ativo = %s
                                AND subclasse_do_ativo = %s
                                AND receita_comissoes = %s
                                AND receita_ai = %s
                                AND receita_escritorio = %s""",
                           [original_data['data_referencia'],
                            original_data['relatorio_xp'],
                            original_data['produto_categoria'],
                            original_data['linha_de_receita'],
                            original_data['classe_do_ativo'],
                            original_data['subclasse_do_ativo'],
                            original_data['receita_comissoes'],
                            original_data['receita_ai'],
                            original_data['receita_escritorio']])
            count = cursor.fetchone()[0]

            # Se nenhuma linha for encontrada, retorna erro
            if count == 0:
                return JsonResponse({'status': 'error', 'message': 'Nenhuma linha encontrada para atualizar.'}, status=400)

            # Atualiza a linha da receita com os novos dados
            cursor.execute("""UPDATE dev_igla.linha_de_receita
                              SET relatorio_xp = %s,
                                  produto_categoria = %s,
                                  linha_de_receita = %s,
                                  classe_do_ativo = %s,
                                  subclasse_do_ativo = %s,
                                  receita_comissoes = %s,
                                  receita_ai = %s,
                                  receita_escritorio = %s
                              WHERE data_referencia = %s
                                AND relatorio_xp = %s
                                AND produto_categoria = %s
                                AND linha_de_receita = %s
                                AND classe_do_ativo = %s
                                AND subclasse_do_ativo = %s
                                AND receita_comissoes = %s
                                AND receita_ai = %s
                                AND receita_escritorio = %s""",
                           [data['relatorio_xp'],
                            data['produto_categoria'],
                            data['linha_de_receita'],
                            data['classe_do_ativo'],
                            data['subclasse_do_ativo'],
                            data['receita_comissoes'],
                            data['receita_ai'],
                            data['receita_escritorio'],
                            original_data['data_referencia'],
                            original_data['relatorio_xp'],
                            original_data['produto_categoria'],
                            original_data['linha_de_receita'],
                            original_data['classe_do_ativo'],
                            original_data['subclasse_do_ativo'],
                            original_data['receita_comissoes'],
                            original_data['receita_ai'],
                            original_data['receita_escritorio']])

            # Verifica o número de linhas afetadas pelo update
            rows_affected = cursor.rowcount

            # Se nenhuma linha foi atualizada, retorna erro
            if rows_affected == 0:
                return JsonResponse({'status': 'error', 'message': 'Nenhuma linha atualizada.'}, status=400)

            # Gera um log das mudanças realizadas
            log_details = []
            for key in data:
                if data[key] != original_data.get(key):
                    log_details.append(f'{key.replace("_", " ").capitalize()} alterado de {original_data.get(key)} para {data[key]}')

            # Se houve mudanças, cria um registro de log
            if log_details:
                LogEntry.objects.create(
                    user=request.user, # Usuário responsável pela edição
                    action='Edição de Receita', # Tipo de ação para o log
                    details=f'Receita com data referência {data_referencia_formatada} atualizada: ' + ', '.join(log_details), # Detalhes da edição
                    timestamp=timezone.now() # Data e hora da edição
                )

        # Retorna uma resposta de sucesso
        return JsonResponse({'status': 'success'})
    except Exception as e:
        # Captura exceções não tratadas e retorna uma resposta de erro
        return JsonResponse({'status': 'error', 'message': f'Ocorreu um erro: {str(e)}'}, status=500)

# Decorador para garantir que o usuário esteja autenticado
@login_required
# Decorador para desabilitar a proteção CSRF, permitindo requisições sem token CSRF (use apenas se necessário)
@csrf_exempt
# Decorador para exigir que a requisição seja do tipo POST
@require_POST
def excluir_receita(request, data_referencia):
    try:
        # Remove espaços extras ao redor de 'data_referencia' e formata a data
        data_referencia = data_referencia.strip()
        try:
            # Converte 'data_referencia' para o formato de data, validando o formato esperado (YYYY-MM-DD)
            data_referencia_formatada = datetime.strptime(data_referencia, '%Y-%m-%d').date()
        except ValueError as e:
            # Retorna erro caso a data esteja em formato incorreto
            return JsonResponse({'status': 'error', 'message': f'Formato de data inválido: {str(e)}'}, status=400)

        # Tenta decodificar o JSON recebido no corpo da requisição
        try:
            dados = json.loads(request.body)
            # Obtém os dados originais, caso estejam disponíveis no JSON
            original_data = dados.get('originalData', {})
        except json.JSONDecodeError as e:
            # Retorna erro caso o JSON esteja mal formatado
            return JsonResponse({'status': 'error', 'message': f'Erro ao decodificar JSON: {str(e)}'}, status=400)

        # Lista de campos que devem estar presentes nos dados originais
        campos_necessarios = ['relatorio_xp', 'produto_categoria', 'linha_de_receita', 'classe_do_ativo', 'subclasse_do_ativo', 'receita_comissoes', 'receita_ai', 'receita_escritorio']

        # Verifica se todos os campos necessários estão presentes e não são None
        for campo in campos_necessarios:
            if original_data.get(campo) is None:
                # Retorna erro caso algum campo esteja vazio ou ausente
                return JsonResponse({'status': 'error', 'message': f'O campo {campo} está vazio ou ausente.'}, status=400)

        # Prepara detalhes para registrar no log sobre a exclusão
        log_details = [
            f'Relatório XP: {original_data["relatorio_xp"]}',
            f'Produto Categoria: {original_data["produto_categoria"]}',
            f'Linha de Receita: {original_data["linha_de_receita"]}',
            f'Classe do Ativo: {original_data["classe_do_ativo"]}',
            f'Subclasse do Ativo: {original_data["subclasse_do_ativo"]}',
            f'Receita Comissões: {original_data["receita_comissoes"]}',
            f'Receita AI: {original_data["receita_ai"]}',
            f'Receita Escritório: {original_data["receita_escritorio"]}'
        ]

        # Conecta ao banco de dados e inicia uma transação com o cursor
        with connection.cursor() as cursor:
            # Executa a exclusão no banco de dados com base nos dados fornecidos
            rows_affected = cursor.execute("""
                DELETE FROM dev_igla.linha_de_receita
                WHERE data_referencia = %s
                AND relatorio_xp = %s
                AND produto_categoria = %s
                AND linha_de_receita = %s
                AND classe_do_ativo = %s
                AND subclasse_do_ativo = %s
                AND receita_comissoes = %s
                AND receita_ai = %s
                AND receita_escritorio = %s
            """, [
                data_referencia_formatada,
                original_data['relatorio_xp'],
                original_data['produto_categoria'],
                original_data['linha_de_receita'],
                original_data['classe_do_ativo'],
                original_data['subclasse_do_ativo'],
                original_data['receita_comissoes'],
                original_data['receita_ai'],
                original_data['receita_escritorio']
            ])

            # Conta o número de linhas afetadas pela exclusão
            rows_affected = cursor.rowcount

        # Confirma as mudanças no banco de dados
        connection.commit()

        # Verifica se alguma linha foi de fato excluída
        if rows_affected > 0:
            # Cria uma entrada de log para registrar a exclusão bem-sucedida
            LogEntry.objects.create(
                user=request.user, # Usuário que realizou a ação
                action='Exclusão de Receita', # Tipo de ação para o log
                details=f'Receita com data referência {data_referencia_formatada} excluída: ' + ', '.join(log_details), # Detalhes sobre os dados excluídos
                timestamp=timezone.now() # Data e hora da exclusão
            )
            # Retorna resposta de sucesso
            return JsonResponse({'status': 'success', 'message': 'Receita excluída com sucesso.'})
        else:
            # Caso nenhuma linha tenha sido encontrada para exclusão, retorna erro 404
            return JsonResponse({'status': 'error', 'message': 'Nenhuma linha encontrada para exclusão.'}, status=404)

    except Exception as e:
        # Captura qualquer exceção não tratada e imprime no console (útil para debug)
        print(f"Erro na view de exclusão: {str(e)}")
        # Retorna uma resposta de erro com status 500
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# Decorador para garantir que o usuário esteja autenticado antes de acessar esta view
@login_required
# Decorador para desabilitar a proteção CSRF (útil para testes ou casos específicos, mas use com cautela)
@csrf_exempt
def adicionar_receita(request):
    # Verifica se a requisição foi feita com o método POST
    if request.method == 'POST':
        try:
            # Extrai dados do corpo da requisição POST e armazena em um dicionário 'data'
            data = {
                'data_referencia': request.POST.get('nova_data_referencia'), # Data de referência da receita
                'relatorio_xp': request.POST.get('novo_relatorio_xp'), # Relatório XP relacionado à receita
                'produto_categoria': request.POST.get('novo_produto_categoria'), # Categoria do produto
                'linha_de_receita': request.POST.get('nova_linha_de_receita'), # Tipo ou linha de receita
                'classe_do_ativo': request.POST.get('nova_classe_do_ativo'), # Classe do ativo associado
                'subclasse_do_ativo': request.POST.get('nova_subclasse_do_ativo'), # Subclasse do ativo associado
                'receita_comissoes': request.POST.get('nova_receita_comissoes'), # Receita de comissões
                'receita_ai': request.POST.get('nova_receita_ai'), # Receita do ativo investido (AI)
                'receita_escritorio': request.POST.get('nova_receita_escritorio'), # Receita do escritório
            }

            # Exibe no console os dados recebidos, útil para depuração
            print("Dados recebidos:", data)

            # Conecta-se ao banco de dados e insere os dados na tabela 'linha_de_receita'
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO dev_igla.linha_de_receita
                    (data_referencia, relatorio_xp, produto_categoria, linha_de_receita,
                    classe_do_ativo, subclasse_do_ativo, receita_comissoes, receita_ai, receita_escritorio)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    data['data_referencia'], data['relatorio_xp'], data['produto_categoria'],
                    data['linha_de_receita'], data['classe_do_ativo'], data['subclasse_do_ativo'],
                    data['receita_comissoes'], data['receita_ai'], data['receita_escritorio']
                ])

            # Cria uma entrada de log após a inserção bem-sucedida para registrar a adição da receita
            LogEntry.objects.create(
                user=request.user, # Usuário que realizou a ação
                action='Adição de Receita', # Tipo de ação para o log
                details=f'Nova receita adicionada com data referência {data["data_referencia"]}', # Detalhes da adição
                timestamp=timezone.now() # Hora e data da ação
            )

            # Retorna resposta de sucesso em formato JSON
            return JsonResponse({'status': 'success'})
        except Exception as e:
            # Exibe a mensagem de erro no console (útil para depuração) e retorna uma resposta de erro
            print("Erro ao adicionar receita:", str(e))
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        # Retorna erro caso o método HTTP da requisição não seja POST
        return JsonResponse({'status': 'error', 'message': 'Método não permitido'})

# Decorador para garantir que o usuário esteja autenticado antes de acessar a view
@login_required
# Decorador para garantir que a requisição seja do tipo POST
@require_POST
def cadastrar_escritorio(request):
    try:
        # Extrai os dados do formulário a partir da requisição POST
        codigo = request.POST.get('codigo') # Código do escritório
        nome = request.POST.get('nome') # Nome do escritório
        irpj = request.POST.get('ir') # IRPJ do escritório

        # Converte o valor do IRPJ para float, trocando vírgulas por pontos para o formato decimal
        irpj = float(irpj.replace(',', '.'))

        # Define a data de referência como o primeiro dia do mês atual
        data_referencia = datetime.now().replace(day=1).date()
        
        # Conecta ao banco de dados PostgreSQL com as credenciais fornecidas
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres_sa',
            password='$72}AG49fIw3',
            host='superbase.c4p9rq34tafz.sa-east-1.rds.amazonaws.com',
            port=5432
        )
        cursor = conn.cursor() # Cria um cursor para realizar operações no banco
        
        # Verifica se já existe um escritório com o mesmo código e data de referência
        cursor.execute("""
            SELECT COUNT(*) FROM dev_igla.escritorios 
            WHERE codigo_escritorio = %s AND data_referencia = %s
        """, (codigo, data_referencia))
        
        # Caso exista um registro com o mesmo código e data de referência, gera uma exceção
        if cursor.fetchone()[0] > 0:
            raise Exception("Já existe um escritório com este código no período atual.")
        
        # Insere o novo escritório na tabela com os dados fornecidos e a data de criação
        cursor.execute("""
            INSERT INTO dev_igla.escritorios 
            (data_referencia, codigo_escritorio, nome_escritorio, imposto, data_criacao, usuario_id)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo', %s)
        """, (data_referencia, codigo, nome, irpj, request.user.id))
        
        # Confirma a inserção no banco de dados
        conn.commit()
        
        # Registra uma entrada de log para documentar o cadastro do novo escritório
        LogEntry.objects.create(
            user=request.user, # Usuário que realizou a ação
            action='Cadastro de Escritório', # Tipo de ação para o log
            details=f'Escritório {codigo} cadastrado. Nome: {nome}, IRPJ: {irpj}%.', # Detalhes do cadastro
            timestamp=timezone.now() # Hora e data da ação
        )
        
        # Fecha o cursor e a conexão com o banco de dados
        cursor.close()
        conn.close()
        
        # Envia uma mensagem de sucesso ao usuário para indicar que o cadastro foi concluído
        messages.success(request, 'Escritório cadastrado com sucesso!')
        # Redireciona o usuário para a página 'gerencial_assessoria'
        return redirect('gerencial_assessoria')
    
    # Tratamento de exceções em caso de erro no processo de cadastro
    except Exception as e:
        # Adiciona uma mensagem de erro com o motivo da falha
        messages.error(request, f'Erro ao cadastrar escritório: {str(e)}')
        # Redireciona o usuário para a página 'gerencial_assessoria'
        return redirect('gerencial_assessoria')

# Decorador para garantir que o usuário esteja autenticado
@login_required
# Decorador para garantir que a requisição seja do tipo POST
@require_POST
def editar_escritorio(request):
    try:
        codigo_escritorio = request.POST.get('codigo')
        nome = request.POST.get('nome')
        irpj = request.POST.get('irpj')
        replicar = request.POST.get('replicar') == 'true'  # Converte para booleano
        data_referencia = request.POST.get('data_referencia')  # Recebe a data de referência do front-end

        # Converte o valor do IRPJ para decimal antes de salvar
        irpj = float(irpj.replace(',', '.')) * 0.01

        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres_sa',
            password='$72}AG49fIw3',
            host='superbase.c4p9rq34tafz.sa-east-1.rds.amazonaws.com',
            port=5432
        )
        cursor = conn.cursor()

        if replicar:
            # Atualiza o valor de imposto para todas as linhas do período especificado
            cursor.execute("""
                UPDATE dev_igla.escritorios
                SET imposto = %s,
                    usuario_id = %s,
                    data_criacao = CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo'
                WHERE EXTRACT(YEAR FROM data_referencia) = EXTRACT(YEAR FROM %s::DATE)
                  AND EXTRACT(MONTH FROM data_referencia) = EXTRACT(MONTH FROM %s::DATE)
            """, (irpj, request.user.id, data_referencia, data_referencia))
        else:
            # Atualiza apenas a linha específica no período selecionado
            cursor.execute("""
                UPDATE dev_igla.escritorios
                SET nome_escritorio = %s,
                    imposto = %s,
                    usuario_id = %s,
                    data_criacao = CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo'
                WHERE codigo_escritorio = %s AND data_referencia = %s
            """, (nome, irpj, request.user.id, codigo_escritorio, data_referencia))

        conn.commit()
        cursor.close()
        conn.close()

        LogEntry.objects.create(
            user=request.user,
            action='Edição de Escritório',
            details=f'Escritório {codigo_escritorio} editado. Nome: {nome}, IRPJ: {irpj}%, Replicado: {replicar}.',
            timestamp=timezone.now()
        )

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

# Decorador para garantir que o usuário esteja autenticado
@login_required
# Decorador para garantir que a requisição seja do tipo POST
@require_POST
# Desabilita temporariamente a verificação CSRF (recomenda-se remover em produção)
@csrf_exempt
def excluir_escritorio(request):
    try:
        # Extrai o código do escritório a ser excluído a partir da requisição POST
        codigo_escritorio = request.POST.get('codigo')
        
        # Conecta ao banco de dados PostgreSQL com as credenciais fornecidas
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres_sa',
            password='$72}AG49fIw3',
            host='superbase.c4p9rq34tafz.sa-east-1.rds.amazonaws.com',
            port=5432
        )
        cursor = conn.cursor() # Cria um cursor para operações no banco de dados

        # Exclui todos os registros do escritório com o código fornecido
        cursor.execute("""
            DELETE FROM dev_igla.escritorios
            WHERE codigo_escritorio = %s
        """, (codigo_escritorio,))

        # Confirma a exclusão no banco de dados
        conn.commit()

        # Fecha o cursor e a conexão com o banco de dados
        cursor.close()
        conn.close()

        # Registra uma entrada de log para documentar a exclusão do escritório
        LogEntry.objects.create(
            user=request.user, # Usuário que realizou a exclusão
            action='Exclusão de Escritório', # Tipo de ação para o log
            details=f'Escritório {codigo_escritorio} excluído.', # Detalhes da exclusão
            timestamp=timezone.now() # Hora e data da ação
        )

        # Retorna uma resposta JSON de sucesso
        return JsonResponse({'success': True})

    # Tratamento de exceção em caso de erro no processo de exclusão
    except Exception as e:
        # Retorna uma resposta JSON com a mensagem de erro
        return JsonResponse({'success': False, 'message': str(e)})

# Função para atualização automática dos registros de escritórios para o mês atual
def auto_update_escritorios():
    try:
        # Conecta ao banco de dados PostgreSQL com as credenciais fornecidas
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres_sa',
            password='$72}AG49fIw3',
            host='superbase.c4p9rq34tafz.sa-east-1.rds.amazonaws.com',
            port=5432
        )
        cursor = conn.cursor() # Cria um cursor para interações com o banco de dados

        # Obtém a data do primeiro dia do mês atual
        current_date = datetime.now().replace(day=1).date()

        # Verifica se já existem registros para o mês atual
        cursor.execute("""
            SELECT COUNT(*) FROM dev_igla.escritorios
            WHERE data_referencia = %s
        """, (current_date,))
        
        count = cursor.fetchone()[0] # Obtém o número de registros encontrados

        # Caso não existam registros para o mês atual, insere cópias do mês anterior
        if count == 0:
            cursor.execute("""
                INSERT INTO dev_igla.escritorios (data_referencia, codigo_escritorio, nome_escritorio, imposto)
                SELECT DISTINCT ON (codigo_escritorio) %s, codigo_escritorio, nome_escritorio, imposto
                FROM dev_igla.escritorios
                WHERE data_referencia = (
                    SELECT MAX(data_referencia)
                    FROM dev_igla.escritorios
                    WHERE data_referencia < %s
                )
                ORDER BY codigo_escritorio, data_referencia DESC
            """, (current_date, current_date))

            # Conta o número de registros inseridos
            inserted_count = cursor.rowcount

            # Confirma a inserção dos novos registros
            conn.commit()
            print(f"Created {inserted_count} new records for {current_date.strftime('%B %Y')}")
        else:
            # Caso já existam registros para o mês atual, nenhuma ação é tomada
            print(f"Records for {current_date.strftime('%B %Y')} already exist. No action taken.")

        # Fecha o cursor e a conexão com o banco de dados
        cursor.close()
        conn.close()

    # Tratamento de exceção para capturar e exibir qualquer erro ocorrido
    except Exception as e:
        print(f"Error in auto_update_escritorios: {e}")

# Decorador para garantir que o usuário esteja autenticado ao acessar a view
@login_required
def metas_escritorio_view(request):
    # Verifica se a requisição é do tipo POST (submissão de formulário)
    if request.method == 'POST':
        form = MetasEscritorioForm(request.POST) # Inicializa o formulário com os dados enviados
        if form.is_valid(): # Verifica se os dados enviados são válidos
            meta = form.save() # Salva a nova meta no banco de dados

            # Registra a criação da nova meta no log
            LogEntry.objects.create(
                user=request.user, # Usuário que fez a criação
                action='Cadastro de Meta de Escritório', # Ação registrada no log
                details=f'Meta {meta} cadastrada com sucesso.', # Detalhes da ação
                timestamp=timezone.now() # Hora e data da ação
            )

            # Redireciona para a página de metas do escritório após o cadastro
            return redirect('metas_escritorio')
    else:
        # Inicializa o formulário vazio caso a requisição não seja POST
        form = MetasEscritorioForm()
    
    # Obtém todas as metas de escritório para exibir na página
    metas = MetasEscritorio.objects.all()

    # Renderiza a página 'gerencial_assessoria.html' com o formulário e as metas
    return render(request, 'gerencial_assessoria.html', {
        'form': form, # Formulário para o cadastro de metas
        'metas': metas, # Lista de metas de escritório
    })

# Decorador para garantir que o usuário esteja autenticado para acessar a função
@login_required
def editar_meta(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        meta = get_object_or_404(MetasEscritorio, id=id)

        # Obtém os novos valores do POST
        periodo = request.POST.get('periodo')
        meta_roa = request.POST.get('meta_roa')
        meta_nps = request.POST.get('meta_nps')

        old_values = {
            'periodo': meta.periodo,
            'meta_roa': meta.meta_roa,
            'meta_nps': meta.meta_nps
        }

        # Divide os valores por 100 antes de salvar no banco de dados
        if meta_roa:
            meta.meta_roa = float(meta_roa.replace(',', '.')) / 100
        if meta_nps:
            meta.meta_nps = float(meta_nps.replace(',', '.')) / 100

        meta.periodo = periodo or meta.periodo
        meta.updated_by = request.user
        meta.save()

        LogEntry.objects.create(
            user=request.user,
            action='Edição de Meta de Escritório',
            details=(f'Meta de escritório com ID {meta.id} editada. '
                     f'Valores antigos: {old_values}. '
                     f'Valores novos: {{periodo: {meta.periodo}, meta_roa: {meta.meta_roa}, meta_nps: {meta.meta_nps}}}.'),
            timestamp=timezone.now()
        )
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Método inválido'}, status=405)

# Decoradores para garantir que o usuário esteja autenticado e para desabilitar o CSRF (para uso em testes; remova o csrf_exempt em produção)
@csrf_exempt
@login_required
def excluir_meta(request):
    # Verifica se a requisição é do tipo POST (exclusão de dados)
    if request.method == 'POST':
        # Obtém o ID da meta a ser excluída a partir dos dados do formulário
        id = request.POST.get('id')

        try:
            # Tenta buscar o objeto MetasEscritorio com o ID fornecido
            meta = MetasEscritorio.objects.get(id=id)
            
            # Registra a ação de exclusão no log, incluindo os valores da meta excluída
            LogEntry.objects.create(
                user=request.user,
                action='Exclusão de Meta de Escritório', # Usuário que realizou a exclusão
                details=f'Meta de escritório com ID {meta.id} excluída. ' # Descrição da ação
                        f'Valores: {{periodo: {meta.periodo}, meta_roa: {meta.meta_roa}, meta_nps: {meta.meta_nps}}}.',
                timestamp=timezone.now() # Hora e data da exclusão
            )

            # Exclui o objeto do banco de dados
            meta.delete()

            # Retorna uma resposta JSON de sucesso para confirmar a exclusão
            return JsonResponse({'success': True})
        
        # Caso a meta não exista, retorna uma resposta JSON indicando falha
        except MetasEscritorio.DoesNotExist:
            return JsonResponse({'success': False})

def gestao_pessoas(request):
    # Conectando ao banco de dados PostgreSQL
    conn = psycopg2.connect(
        dbname='postgres',
        user='postgres_sa',
        password='$72}AG49fIw3',
        host='superbase.c4p9rq34tafz.sa-east-1.rds.amazonaws.com',
        port=5432
    )
    cursor = conn.cursor()

    # Lista com a ordem fixa de cargos para padronizar a exibição
    ordem_cargo_solides = [
        "AAI ACADEMIA - F1", "AAI ACADEMIA - F2", "AAI ACADEMIA - F3", "AAI ACADEMIA - F4", "AAI ACADEMIA - F5", 
        "AAI ACADEMIA - F6", "AAI COORDENADOR", "AAI ESPECIALISTA", "AAI JUNIOR", "AAI JUNIOR INVESTOR", 
        "AAI PLENO INVESTOR", "AAI LIDER DE EQUIPE", "AAI LIDER DE UNIDADE", "AAI PLENO", "AAI SENIOR", 
        "AAI SENIOR INVESTOR", "AAI SENIOR WEALTH", "AAI JUNIOR - SIX", "AAI PLENO/JUNIOR", "AAI SENIOR/PLENO", 
        "ESPECIALISTA BI", "ESPECIALISTA EM MERCADO INTERNACIONAL", 
        "ESPECIALISTA EM PLANEJAMENTO PATRIMONIAL E SUCESSORIO", "ESPECIALISTA EM PREVIDENCIA PRIVADA", 
        "HEAD DE ALOCACAO/PRODUTOS", "HEAD DE OPERACOES", "HEAD PROCESSOS E PERFORMANCE", "HEAD RENDA VARIAVEL", 
        "LÍDER DE EQUIPE", "SOCIO FUNDADOR", "AAI HUNTER", "AAI JUNIOR - B2B", "AAI SENIOR - B2B", "AAI SENIOR - B2B RV", 
        "ESPECIALISTA VIDA SENIOR", "ESPECIALISTA VIDA PLENO", "ESPECIALISTA EM CONSORCIO PLENO", 
        "ESPECIALISTA CONSORCIO SENIOR", "SEM CARGO", "ESPECIALISTA EM INVESTIMENTOS"
    ]

    # Lista com a ordem fixa de unidades para padronizar a exibição
    ordem_unidade_solides = [
        "CAMPINAS - B2B",
        "BALNEARIO CAMBORIU - TIMES SQUAD",
        "BALNEARIO CAMBORIU - GOAT",
        "BALNEARIO CAMBORIU - GALACTICOS",
        "BALNEARIO CAMBORIU",
        "LENCOIS PAULISTA - B2B",
        "MATRIZ - SPARTA",
        "MATRIZ - GOLDMAN",
        "SAO SEBASTIAO DO CAI - SPARTA",
        "SAO SEBASTIAO DO CAI - B2B",
        "MATRIZ - SQUAD SIX",
        "MATRIZ - INCUBADORA ACADEMIA",
        "MATRIZ - MANHATTAN",
        "LENCOIS PAULISTA - GOAT",
        "MATRIZ - WEALTH",
        "MATRIZ - LIBERTA DIGITAL",
        "MATRIZ - INCUBADORA INICIAL",
        "MATRIZ",
        "BALNEARIO CAMBORIU",
        "MATRIZ - BI",
        "PELOTAS",
        "FORTALEZA",
        "MATRIZ - HUNTER",
        "MATRIZ - EDUCACAO"
    ]

    # Inicialização das listas que vão armazenar os dados das abas
    cargos = []
    senioridades = []
    squads = []
    senioridade_options = []
    squad_options = []
    departamento_options = []
    cargo_options = []

    # Determina qual aba está ativa com base nos parâmetros de URL, padrão é 'cargos'
    active_tab = request.GET.get('tab', 'cargos')

    if active_tab == 'cargos':
        # Consulta para obter os dados de cargos
        cursor.execute(''' 
            SELECT data_referencia, data_criacao, departamento_solides, cargo_solides, departamento, cargo 
            FROM dev_igla.aai_cargos 
        ''')
        cargos = cursor.fetchall()

        # Ordena os cargos com base na lista `ordem_cargo_solides` para exibição padronizada
        cargos.sort(key=lambda x: ordem_cargo_solides.index(x[3]) if x[3] in ordem_cargo_solides else len(ordem_cargo_solides))

        # Obtem opções únicas de departamento e cargo para o filtro
        cursor.execute(''' 
            SELECT DISTINCT departamento FROM dev_igla.aai_cargos 
        ''')
        departamento_options = [row[0] for row in cursor.fetchall()]

        cursor.execute(''' 
            SELECT DISTINCT cargo FROM dev_igla.aai_cargos 
        ''')
        cargo_options = [row[0] for row in cursor.fetchall()]

        # Armazena valores selecionados para o filtro, se houver
        selected_departamento = request.GET.get('selected_departamento', '')
        selected_cargo = request.GET.get('selected_cargo', '')

    elif active_tab == 'senioridades':
        # Consulta para obter os dados de senioridades
        cursor.execute(''' 
            SELECT data_referencia, data_criacao, cargo_solides, senioridade 
            FROM dev_igla.aai_senioridades 
        ''')
        senioridades = cursor.fetchall()

        # Ordena as senioridades com base na lista `ordem_cargo_solides` para exibição padronizada
        senioridades.sort(key=lambda x: ordem_cargo_solides.index(x[2]) if x[2] in ordem_cargo_solides else len(ordem_cargo_solides))

        # Obtem opções únicas de senioridade
        cursor.execute(''' 
            SELECT DISTINCT senioridade FROM dev_igla.aai_senioridades 
        ''')
        senioridade_options = [row[0] for row in cursor.fetchall()]

        # Limpa seleção de departamento e cargo, pois não se aplicam a esta aba
        selected_departamento = ''
        selected_cargo = ''

    elif active_tab == 'squads':
        # Consulta para obter os dados de squads
        cursor.execute(''' 
            SELECT unidade_solides, squad 
            FROM dev_igla.aai_squads 
        ''')
        squads = cursor.fetchall()

        # Ordena os squads com base na lista `ordem_unidade_solides` para exibição padronizada
        squads.sort(key=lambda x: ordem_unidade_solides.index(x[0]) if x[0] in ordem_unidade_solides else len(ordem_unidade_solides))

        # Obtem opções únicas de squad para o filtro
        cursor.execute(''' 
            SELECT DISTINCT squad FROM dev_igla.aai_squads 
        ''')
        squad_options = [row[0] for row in cursor.fetchall()]

        # Limpa seleção de departamento e cargo, pois não se aplicam a esta aba
        selected_departamento = ''
        selected_cargo = ''

    # Fechando o cursor e a conexão com o banco de dados para liberar os recursos
    cursor.close()
    conn.close()

    # Renderiza o template HTML, passando as variáveis necessárias para exibição
    return render(request, 'core/gestao_pessoas.html', {
        'cargos': cargos,
        'senioridades': senioridades,
        'senioridade_options': senioridade_options,
        'squads': squads,
        'squad_options': squad_options,
        'departamento_options': departamento_options,
        'cargo_options': cargo_options,
        'active_tab': active_tab,
        'selected_departamento': selected_departamento,  # Passa o departamento selecionado
        'selected_cargo': selected_cargo,                # Passa o cargo selecionado
    })

# Função para atualizar informações de cargo no banco de dados e registrar a ação em um log
def update_cargo(request):
    # Verifica se o método de requisição é POST
    if request.method == 'POST':
        # Carrega os dados enviados na requisição em formato JSON
        data = json.loads(request.body)
        old_departamento = data.get('old_departamento') # Nome do departamento antigo
        new_departamento = data.get('new_departamento') # Nome do departamento novo
        old_cargo = data.get('old_cargo') # Nome do cargo antigo
        new_cargo = data.get('new_cargo') # Nome do cargo novo
        old_departamento_solides = data.get('old_departamento_solides') # Departamento em sistema externo (Solides)
        old_cargo_solides = data.get('old_cargo_solides') # Cargo em sistema externo (Solides)

        try:
            # Conecta ao banco de dados PostgreSQL
            conn = psycopg2.connect(
                dbname='postgres',
                user='postgres_sa',
                password='$72}AG49fIw3',
                host='superbase.c4p9rq34tafz.sa-east-1.rds.amazonaws.com',
                port=5432
            )
            cursor = conn.cursor()

            # Executa a atualização dos dados de cargo no banco de dados
            cursor.execute(''' 
                UPDATE dev_igla.aai_cargos 
                SET departamento = %s, cargo = %s 
                WHERE departamento_solides = %s AND cargo_solides = %s AND departamento = %s AND cargo = %s
            ''', (new_departamento, new_cargo, old_departamento_solides, old_cargo_solides, old_departamento, old_cargo))

            conn.commit() # Confirma a transação
            cursor.close() # Fecha o cursor
            conn.close() # Fecha a conexão com o banco

            # Cria uma entrada de log para registrar a atualização do cargo
            LogEntry.objects.create(
                user=request.user, # Cria uma entrada de log para registrar a atualização do cargo
                action='Atualização de Cargo', # Usuário que fez a requisição
                details=( # Detalhes da atualização
                    f'Cargo atualizado de {old_cargo} para {new_cargo} no departamento {old_departamento} '
                    f'para {new_departamento}, com referência aos dados de solides.'
                ),
                timestamp=timezone.now() # Hora da atualização
            )

            # Retorna uma resposta de sucesso
            return JsonResponse({'success': True})

        # Caso ocorra uma exceção, captura e retorna o erro
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

# Função para excluir um cargo do banco de dados e registrar a exclusão em um log
def delete_cargo(request):
    # Verifica se o método de requisição é POST
    if request.method == 'POST':
        # Carrega os dados enviados na requisição em formato JSON
        data = json.loads(request.body)
        old_departamento = data.get('old_departamento') # Nome do departamento antigo
        old_cargo = data.get('old_cargo') # Nome do cargo antigo
        old_departamento_solides = data.get('old_departamento_solides') # Departamento em sistema externo (Solides)
        old_cargo_solides = data.get('old_cargo_solides') # Cargo em sistema externo (Solides)
    
        # Log de depuração para verificar os dados que serão excluídos
        print(f"Tentando excluir: {old_departamento_solides} - {old_cargo_solides}")  # Log para depuração

        try:
            # Conecta ao banco de dados PostgreSQL
            conn = psycopg2.connect(
                dbname='postgres',
                user='postgres_sa',
                password='$72}AG49fIw3',
                host='superbase.c4p9rq34tafz.sa-east-1.rds.amazonaws.com',
                port=5432
            )
            cursor = conn.cursor()

            # Executa a exclusão do cargo no banco de dados
            cursor.execute('''
                DELETE FROM dev_igla.aai_cargos 
                WHERE departamento = %s AND cargo = %s 
                AND departamento_solides = %s AND cargo_solides = %s
            ''', (old_departamento, old_cargo, old_departamento_solides, old_cargo_solides))

            affected_rows = cursor.rowcount # Número de linhas afetadas pela operação
            print(f"Linhas afetadas: {affected_rows}")  # Log de depuração

            conn.commit() # Confirma a transação
            cursor.close() # Fecha o cursor
            conn.close() # Fecha a conexão com o banco

            # Verifica se algum registro foi excluído e registra no log
            if affected_rows > 0:
                LogEntry.objects.create(
                    user=request.user, # Usuário que fez a requisição
                    action='Exclusão de Cargo', # Ação realizada
                    details=( # Detalhes da exclusão
                        f'Cargo {old_cargo} no departamento {old_departamento} '
                        f'com referência solides ({old_cargo_solides}, {old_departamento_solides}) foi excluído.'
                    ),
                    timestamp=timezone.now() # Hora da exclusão
                )
                # Retorna uma resposta de sucesso
                return JsonResponse({'success': True})
            else:
                # Retorna erro se nenhum cargo for encontrado para exclusão
                return JsonResponse({'success': False, 'error': 'Nenhum cargo encontrado para exclusão'})

        # Captura e retorna o erro caso ocorra uma exceção
        except Exception as e:
            print(f"Erro ao excluir cargo: {str(e)}")  # Log de depuração
            return JsonResponse({'success': False, 'error': str(e)})

    # Retorna erro se o método de requisição não for POST
    return JsonResponse({'success': False, 'error': 'Método não permitido'})

# Função para atualizar o nível de senioridade de um cargo no banco de dados e registrar a ação em um log
def update_senioridade(request):
    # Verifica se o método de requisição é POST
    if request.method == 'POST':
        # Carrega os dados enviados na requisição em formato JSON
        data = json.loads(request.body)
        cargo_solides = data.get('cargo_solides')  # Cargo identificado no sistema Solides
        old_senioridade = data.get('old_senioridade')  # Nível de senioridade atual
        new_senioridade = data.get('new_senioridade')  # Novo nível de senioridade

        try:
            # Conecta ao banco de dados PostgreSQL
            conn = psycopg2.connect(
                dbname='postgres',
                user='postgres_sa',
                password='$72}AG49fIw3',
                host='superbase.c4p9rq34tafz.sa-east-1.rds.amazonaws.com',
                port=5432
            )
            cursor = conn.cursor()

            # Executa a atualização do nível de senioridade no banco de dados
            cursor.execute(''' 
                UPDATE dev_igla.aai_senioridades 
                SET senioridade = %s 
                WHERE cargo_solides = %s AND senioridade = %s
            ''', (new_senioridade, cargo_solides, old_senioridade))

            conn.commit()  # Confirma a transação
            cursor.close()  # Fecha o cursor
            conn.close()  # Fecha a conexão com o banco

            # Cria uma entrada de log para registrar a atualização da senioridade
            LogEntry.objects.create(
                user=request.user, # Usuário que fez a requisição
                action='Atualização de Senioridade', # Ação realizada
                details=( # Detalhes da atualização
                    f'Senioridade do cargo {cargo_solides} foi atualizada de {old_senioridade} para {new_senioridade}.'
                ),
                timestamp=timezone.now() # Hora da atualização
            )

            # Retorna uma resposta de sucesso
            return JsonResponse({'success': True})

        # Caso ocorra uma exceção, captura e retorna o erro
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

# Função para excluir o nível de senioridade de um cargo no banco de dados e registrar a exclusão em um log        
def delete_senioridade(request):
    # Verifica se o método de requisição é POST
    if request.method == 'POST':
        # Carrega os dados enviados na requisição em formato JSON
        data = json.loads(request.body)
        cargo_solides = data.get('cargo_solides') # Cargo identificado no sistema Solides
        senioridade = data.get('senioridade') # Nível de senioridade a ser excluído

        try:
            # Conecta ao banco de dados PostgreSQL
            conn = psycopg2.connect(
                dbname='postgres',
                user='postgres_sa',
                password='$72}AG49fIw3',
                host='superbase.c4p9rq34tafz.sa-east-1.rds.amazonaws.com',
                port=5432
            )
            cursor = conn.cursor()

            # Executa a exclusão do nível de senioridade no banco de dados
            cursor.execute('''
                DELETE FROM dev_igla.aai_senioridades 
                WHERE cargo_solides = %s AND senioridade = %s
            ''', (cargo_solides, senioridade))

            conn.commit()  # Confirma a transação
            cursor.close()  # Fecha o cursor
            conn.close()  # Fecha a conexão com o banco

            # Cria uma entrada de log para registrar a exclusão da senioridade
            LogEntry.objects.create(
                user=request.user, # Usuário que fez a requisição
                action='Exclusão de Senioridade', # Ação realizada
                details=f'Senioridade {senioridade} do cargo {cargo_solides} foi excluída.',
                timestamp=timezone.now() # Hora da exclusão
            )

            # Retorna uma resposta de sucesso
            return JsonResponse({'success': True})

        # Captura e retorna o erro caso ocorra uma exceção
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

# Função para atualizar o nome de um squad no banco de dados e registrar a ação em um log
def update_squad(request):
    # Verifica se o método de requisição é POST
    if request.method == 'POST':
        # Carrega os dados enviados na requisição em formato JSON
        data = json.loads(request.body)
        unidade_solides = data.get('unidade_solides')  # Unidade identificada no sistema Solides
        old_squad = data.get('old_squad')  # Nome atual do squad
        new_squad = data.get('new_squad')  # Novo nome do squad

        try:
            # Conecta ao banco de dados PostgreSQL
            conn = psycopg2.connect(
                dbname='postgres',
                user='postgres_sa',
                password='$72}AG49fIw3',
                host='superbase.c4p9rq34tafz.sa-east-1.rds.amazonaws.com',
                port=5432
            )
            cursor = conn.cursor()

            # Executa a atualização do nome do squad no banco de dados
            cursor.execute('''
                UPDATE dev_igla.aai_squads 
                SET squad = %s 
                WHERE unidade_solides = %s AND squad = %s
            ''', (new_squad, unidade_solides, old_squad))

            conn.commit()  # Confirma a transação
            cursor.close()  # Fecha o cursor
            conn.close()  # Fecha a conexão com o banco

            # Cria uma entrada de log para registrar a atualização do squad
            LogEntry.objects.create(
                user=request.user, # Usuário que fez a requisição
                action='Atualização de Squad', # Ação realizada
                details=( # Detalhes da atualização
                    f'Squad atualizado de {old_squad} para {new_squad} na unidade de solides {unidade_solides}.'
                ),
                timestamp=timezone.now() # Hora da atualização
            )

            # Retorna uma resposta de sucesso
            return JsonResponse({'success': True})

        # Captura e retorna o erro caso ocorra uma exceção
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

# Função para excluir um squad do banco de dados e registrar a exclusão em um log
def delete_squad(request):
    # Verifica se o método de requisição é POST
    if request.method == 'POST':
        # Carrega os dados enviados na requisição em formato JSON
        data = json.loads(request.body)
        unidade_solides = data.get('unidade_solides')  # Unidade identificada no sistema Solides
        squad = data.get('squad')  # Nome do squad a ser excluído

        try:
            # Conecta ao banco de dados PostgreSQL
            conn = psycopg2.connect(
                dbname='postgres',
                user='postgres_sa',
                password='$72}AG49fIw3',
                host='superbase.c4p9rq34tafz.sa-east-1.rds.amazonaws.com',
                port=5432
            )
            cursor = conn.cursor()

            # Executa a exclusão do squad no banco de dados
            cursor.execute('''
                DELETE FROM dev_igla.aai_squads 
                WHERE unidade_solides = %s AND squad = %s
            ''', (unidade_solides, squad))

            conn.commit()  # Confirma a transação
            cursor.close()  # Fecha o cursor
            conn.close()  # Fecha a conexão com o banco

            # Cria uma entrada de log para registrar a exclusão do squad
            LogEntry.objects.create(
                user=request.user, # Usuário que fez a requisição
                action='Exclusão de Squad', # Ação realizada
                details=f'Squad {squad} da unidade de solides {unidade_solides} foi excluído.', # Detalhes da exclusão
                timestamp=timezone.now() # Hora da exclusão
            )

            # Retorna uma resposta de sucesso
            return JsonResponse({'success': True})

        # Captura e retorna o erro caso ocorra uma exceção
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

# Função para renderizar a página de informações do usuário
@login_required  # Garante que apenas usuários autenticados possam acessar esta página
def info_user(request):
    # Renderiza o template 'info_user.html' e retorna como resposta
    return render(request, 'core/info_user.html')

# Função para renderizar a página de riqueza liberada (liberdade financeira)
def lib_wealth(request):
    # Renderiza o template 'lib_wealth.html' e retorna como resposta
    return render(request, 'core/lib_wealth.html')

# Função para renderizar a página de crédito cambial para pessoas jurídicas
def pj_cred_camb(request):
    # Renderiza o template 'pj_cred_camb.html' e retorna como resposta
    return render(request, 'core/pj_cred_camb.html')

# Função para renderizar a página relacionada a RV (Renda Variável)
def rv(request):
    # Renderiza o template 'rv.html' e retorna como resposta
    return render(request, 'core/rv.html')

# Função para renderizar a página de seguridade
def seguridade(request):
    # Renderiza o template 'seguridade.html' e retorna como resposta
    return render(request, 'core/seguridade.html')

# Função de visualização para o login
def login_view(request):
    # Limpa a sessão ao carregar a página de login, garantindo que não haja dados de sessão antigos
    request.session.flush()
    
    # Verifica se a solicitação é do tipo POST (submissão do formulário de login)
    if request.method == 'POST':
        email = request.POST.get('email') # Obtém o e-mail do formulário
        password = request.POST.get('password') # Obtém a senha do formulário
        
        try:
            # Tenta encontrar o usuário pelo e-mail fornecido
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Se o usuário não existir, exibe uma mensagem de erro e renderiza o template de login novamente
            messages.error(request, 'E-mail não cadastrado. Solicite acesso ao administrador do sistema')
            return render(request, 'core/login.html', {'is_index_page': True})

        # Autentica o usuário com base no nome de usuário e senha
        user = authenticate(request, username=user.username, password=password)
        
        # Se o usuário for autenticado com sucesso
        if user is not None:
            auth_login(request, user) # Realiza o login do usuário na sessão
            return redirect('home') # Redireciona para a página inicial
        else:
            # Se a autenticação falhar, exibe uma mensagem de erro
            messages.error(request, 'E-mail ou senha incorretos.')
            return render(request, 'core/login.html', {'is_index_page': True})

    # Se não for uma solicitação POST, renderiza a página de login
    return render(request, 'core/login.html', {'is_index_page': True})

# Função de visualização para registro de novos usuários
@login_required # Garante que apenas usuários autenticados possam acessar esta página
def register_view(request):
    # Verifica se a solicitação é do tipo POST (submissão do formulário de registro)
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST) # Cria uma instância do formulário com os dados do POST
        if form.is_valid(): # Verifica se o formulário é válido
            email = form.cleaned_data.get('email') # Obtém o e-mail do formulário
            
            # Verifica se o e-mail já está cadastrado
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Este e-mail já está cadastrado.') # Exibe uma mensagem de erro
                return render(request, 'core/register.html', {'form': form, 'hide_navbar': True})

            # Cria um usuário com uma senha aleatória (não será usada devido ao SSO)
            user = form.save(commit=False)  # Salva o usuário, mas não o comita ainda
            user.username = email.split('@')[0]  # Define o nome de usuário como a parte antes do '@' no e-mail
            user.set_password(str(uuid.uuid4()))  # Gera e define uma senha aleatória
            user.save()  # Salva o usuário no banco de dados

            # Cria ou obtém o perfil do usuário
            profile, created = Profile.objects.get_or_create(user=user)
            profile.department = form.cleaned_data.get('department') # Atribui o departamento ao perfil
            profile.user_level = form.cleaned_data.get('user_level') # Atribui o nível do usuário ao perfil
            profile.save() # Salva o perfil no banco de dados

            # Registra a ação no log
            LogEntry.objects.create(
                user=request.user, # Usuário que realizou a ação
                action='Registered a new user', #Tipo de ação
                details=f'User {user.username} registered with email {user.email} and user level {profile.user_level}.', # Detalhes da ação
                timestamp=timezone.now() # Data da ação
            )

            return redirect('info_user') # Redireciona para a página de informações do usuário
    else:
        form = CustomUserCreationForm() # Cria uma instância vazia do formulário se não for uma solicitação POST

    # Renderiza a página de registro, passando o formulário e ocultando a navbar
    return render(request, 'core/register.html', {'form': form, 'hide_navbar': True})

# Função para obter o e-mail pelo nome
def get_email_by_name(request):
    # Obtém o parâmetro 'name' da URL, ou None se não estiver presente
    name = request.GET.get('name', None)

    # Verifica se o nome foi fornecido
    if name:
        try:
            # Estabelece uma conexão com o banco de dados PostgreSQL
            conn = psycopg2.connect(
                dbname='postgres',
                user='postgres_sa',
                password='$72}AG49fIw3',
                host='superbase.c4p9rq34tafz.sa-east-1.rds.amazonaws.com',
                port=5432
            )
            cursor = conn.cursor() # Cria um cursor para executar comandos SQL

            # Executa uma consulta para buscar o e-mail do assessor com base no nome fornecido
            cursor.execute("SELECT username FROM dados_assessoria.d_assessores WHERE nome_ai = %s", [name])
            result = cursor.fetchone()  # Obtém o primeiro resultado da consulta
            cursor.close()  # Fecha o cursor
            conn.close()  # Fecha a conexão com o banco de dados
            
            # Se um resultado foi encontrado, retorna o e-mail em formato JSON
            if result:
                return JsonResponse({'email': result[0]})
        except Exception as e:
            # Se ocorrer um erro, retorna uma resposta JSON vazia com status 500
            return JsonResponse({'email': ''}, status=500)
        
    # Se o nome não foi fornecido ou nenhum resultado foi encontrado, retorna uma resposta JSON vazia
    return JsonResponse({'email': ''})

# Função para obter o departamento pelo nome
def get_department_by_name(request):
    # Obtém o parâmetro 'name' da URL, ou None se não estiver presente
    name = request.GET.get('name', None)

    # Verifica se o nome foi fornecido
    if name:
        try:
            # Estabelece uma conexão com o banco de dados PostgreSQL
            conn = psycopg2.connect(
                dbname='postgres',
                user='postgres_sa',
                password='$72}AG49fIw3',
                host='superbase.c4p9rq34tafz.sa-east-1.rds.amazonaws.com',
                port=5432
            )
            cursor = conn.cursor() # Cria um cursor para executar comandos SQL

            # Executa uma consulta para buscar o departamento do assessor com base no nome fornecido
            cursor.execute("SELECT departamento FROM dados_assessoria.d_assessores WHERE nome_ai = %s", [name])
            result = cursor.fetchone()  # Obtém o primeiro resultado da consulta
            cursor.close()  # Fecha o cursor
            conn.close()  # Fecha a conexão com o banco de dados
            
            # Se um resultado foi encontrado, retorna o departamento em formato JSON
            if result:
                return JsonResponse({'department': result[0]})
        except Exception as e:
            # Se ocorrer um erro, retorna uma resposta JSON vazia com status 500
            return JsonResponse({'department': ''}, status=500)
    
    # Se o nome não foi fornecido ou nenhum resultado foi encontrado, retorna uma resposta JSON vazia
    return JsonResponse({'department': ''})

# Função para gerenciar usuários
@login_required
def manage_users(request):
    # Faz a query para pegar todos os usuários e seus perfis
    users = User.objects.select_related('profile').all()

    # Verifica se a requisição é do tipo POST
    if request.method == 'POST':
        # Verifica se é uma solicitação para atualizar o nível de um usuário
        if 'update_user_level' in request.POST:
            user_id = request.POST.get('user_id')  # Obtém o ID do usuário a ser atualizado
            new_level = request.POST.get('user_level')  # Obtém o novo nível do usuário
            user = get_object_or_404(User, id=user_id)  # Busca o usuário pelo ID ou retorna 404 se não encontrado
            old_level = user.profile.user_level  # Obtém o nível antigo do usuário
            user.profile.user_level = new_level  # Atualiza o nível do usuário
            user.profile.save()  # Salva as alterações no perfil do usuário
            
            # Registrar log para a atualização do nível do usuário
            LogEntry.objects.create(
                user=request.user, # Usuário que fez a atualização
                action='Atualização de Nível de Usuário', # Ação registrada
                details=f'Nível do usuário {user.username} alterado de {old_level} para {new_level}.', # Detalhes da ação
                timestamp=timezone.now() # Data da ação
            )
            return redirect('manage_users') # Redireciona para a mesma página de gerenciamento de usuários

        # Verifica se é uma solicitação para excluir o usuário
        if 'delete_user' in request.POST:
            user_id = request.POST.get('user_id')  # Obtém o ID do usuário a ser excluído
            user = get_object_or_404(User, id=user_id)  # Busca o usuário pelo ID ou retorna 404 se não encontrado
            username = user.username  # Armazena o nome de usuário para registro no log
            user.delete()  # Exclui o usuário
            
            # Registrar log para a exclusão do usuário
            LogEntry.objects.create(
                user=request.user,  # Usuário que fez a exclusão
                action='Exclusão de Usuário',  # Ação registrada
                details=f'Usuário {username} excluído.',  # Detalhes do log
                timestamp=timezone.now()  # Timestamp da ação
            )
            return redirect('manage_users') # Redireciona para a mesma página de gerenciamento de usuários

    # Renderiza a página de gerenciamento de usuários com a lista de usuários
    return render(request, 'core/manage_users.html', {'users': users})

# Função para renderizar uma página de teste
def teste_view(request):
    return render(request, 'core/teste.html')  # Renderiza a página de teste

# Função para realizar logout do usuário
@login_required
def logout_view(request):
    logout(request)  # Realiza o logout do usuário
    request.session.flush()  # Limpa a sessão do usuário
    # Redireciona para a página de logout da Microsoft com um URL de redirecionamento
    return redirect('https://login.microsoftonline.com/common/oauth2/logout?post_logout_redirect_uri=http://localhost:8000/')

# Função para exibir logs de ações
def log_view(request):
    logs = LogEntry.objects.all().order_by('-timestamp')  # Obtém todos os logs e os ordena por timestamp (mais recentes primeiro)
    # Renderiza a página de logs com a lista de logs
    return render(request, 'core/log-igla.html', {'logs': logs})