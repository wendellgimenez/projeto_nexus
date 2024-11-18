function editarLinha(botao) {
    let linha = botao.closest('tr');
    let senioridade = linha.querySelector('.senioridade');
    let abrangencia = linha.querySelector('.abrangencia');
    let indicador = linha.querySelector('.indicador');
    let valorMeta = linha.querySelector('.valor_meta .valor-meta-input');

    // Armazenar os valores originais das 4 colunas
    linha.dataset.senioridadeOriginal = senioridade.textContent.trim();
    linha.dataset.abrangenciaOriginal = abrangencia.textContent.trim();
    linha.dataset.indicadorOriginal = indicador.textContent.trim();
    linha.dataset.valorMetaOriginal = valorMeta.value.trim();

    let valorSenioridade = senioridade.textContent.trim();
    let valorAbrangencia = abrangencia.textContent.trim();
    let valorIndicador = indicador.textContent.trim();
    let valorMetaAtual = valorMeta.value.trim();

    // Atualizar os campos da tabela com seletores para edição
    senioridade.innerHTML = `<select class="form-control">${senioridades.map(opt => `<option value="${opt}" ${opt === valorSenioridade ? 'selected' : ''}>${opt}</option>`).join('')}</select>`;
    abrangencia.innerHTML = `<select class="form-control">${abrangencias.map(opt => `<option value="${opt}" ${opt === valorAbrangencia ? 'selected' : ''}>${opt}</option>`).join('')}</select>`;
    indicador.innerHTML = `<select class="form-control">${indicadores.map(opt => `<option value="${opt}" ${opt === valorIndicador ? 'selected' : ''}>${opt}</option>`).join('')}</select>`;

    valorMeta.parentElement.innerHTML = `<input type="text" class="form-control valor-meta-input" value="${valorMetaAtual.replace('R$', '').trim()}">`;

    botao.textContent = "Salvar";
    botao.onclick = function () { salvarLinha(linha); };

    let botaoExcluir = linha.querySelector('.btn-danger');
    botaoExcluir.textContent = "Cancelar";
    botaoExcluir.classList.replace("btn-danger", "btn-secondary");
    botaoExcluir.onclick = function () { cancelarEdicao(linha, botao, botaoExcluir, valorSenioridade, valorAbrangencia, valorIndicador, valorMetaAtual); };
}

function cancelarEdicao(linha, botaoEditar, botaoCancelar, senioridadeOriginal, abrangenciaOriginal, indicadorOriginal, valorMetaOriginal) {
    // Restaurar os valores originais nas colunas editáveis
    linha.querySelector('.senioridade').textContent = senioridadeOriginal;
    linha.querySelector('.abrangencia').textContent = abrangenciaOriginal;
    linha.querySelector('.indicador').textContent = indicadorOriginal;

    // Restaurar o campo valor_meta com "R$" adicionado apenas uma vez
    let valorMetaFormatado = valorMetaOriginal.replace('R$', '').trim();  // Remove qualquer "R$" duplicado
    linha.querySelector('.valor_meta').innerHTML = `<input type="text" class="form-control valor-meta-input" value="R$ ${valorMetaFormatado.replace('.', ',')}" readonly>`;

    // Restaurar botões para "Editar" e "Excluir"
    botaoEditar.textContent = "Editar";
    botaoEditar.onclick = function () { editarLinha(botaoEditar); };
    
    botaoCancelar.textContent = "Excluir";
    botaoCancelar.classList.replace("btn-secondary", "btn-danger");
    botaoCancelar.onclick = function () { excluirLinha(linha.getAttribute('data-id')); };
}

function formatarValorBrasileiro(valor) {
    if (typeof valor === "string") {
        valor = parseFloat(valor.replace(/\./g, '').replace(',', '.'));
    }
    return 'R$ ' + valor.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function salvarLinha(linha) {
    let senioridade = linha.querySelector('.senioridade select').value;
    let abrangencia = linha.querySelector('.abrangencia select').value;
    let indicador = linha.querySelector('.indicador select').value;
    let valorMeta = linha.querySelector('.valor_meta .valor-meta-input').value.trim();

    // Remove "R$", separadores de milhar e ajusta o ponto decimal
    valorMeta = valorMeta.replace('R$', '').replace(/\./g, '').replace(',', '.').trim();

    // Confirma se o valor está no formato correto, removendo qualquer vírgula ou ponto indevido
    valorMeta = parseFloat(valorMeta);

    // Recupera os valores originais armazenados para cada coluna
    let senioridadeOriginal = linha.dataset.senioridadeOriginal;
    let abrangenciaOriginal = linha.dataset.abrangenciaOriginal;
    let indicadorOriginal = linha.dataset.indicadorOriginal;
    let valorMetaOriginal = linha.dataset.valorMetaOriginal.replace('R$', '').replace(/\./g, '').replace(',', '.').trim();

    // Envia a requisição ao backend
    fetch(atualizarMetaUrl, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken, 'Content-Type': 'application/json' },
        body: JSON.stringify({
            senioridade,
            abrangencia,
            indicador,
            valor_meta: valorMeta.toFixed(2),  // Garantir o formato correto
            senioridade_original: senioridadeOriginal, 
            abrangencia_original: abrangenciaOriginal, 
            indicador_original: indicadorOriginal, 
            valor_meta_original: valorMetaOriginal  
        })
    }).then(response => response.json())
    .then(data => {
        console.log("Resposta do backend:", data);
        if (data.status === "success") {
            // Atualizar a linha conforme necessário com formatação
            linha.querySelector('.senioridade').textContent = senioridade;
            linha.querySelector('.abrangencia').textContent = abrangencia;
            linha.querySelector('.indicador').textContent = indicador;

            // Aplicar formatação correta ao valor_meta
            let valorMetaFormatado = formatarValorBrasileiro(valorMeta);
            linha.querySelector('.valor_meta').innerHTML = `<input type="text" class="form-control valor-meta-input" value="${valorMetaFormatado}" readonly>`;

            // Restaurar botões
            let botaoEditar = linha.querySelector('.btn-edit');
            botaoEditar.textContent = "Editar";
            botaoEditar.onclick = function () { editarLinha(botaoEditar); };

            let botaoCancelar = linha.querySelector('.btn-secondary');
            botaoCancelar.textContent = "Excluir";
            botaoCancelar.classList.replace("btn-secondary", "btn-danger");
            botaoCancelar.onclick = function () { excluirLinha(linha.getAttribute('data-id')); };
        } else {
            console.error("Erro do backend:", data.message);
        }
    }).catch(error => console.error("Erro na requisição:", error));
}

function excluirLinha(chave) {
    if (confirm("Tem certeza que deseja excluir esta linha?")) {
        fetch("{% url 'excluir_meta' %}", {
            method: 'POST',
            headers: { 'X-CSRFToken': '{{ csrf_token }}', 'Content-Type': 'application/json' },
            body: JSON.stringify({ chave })
        }).then(response => response.json())
        .then(data => {
            if (data.success) {
                document.querySelector(`tr[data-id="${chave}"]`).remove();
            } else {
                alert("Erro ao excluir a linha.");
            }
        });
    }
}
