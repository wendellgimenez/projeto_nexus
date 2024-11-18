// Espera que o DOM esteja completamente carregado para executar o código.
document.addEventListener('DOMContentLoaded', () => {
    // Seleciona todos os botões com a classe 'btn-editar' e itera sobre eles.
    document.querySelectorAll('.btn-editar').forEach(button => {
        // Adiciona um evento de clique a cada botão de edição.
        button.addEventListener('click', function() {
            // Encontra a linha (<tr>) mais próxima do botão clicado.
            const row = this.closest('tr');
            // Seleciona todos os elementos dentro da linha que possuem a classe 'editable'.
            row.querySelectorAll('.editable').forEach(div => {
                // Obtém o valor do atributo 'data-field' do elemento 'div'.
                const field = div.getAttribute('data-field');
                // Encontra o elemento <select> correspondente ao campo atual usando 'data-field'.
                const select = row.querySelector(`select[data-field="${field}"]`);
                if (select) {
                    // Exibe o elemento <select> e oculta o elemento <div> com o valor original.
                    select.style.display = 'block';
                    div.style.display = 'none';
                }
            });
            // Exibe os botões de salvar e cancelar na linha de edição.
            row.querySelector('.btn-save').style.display = 'block';
            row.querySelector('.btn-cancelar').style.display = 'block';
            // Oculta o botão de edição para evitar múltiplos cliques durante a edição.
            this.style.display = 'none';
        });
    });

    // Seleciona todos os botões com a classe 'btn-save' e adiciona um evento de clique a cada um.
    document.querySelectorAll('.btn-save').forEach(button => {
        button.addEventListener('click', function() {
            // Encontra a linha (<tr>) mais próxima do botão clicado.
            const row = this.closest('tr');
            const data = {}; // Objeto para armazenar os dados editados
            const originalData = {}; // Objeto para armazenar os valores originais dos dados

            // Coleta os dados dos campos de entrada e seleção na linha.
            row.querySelectorAll('select, input').forEach(element => {
                let value = element.value; // Valor atual do campo
                let originalValue = element.getAttribute('data-original-value');  // Capturando o valor original do atributo

                // Verifica e ajusta o valor dos campos numéricos.
                if (element.type === 'number') {
                    value = value.trim();
                    value = value === '' ? '0' : value; // Define 0 como valor padrão para campos vazios
                    if (!isNaN(value)) {
                        value = Number(value); // Converte o valor para número
                    } else {
                        value = '0';  // Define 0 para valores não numéricos inválidos
                    }
                }

                // Armazena o valor atual e o valor original no objeto correspondente.
                data[element.getAttribute('data-field')] = value;
                originalData[element.getAttribute('data-field')] = originalValue;  // Atribuindo o valor original
            });

            // Captura o valor de referência de data e define uma expressão regular para validar o formato ISO (YYYY-MM-DD).
            const dataReferencia = row.querySelector('select[data-field="data_referencia"]').value;
            const regexDataISO = /^\d{4}-\d{2}-\d{2}$/;

            // Verifica se a data está no formato ISO antes de enviar a requisição.
            if (regexDataISO.test(dataReferencia)) {
                console.log('Dados a serem enviados:', { data, originalData }); // Log para depuração dos dados enviados
                fetch(`/editar_receita/${encodeURIComponent(dataReferencia)}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken') // Inclui o token CSRF para proteção contra ataques CSRF
                    },
                    body: JSON.stringify({ data, originalData })  // Envia os dados e valores originais como JSON
                })
                .then(response => {
                    // Verifica se a resposta da requisição é bem-sucedida.
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    // Se a edição for bem-sucedida, recarrega a página para refletir as alterações.
                    if (data.status === 'success') {
                        window.location.reload();
                    } else {
                        console.error('Erro ao editar receita:', data.message);
                    }
                })
                .catch(error => console.error('Erro na requisição:', error));
            } else {
                console.error('Formato de data inválido:', dataReferencia); // Log de erro se a data não estiver no formato esperado
            }
        });
    });

    // Seleciona todos os botões com a classe 'btn-cancelar' e adiciona um evento de clique a cada um.
    document.querySelectorAll('.btn-cancelar').forEach(button => {
        button.addEventListener('click', function() {
            // Encontra a linha (<tr>) mais próxima do botão clicado.
            const row = this.closest('tr');

            // Oculta todos os elementos <select> e exibe os valores originais na linha.
            row.querySelectorAll('select').forEach(select => {
                const field = select.getAttribute('data-field');
                const div = row.querySelector(`div[data-field="${field}"]`);
                if (div) {
                    select.style.display = 'none';
                    div.style.display = 'block';
                }
            });

            // Oculta os botões de salvar e cancelar, e exibe novamente o botão de editar.
            row.querySelector('.btn-save').style.display = 'none';
            row.querySelector('.btn-cancelar').style.display = 'none';
            row.querySelector('.btn-editar').style.display = 'block';
        });
    });

    // Seleciona todos os botões com a classe 'btn-excluir-matriz-receita' e adiciona um evento de clique.
    document.querySelectorAll('.btn-excluir-matriz-receita').forEach(button => {
        button.addEventListener('click', async (event) => {
            event.preventDefault(); // Evita o comportamento padrão do clique.
            
            // Obtém o ID de referência e a linha (<tr>) associada ao botão.
            const dataReferencia = button.getAttribute('data-id');
            const row = button.closest('tr'); // Mudança aqui: usar closest('tr') é mais confiável
            
            // Verifica se a linha existe e loga um erro se não for encontrada.
            if (!row) {
                console.error(`Linha não encontrada para a data ${dataReferencia}`);
                return;
            }

            // Adicionando logs para debug
            console.log('Data Referência:', dataReferencia);
            console.log('Row encontrada:', row);

            // Coleta os dados atuais da linha para exclusão.
            const originalData = {
                data_referencia: dataReferencia,
                relatorio_xp: row.querySelector('[data-field="relatorio_xp"]')?.textContent.trim() || '',
                produto_categoria: row.querySelector('[data-field="produto_categoria"]')?.textContent.trim() || '',
                linha_de_receita: row.querySelector('[data-field="linha_de_receita"]')?.textContent.trim() || '',
                classe_do_ativo: row.querySelector('[data-field="classe_do_ativo"]')?.textContent.trim() || '',
                subclasse_do_ativo: row.querySelector('[data-field="subclasse_do_ativo"]')?.textContent.trim() || '',
                receita_comissoes: row.querySelector('[data-field="receita_comissoes"]')?.textContent.trim() || '',
                receita_ai: row.querySelector('[data-field="receita_ai"]')?.textContent.trim() || '',
                receita_escritorio: row.querySelector('[data-field="receita_escritorio"]')?.textContent.trim() || ''
            };

            // Log dos dados coletados
            console.log('Dados coletados para exclusão:', originalData); // Log para depuração.

            // Solicita confirmação do usuário antes de excluir.
            const confirmDelete = confirm('Tem certeza que deseja excluir esta receita da matriz?');
            
            if (confirmDelete) {
                try {
                    // Envia uma requisição POST para excluir a receita.
                    const response = await fetch(`/excluir-receita/${encodeURIComponent(dataReferencia)}/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken') // Adiciona o token CSRF para segurança
                        },
                        body: JSON.stringify({ originalData }) // Envia os dados para o servidor.
                    });
                    
                    // Exibe informações detalhadas da resposta para depuração.
                    console.log('Status da resposta:', response.status);
                    const responseData = await response.json();
                    console.log('Dados da resposta:', responseData);

                    // Se a resposta for bem-sucedida, remove a linha da tabela.
                    if (response.ok) {
                        if (responseData.status === 'success') {
                            alert('Receita excluída com sucesso!');
                            // Remove a linha diretamente ao invés de recarregar a página.
                            row.remove();
                        } else {
                            alert(`Erro ao excluir receita: ${responseData.message}`);
                        }
                    } else {
                        throw new Error(`${response.status}: ${responseData.message || 'Erro desconhecido'}`);
                    }
                } catch (error) {
                    console.error('Erro detalhado:', error);
                    alert(`Erro ao excluir receita: ${error.message}`);
                }
            }
        });
    });
});

// Aguarda até que o DOM esteja completamente carregado antes de executar o código.
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');

    // Seleciona os elementos necessários para a funcionalidade do modal de adicionar linha.
    const addLineModal = document.getElementById('addLineModal');
    const btnAdicionarLinha = document.getElementById('btnAdicionarLinha');
    const addLineForm = document.getElementById('addLineForm');
    const btnSalvarNova = document.getElementById('btnSalvarNova');

    // Verifica se todos os elementos necessários estão presentes; se algum estiver ausente, exibe um erro e encerra a execução.
    if (!addLineModal || !btnAdicionarLinha || !addLineForm || !btnSalvarNova) {
        console.error('One or more required elements are missing.');
        return;
    }

    // Inicializa o modal usando a biblioteca Bootstrap.
    const modal = new bootstrap.Modal(addLineModal);

    // Exibe o modal ao clicar no botão "Adicionar Linha".
    btnAdicionarLinha.addEventListener('click', function(event) {
        console.log('Add Line button clicked');
        event.preventDefault();
        modal.show();
    });

    // Função para sincronizar os campos de input e select, permitindo que o usuário adicione um valor ao input e o selecione no dropdown.
    function setupInputSelect(inputId, selectId) {
        const input = document.getElementById(inputId);
        const select = document.getElementById(selectId);
        
        // Exibe um erro no console se algum dos elementos estiver ausente.
        if (!input || !select) {
            console.error(`Missing elements for ${inputId} or ${selectId}`);
            return;
        }
        
        // Ao inserir um valor no campo de input, ele é adicionado como uma nova opção no select e automaticamente selecionado.
        input.addEventListener('input', function() {
            const newOption = document.createElement('option');
            newOption.value = this.value;
            newOption.text = this.value;
            select.insertBefore(newOption, select.firstChild);
            select.value = this.value;
        });

        // Sincroniza o campo de input com o valor selecionado no dropdown.
        select.addEventListener('change', function() {
            input.value = this.value;
        });
    }

    // Define os pares de input e select que serão sincronizados usando a função setupInputSelect.
    const fieldPairs = [
        ['novo_relatorio_xp_input', 'novo_relatorio_xp'],
        ['novo_produto_categoria_input', 'novo_produto_categoria'],
        ['nova_linha_de_receita_input', 'nova_linha_de_receita'],
        ['nova_classe_do_ativo_input', 'nova_classe_do_ativo'],
        ['nova_subclasse_do_ativo_input', 'nova_subclasse_do_ativo'],
        ['nova_receita_comissoes_input', 'nova_receita_comissoes']
    ];

    // Configura a sincronização para cada par de campos input e select.
    fieldPairs.forEach(pair => setupInputSelect(pair[0], pair[1]));

    // Manipulador de evento para o botão "Salvar Nova", que envia o formulário com os dados.
    btnSalvarNova.addEventListener('click', function() {
        console.log('Save button clicked');
        const formData = new FormData(addLineForm);

        // Atualiza o FormData com valores dos inputs, caso tenham sido preenchidos.
        fieldPairs.forEach(pair => {
            const inputValue = document.getElementById(pair[0]).value;
            if (inputValue) {
                formData.set(pair[1], inputValue);
            }
        });

        // Exibe no console os dados que serão enviados para depuração.
        for (let [key, value] of formData.entries()) {
            console.log(key, value);
        }

        // Envia os dados do formulário via fetch para a URL especificada.
        fetch('/adicionar_receita/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken') // Inclui o token CSRF no cabeçalho para segurança
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Response received:', data);
            if (data.status === 'success') {
                modal.hide();
                removeBackdrop();
                location.reload(); // Recarrega a página para refletir a nova linha adicionada.
            } else {
                alert('Erro ao adicionar linha: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Ocorreu um erro ao adicionar a linha.');
        });
    });

    // Função para obter o token CSRF a partir dos cookies do navegador.
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Função para remover o fundo (backdrop) do modal e redefinir o estilo da página quando o modal é ocultado.
    function removeBackdrop() {
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) {
            backdrop.remove();
        }
        document.body.classList.remove('modal-open');
        document.body.style.removeProperty('overflow');
        document.body.style.removeProperty('padding-right');
    }

    // Adiciona o evento para remover o backdrop quando o modal é fechado.
    addLineModal.addEventListener('hidden.bs.modal', removeBackdrop);

    // Adiciona eventos de fechamento ao modal para remover o backdrop e o estado modal da página.
    const closeButtons = addLineModal.querySelectorAll('[data-bs-dismiss="modal"]');
    closeButtons.forEach(button => {
        button.addEventListener('click', () => {
            modal.hide();
            removeBackdrop();
        });
    });
});
    
    // Submete o formulário de filtros ao detectar uma mudança no dropdown.
    function handleDropdownChange() {
        // Encontra o campo de pesquisa de texto
        const searchInput = document.querySelector('#filtroForm input[name="search"]');
    
        // Limpa o valor do campo de pesquisa
        searchInput.value = '';
    
        // Submete o formulário de filtros
        var form = document.getElementById('filtroForm');
        form.submit();
    }

    // Função para tratar mudanças nos filtros e enviar o formulário com os valores dos filtros.
    function handleFilterChange() {
        const periodoRepasse = document.querySelector('#filtro_periodo_repasse').value; // Captura o valor do filtro "Período Repasse"
        const opcoesPeriodoRepasse = document.querySelector('#opcoes_periodo_repasse').value; // Captura as opções "Opções Período Repasse"

        // Define o formulário e cria um objeto para armazenar os dados do filtro.
        const form = document.getElementById('filtroForm');
        const filterData = {};

        // Adiciona os filtros ao objeto 'filterData' se estiverem preenchidos.
        if (periodoRepasse) {
            filterData['filtro_periodo_repasse'] = periodoRepasse;
        }

        if (opcoesPeriodoRepasse) {
            filterData['opcoes_periodo_repasse'] = opcoesPeriodoRepasse;
        }

        // Para cada filtro em filterData, cria um input oculto no formulário com o valor correspondente.
        for (const key in filterData) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = key;
            input.value = filterData[key];
            form.appendChild(input);
        }

        // Submete o formulário para aplicar os filtros.
        form.submit();
    }

    // Adiciona ouvintes de evento para monitorar mudanças nos elementos de filtro e acionar 'handleFilterChange' quando ocorrerem.
    const filtroPeriodoRepasseElement = document.getElementById('filtro_periodo_repasse');
    const opcoesPeriodoRepasseElement = document.getElementById('opcoes_periodo_repasse');

    if (filtroPeriodoRepasseElement) {
        filtroPeriodoRepasseElement.addEventListener('change', handleFilterChange);
    }

    if (opcoesPeriodoRepasseElement) {
        opcoesPeriodoRepasseElement.addEventListener('change', handleFilterChange);
    }


    // Mantém a aba ativa selecionada ao recarregar a página, usando o armazenamento local (localStorage).
    document.addEventListener('DOMContentLoaded', function () {
        var activeTab = localStorage.getItem('activeTab') || 'matriz'; // Define 'matriz' como aba padrão
        var tab = document.querySelector('#myTab a[href="#' + activeTab + '"]');
        if (tab) {
            new bootstrap.Tab(tab).show(); // Exibe a aba armazenada como ativa.
        }
    });

    // Salva a aba ativa no armazenamento local sempre que o usuário clica em uma nova aba.
    document.querySelectorAll('#myTab a').forEach(function (tab) {
        tab.addEventListener('click', function (event) {
            localStorage.setItem('activeTab', event.target.getAttribute('href').substring(1));
        });
    });

    // Filtra os dados com base no valor do período selecionado no escritório e redireciona para a URL com o filtro aplicado.
    function filtrarPorPeriodoEscritorio(periodo) {
        var url = new URL(window.location.href); // Obtem a URL atual
        url.searchParams.set('filtro_periodo_escritorio', periodo); // Define ou atualiza o parâmetro de filtro
        window.location.href = url.toString(); // Redireciona para a URL modificada.
    }
    
    // Quando a página carrega, verifica se há um filtro de período no escritório na URL e seleciona a opção correspondente.
    document.addEventListener('DOMContentLoaded', function() {
        // Verificar se há um parâmetro de filtro na URL
        var urlParams = new URLSearchParams(window.location.search);
        var filtroPeriodo = urlParams.get('filtro_periodo_escritorio');
        
        if (filtroPeriodo) {
            // Se o filtro está na URL, define o valor no dropdown correspondente.
            var select = document.getElementById('filtro-periodo-escritorio');
            if (select) {
                select.value = filtroPeriodo;
            }
        }
    });

    // Ao carregar o DOM, configura o modal de exclusão de escritório com o ID do escritório selecionado.
    document.addEventListener('DOMContentLoaded', function () {
        $('#excluirEscritorioModal').on('show.bs.modal', function (event) {
            var button = $(event.relatedTarget); // Botão que abriu o modal.
            var escritorioId = button.data('id'); // Captura o ID do escritório do atributo 'data-*'.
            var modal = $(this);
            modal.find('#escritorio-id').val(escritorioId); // Define o ID no campo oculto dentro do modal.
        });
    });

    // Funções para editar e excluir escritórios na tabela de receitas.
    document.addEventListener('DOMContentLoaded', function () {
        const tableEscritorios = document.querySelector('.matriz-receitas-table');
        
        if (!tableEscritorios) return; // Previne erros se a tabela não existir.
        
        // Adiciona listener de evento para a tabela, capturando cliques nos botões de ação para cada escritório.
        tableEscritorios.addEventListener('click', function(e) {
            const target = e.target;
            const row = target.closest('tr'); // Linha correspondente ao escritório.
            
            // Verifica qual botão foi clicado e aciona a função apropriada.
            if (target.classList.contains('editar-btn-escritorio')) {
                toggleEditModeEscritorio(row, true); // Habilita o modo de edição.
            } else if (target.classList.contains('cancelar-btn-escritorio')) {
                toggleEditModeEscritorio(row, false, true); // Cancela a edição e restaura valores.
            } else if (target.classList.contains('salvar-btn-escritorio')) {
                salvarEdicaoEscritorio(row); // Salva a edição.
            } else if (target.classList.contains('excluir-btn-escritorio')) {
                excluirEscritorio(row); // Exclui o escritório.
            }
        });
        
        // Alterna entre os modos de visualização e edição de um escritório.
        function toggleEditModeEscritorio(row, isEditing, isCancelling = false) {
            const inputs = row.querySelectorAll('input'); // Seleciona todos os campos de entrada (input) na linha fornecida.
            const editarBtn = row.querySelector('.editar-btn-escritorio'); // Seleciona o botão de editar.
            const salvarBtn = row.querySelector('.salvar-btn-escritorio'); // Seleciona o botão de salvar.
            const cancelarBtn = row.querySelector('.cancelar-btn-escritorio'); // Seleciona o botão de cancelar.
            const excluirBtn = row.querySelector('.excluir-btn-escritorio'); // Seleciona o botão de excluir.
        
            if (isEditing) {
                // Ativa o modo de edição, permitindo alterações nos campos de input.
                inputs.forEach(input => {
                    input.dataset.originalValue = input.value; // Salva o valor original.
                    input.readOnly = false; // Torna o campo editável.
                });
                editarBtn.classList.add('d-none'); // Esconde o botão de editar.
                salvarBtn.classList.remove('d-none'); // Mostra o botão de salvar.
                cancelarBtn.classList.remove('d-none'); // Mostra o botão de cancelar.
                excluirBtn.classList.add('d-none'); // Esconde o botão de excluir.
            } else {
                // Desativa o modo de edição, restaurando valores originais caso o cancelamento seja solicitado.
                if (isCancelling) {
                    inputs.forEach(input => {
                        input.value = input.dataset.originalValue; // Restaura valor original.
                    });
                }
                inputs.forEach(input => input.readOnly = true); // Torna os campos somente leitura.
                editarBtn.classList.remove('d-none'); // Mostra o botão de editar.
                salvarBtn.classList.add('d-none'); // Esconde o botão de salvar.
                cancelarBtn.classList.add('d-none'); // Esconde o botão de cancelar.
                excluirBtn.classList.remove('d-none'); // Mostra o botão de excluir.
            }
        }
        
        // Envia a atualização dos dados do escritório ao servidor.
        function salvarEdicaoEscritorio(row) {
            const id = row.getAttribute('data-id'); // Obtém o ID do escritório a partir da linha.
            const codigo = row.querySelector('.codigo').value; // Obtém o código do escritório.
            const nome = row.querySelector('.nome').value; // Obtém o nome do escritório.
            let ir = row.querySelector('.ir').value.replace(',', '.'); // Obtém o valor do IR e substitui vírgula por ponto.
            const url = row.querySelector('.salvar-btn-escritorio').getAttribute('data-url'); // Obtém a URL para salvar os dados.

            // Obtém o período selecionado e formata a data
            const dataReferencia = document.getElementById('filtro-periodo-escritorio').value;
            const dataFormatada = formatarData(dataReferencia);

            // Atualiza a mensagem do modal com o período
            const mensagemModal = document.getElementById('confirmarReplicacaoMensagem');
            mensagemModal.textContent = `Deseja aplicar o valor de Impostos para todas as linhas do período ${dataFormatada}?`;
        
            // Exibe o modal de confirmação para replicação do valor
            $('#confirmarReplicacaoModal').modal('show');
            
            // Configura o evento de clique para confirmar a replicação
            document.getElementById('confirmar-replicacao').onclick = function() {
                enviarEdicaoEscritorio(codigo, nome, ir, url, true);  // Passa true para replicar
                $('#confirmarReplicacaoModal').modal('hide'); // Esconde o modal após confirmação.
            };
            
            // Configura o evento de clique para cancelar a replicação
            document.querySelector('#confirmarReplicacaoModal .btn-secondary').onclick = function() {
                enviarEdicaoEscritorio(codigo, nome, ir, url, false);  // Passa false para não replicar
            };
        }

        // Envia os dados atualizados do escritório ao servidor.
        function enviarEdicaoEscritorio(codigo, nome, ir, url, replicar) {
            const dataReferencia = document.getElementById('filtro-periodo-escritorio').value; // Captura o período selecionado
            fetch(url, {
                method: 'POST', // Método de requisição POST
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded', // Define o tipo de conteúdo da requisição
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value // Inclui o token CSRF para segurança
                },
                body: new URLSearchParams({
                    'codigo': codigo, // Dados do código do escritório
                    'nome': nome, // Dados do nome do escritório
                    'irpj': ir, // Dados do valor do IRPJ
                    'replicar': replicar,  // Envia a escolha do usuário sobre replicar
                    'data_referencia': dataReferencia  // Envia o período selecionado
                })
            })
            .then(response => response.json()) // Converte a resposta para JSON
            .then(data => {
                if (data.success) {
                    alert('Alterações salvas com sucesso!'); // Exibe mensagem de sucesso
                    location.reload(); // Recarrega a página para refletir as alterações
                } else {
                    alert('Erro ao salvar as alterações: ' + data.message); // Exibe mensagem de erro
                }
            })
            .catch(error => console.error('Erro:', error)); // Trata possíveis erros na requisição
        }

        // Função para formatar a data no formato "MMM/YYYY"
        function formatarData(data) {
            const [ano, mes] = data.split('-');
            const meses = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];
            return `${meses[parseInt(mes, 10) - 1]}/${ano}`;
        }
        
        // Função para excluir o escritório após confirmação do usuário.
        function excluirEscritorio(row) {
            if (!confirm('Tem certeza que deseja excluir este escritório?')) {
                return; // Se o usuário cancelar a confirmação, não faz nada.
            }
    
            const codigo = row.getAttribute('data-id'); // ID do escritório a ser excluído.
            const excluirBtn = row.querySelector('.excluir-btn-escritorio'); // Seleciona o botão de excluir.
            const url = excluirBtn.getAttribute('data-url'); // URL de exclusão.
            
            // Realiza a solicitação de exclusão via POST.
            fetch(url, {
                method: 'POST', // Método de requisição POST
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded', // Define o tipo de conteúdo da requisição
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value // Inclui o token CSRF para segurança
                },
                body: new URLSearchParams({
                    'codigo': codigo // Envia o ID do escritório a ser excluído
                })
            })
            .then(response => response.json()) // Converte a resposta para JSON
            .then(data => {
                if (data.success) {
                    row.remove(); // Remove a linha correspondente da tabela.
                    alert('Escritório excluído com sucesso!'); // Exibe mensagem de sucesso
                } else {
                    alert('Erro ao excluir o escritório: ' + data.message); // Exibe mensagem de erro
                }
            })
            .catch(error => {
                console.error('Erro:', error); // Trata possíveis erros na requisição
                alert('Erro ao excluir o escritório. Por favor, tente novamente.'); // Mensagem de erro ao usuário
            });
        }
    });

    // Funções para manipulação dos botões de edição, salvamento e exclusão de metas.
    document.addEventListener('DOMContentLoaded', function () {
        const metasTable = document.querySelector('.matriz-receitas-table');
        if (!metasTable) return; // Previne erros se a tabela não existir.

        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content'); // Token CSRF para proteger as requisições.
        const editarButtons = document.querySelectorAll('.editar-btn');
        const salvarButtons = document.querySelectorAll('.salvar-btn');
        const cancelarButtons = document.querySelectorAll('.cancelar-btn');
        const excluirButtons = document.querySelectorAll('.excluir-btn');
        
        // Configura o comportamento dos botões de edição.
        editarButtons.forEach(button => {
            button.addEventListener('click', function (e) {
                e.preventDefault();
                const row = button.closest('tr'); // Encontra a linha correspondente.
                
                // Permite edição nas colunas Meta ROA e Meta NPS.
                row.querySelector('.meta_roa').removeAttribute('readonly');
                row.querySelector('.meta_nps').removeAttribute('readonly');
    
                button.classList.add('d-none'); // Esconde o botão de Editar.
                row.querySelector('.salvar-btn').classList.remove('d-none'); // Mostra o botão de Salvar.
                row.querySelector('.cancelar-btn').classList.remove('d-none'); // Mostra o botão de Cancelar
            });
        });
        
        // Configura o comportamento dos botões de cancelamento.
        cancelarButtons.forEach(button => {
            button.addEventListener('click', function () {
                const row = button.closest('tr');
    
                // Retorna as colunas Meta ROA e Meta NPS para readonly.
                row.querySelector('.meta_roa').setAttribute('readonly', true);
                row.querySelector('.meta_nps').setAttribute('readonly', true);
    
                row.querySelector('.editar-btn').classList.remove('d-none'); // Mostra o botão de Editar.
                button.classList.add('d-none'); // Esconde o botão de Cancelar
                row.querySelector('.salvar-btn').classList.add('d-none'); // Esconde o botão de Salvar
            });
        });
        
        // Configura o comportamento dos botões de salvamento.
        salvarButtons.forEach(button => {
            button.addEventListener('click', function () {
                const row = button.closest('tr');
                const id = row.getAttribute('data-id'); // ID da meta.
                const inputs = row.querySelectorAll('input');
                const periodo = inputs[0].value; 
                const meta_roa = inputs[1].value.replace(',', '.');  // Converte vírgula em ponto.
                const meta_nps = inputs[2].value.replace(',', '.'); // Converte vírgula em ponto.

                // Converte vírgula em ponto.
                fetch(editarMetaUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrfToken
                    },
                    body: new URLSearchParams({
                        'id': id,
                        'periodo': periodo,
                        'meta_roa': meta_roa,
                        'meta_nps': meta_nps
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload(); // Recarrega a página para aplicar alterações.
                    } else {
                        alert('Erro ao salvar as alterações.');
                    }
                });
            });
        });
        
        // Recarrega a página para aplicar alterações.
        excluirButtons.forEach(button => {
            button.addEventListener('click', function () {
                const row = button.closest('tr');
                const id = row.getAttribute('data-id'); // Configura o comportamento dos botões de exclusão.

                // Confirmação do usuário antes de excluir.
                if (confirm('Tem certeza que deseja excluir esta meta?')) {
                    fetch(excluirMetaUrl, {  // Usando a variável com a URL correta
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-CSRFToken': '{{ csrf_token }}'
                        },
                        body: new URLSearchParams({
                            'id': id
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            row.remove(); // Confirmação do usuário antes de excluir.
                        } else {
                            alert('Erro ao excluir a meta.');
                        }
                    });
                }
            });
        });
    });

    // Funções para manipulação dos botões de edição, salvamento, cancelamento e exclusão de repasses contratuais.
    document.addEventListener('DOMContentLoaded', function () {
        const editarButtons = document.querySelectorAll('.btn-editar');
        const salvarButtons = document.querySelectorAll('.btn-save');
        const cancelarButtons = document.querySelectorAll('.btn-cancelar');
        const excluirButtons = document.querySelectorAll('.btn-excluir');

        // Configura o comportamento dos botões de edição.
        editarButtons.forEach(button => {
            button.addEventListener('click', function (e) {
                e.preventDefault();
                const row = button.closest('tr'); // Encontra a linha correspondente.

                // Esconde as divs com valores originais e exibe os campos para edição.
                row.querySelectorAll('.editable').forEach(div => div.style.display = 'none');
                row.querySelectorAll('.edit-mode').forEach(input => {
                    console.log("Valor original:", input.value); // Log para verificar o valor original
                    input.setAttribute('data-original-value', input.value); // Salva o valor original
                    input.style.display = 'block';
                    input.removeAttribute('readonly'); // Torna o campo editável
                });

                // Alterna a visibilidade dos botões.
                button.style.display = 'none';
                row.querySelector('.btn-save').style.display = 'inline-block';
                row.querySelector('.btn-cancelar').style.display = 'inline-block';
            });
        });

        // Configura o comportamento dos botões de cancelamento.
        cancelarButtons.forEach(button => {
            button.addEventListener('click', function (e) {
                e.preventDefault();
                const row = button.closest('tr');
        
                // Restaura todos os valores dos inputs de modo edição para os valores originais e os torna readonly
                row.querySelectorAll('.edit-mode').forEach(input => {
                    input.style.display = 'none';
                    input.value = input.getAttribute('data-original-value'); // Reverte para o valor original armazenado
                    input.setAttribute('readonly', 'true'); // Retorna o campo para readonly
                });
        
                // Especificamente para o campo "repasse bruto", exibe o valor original com formatação
                const repasseBrutoField = row.querySelector('.repasse-bruto');
                if (repasseBrutoField) {
                    repasseBrutoField.value = repasseBrutoField.getAttribute('data-original-value');
                    repasseBrutoField.style.display = 'block';
                    repasseBrutoField.setAttribute('readonly', 'true'); // Retorna o campo para readonly
                }
        
                // Restaura a exibição dos valores originais não editáveis
                row.querySelectorAll('.editable').forEach(div => div.style.display = 'block');
        
                // Alterna a visibilidade dos botões
                row.querySelector('.btn-editar').style.display = 'inline-block';
                button.style.display = 'none';
                row.querySelector('.btn-save').style.display = 'none';
            });
        });

        // Configura o comportamento dos botões de salvamento.
        salvarButtons.forEach(button => {
            button.addEventListener('click', function (e) {
                e.preventDefault();
                const row = button.closest('tr');

                // Extrai ID, data de referência e categoria do produto.
                const id = row.getAttribute('data-id').split('|'); // Divide o id em duas partes
                const data_referencia = id[0]; // A primeira parte é a data
                const produto_categoria_xp = id[1]; // A segunda parte é a categoria
        
                const inputs = row.querySelectorAll('.edit-mode');
        
                // Validação e formatação dos dados
                const repasse_bruto = parseFloat(inputs[1].value.replace(',', '.')) / 100; // Conversão e formatação para percentual.
        
                // Validações adicionais antes do envio.
                if (isNaN(repasse_bruto)) {
                    alert('Por favor, insira um valor numérico válido para Repasse Bruto.');
                    return;
                }
        
                // Verifica se a categoria do produto está vazia
                if (produto_categoria_xp.trim() === "") {
                    alert('Por favor, selecione uma categoria de produto.');
                    return;
                }
                
                // Coleta os dados restantes.
                const fee_fixo = parseInt(inputs[2].value);
                const fee_fixo_ex_rv = parseInt(inputs[3].value);
        
                // Cria o objeto de dados a ser enviado.
                const data = {
                    data_referencia: data_referencia,
                    produto_categoria_xp: produto_categoria_xp,
                    repasse_bruto: repasse_bruto.toFixed(5), // Arredonda para 5 casas decimais.
                    fee_fixo: fee_fixo,
                    fee_fixo_ex_rv: fee_fixo_ex_rv
                };
        
                // Envia os dados para o servidor para salvar as edições.
                fetch('/editar_repasse/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload(); // Recarrega a página se o salvamento for bem-sucedido.
                    } else {
                        alert('Erro ao salvar as alterações: ' + (data.error || 'Erro desconhecido'));
                    }
                })
                .catch(error => {
                    console.error('Erro:', error);
                    alert('Erro ao salvar as alterações. Verifique o console para mais detalhes.');
                });
            });
        });

        // Configura o comportamento dos botões de exclusão.
        excluirButtons.forEach(button => {
            button.addEventListener('click', function (e) {
                e.preventDefault();
                const row = button.closest('tr');
                const id = row.getAttribute('data-id');

                // Solicita confirmação antes de excluir.
                if (confirm('Tem certeza que deseja excluir este repasse?')) {
                    fetch('/excluir_repasse/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({ data_referencia: id })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            row.remove(); // Remove a linha da tabela em caso de sucesso.
                        } else {
                            alert('Erro ao excluir o repasse: ' + (data.error || 'Erro desconhecido'));
                        }
                    })
                    .catch(error => {
                        console.error('Erro:', error);
                        alert('Erro ao excluir o repasse. Verifique o console para mais detalhes.');
                    });
                }
            });
        });
    });

    // Função para obter o valor do cookie CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

// Função executada após o carregamento completo do DOM
document.addEventListener('DOMContentLoaded', function () {
    // Configura o botão de salvar repasse para enviar os dados do formulário
    document.getElementById('btnSalvarRepasse').addEventListener('click', function () {
        const form = document.getElementById('addRepasseForm'); // Obtém o formulário de cadastro
        
        // Captura os valores dos campos do formulário
        const novaDataReferencia = form.nova_data_referencia.value;
        const novoProdutoCategoriaXP = form.novo_produto_categoria_xp_input.value || form.novo_produto_categoria_xp.value;
        const novoRepasseBruto = form.novo_repasse_bruto.value;
        const novoFeeFixo = form.novo_fee_fixo.value;
        const novoFeeFixoExRV = form.novo_fee_fixo_ex_rv.value;

        // Valida se todos os campos obrigatórios estão preenchidos e o valor de repasse é numérico
        if (!novaDataReferencia || !novoProdutoCategoriaXP || !novoRepasseBruto || isNaN(novoRepasseBruto.replace(',', '.'))) {
            alert("Preencha todos os campos corretamente.");
            return; // Interrompe a execução se a validação falhar
        }

        // Envia os dados capturados para o servidor
        fetch('/cadastrar_repasse/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')  // Usa um token CSRF para proteção contra ataques CSRF
            },
            body: JSON.stringify({
                data_referencia: novaDataReferencia,
                produto_categoria_xp: novoProdutoCategoriaXP,
                repasse_bruto: parseFloat(novoRepasseBruto.replace(',', '.')).toFixed(5), // Formata o valor de repasse bruto com 5 casas decimais
                fee_fixo: novoFeeFixo,
                fee_fixo_ex_rv: novoFeeFixoExRV
            })
        })
        .then(response => response.json()) // Converte a resposta em JSON
        .then(data => {
            if (data.success) {
                location.reload();  // Recarrega a página se o salvamento for bem-sucedido
            } else {
                alert("Erro ao cadastrar repasse."); // Mostra um alerta em caso de erro
            }
        })
        .catch(error => console.error('Erro:', error)); // Loga o erro no console em caso de falha
    });
});