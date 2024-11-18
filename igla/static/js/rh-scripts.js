document.addEventListener('DOMContentLoaded', function() {
    // Script para manter a última aba ativa
    const urlParams = new URLSearchParams(window.location.search);
    const activeTab = urlParams.get('tab');

    if (activeTab) {
        document.querySelectorAll('.nav-link').forEach(tab => {
            tab.classList.remove('active');
        });

        document.querySelectorAll('.tab-pane').forEach(content => {
            content.classList.remove('show', 'active');
        });

        const activeTabElement = document.querySelector(`a[href="?tab=${activeTab}"]`);
        const activeTabContent = document.getElementById(activeTab);

        if (activeTabElement && activeTabContent) {
            activeTabElement.classList.add('active');
            activeTabContent.classList.add('show', 'active');
        }
    }

    //Editar Cargos e Departamentos
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('editar-btn')) {
            const row = event.target.closest('tr');
            row.querySelector('.departamento-value').classList.add('d-none');
            row.querySelector('.departamento-input').classList.remove('d-none');
            row.querySelector('.departamento-dropdown').classList.remove('d-none');  // Mostrar dropdown
            row.querySelector('.cargo-value').classList.add('d-none');
            row.querySelector('.cargo-input').classList.remove('d-none');
            row.querySelector('.cargo-dropdown').classList.remove('d-none');  // Mostrar dropdown
            row.querySelector('.editar-btn').classList.add('d-none');
            row.querySelector('.salvar-btn').classList.remove('d-none');
            row.querySelector('.cancelar-btn').classList.remove('d-none');
        }
    
        if (event.target.classList.contains('cancelar-btn')) {
            const row = event.target.closest('tr');
            row.querySelector('.departamento-value').classList.remove('d-none');
            row.querySelector('.departamento-input').classList.add('d-none');
            row.querySelector('.departamento-dropdown').classList.add('d-none');  // Ocultar dropdown
            row.querySelector('.cargo-value').classList.remove('d-none');
            row.querySelector('.cargo-input').classList.add('d-none');
            row.querySelector('.cargo-dropdown').classList.add('d-none');  // Ocultar dropdown
            row.querySelector('.editar-btn').classList.remove('d-none');
            row.querySelector('.salvar-btn').classList.add('d-none');
            row.querySelector('.cancelar-btn').classList.add('d-none');
        }
    
        if (event.target.classList.contains('salvar-btn')) {
            const row = event.target.closest('tr');
            const newDepartamentoInput = row.querySelector('.departamento-input').value;
            const newDepartamentoDropdown = row.querySelector('.departamento-dropdown').value;
            const newCargoInput = row.querySelector('.cargo-input').value;
            const newCargoDropdown = row.querySelector('.cargo-dropdown').value;
        
            // Prioriza o valor do dropdown se um valor for selecionado
            const newDepartamento = newDepartamentoDropdown || newDepartamentoInput;
            const newCargo = newCargoDropdown || newCargoInput;
        
            // Obtendo o identificador único
            const uniqueId = row.getAttribute('data-unique-id').split('|');
        
            fetch('/update_cargo/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    old_departamento: uniqueId[0],
                    new_departamento: newDepartamento,
                    old_cargo: uniqueId[1],
                    new_cargo: newCargo,
                    old_departamento_solides: uniqueId[2],
                    old_cargo_solides: uniqueId[3]
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Atualiza as células
                    row.querySelector('.departamento-value').textContent = newDepartamento;
                    row.querySelector('.cargo-value').textContent = newCargo;
                    row.setAttribute('data-departamento', newDepartamento);
                    row.setAttribute('data-cargo', newCargo);
                    row.querySelector('.departamento-value').classList.remove('d-none');
                    row.querySelector('.departamento-input').classList.add('d-none');
                    row.querySelector('.departamento-dropdown').classList.add('d-none');  // Ocultar dropdown
                    row.querySelector('.cargo-value').classList.remove('d-none');
                    row.querySelector('.cargo-input').classList.add('d-none');
                    row.querySelector('.cargo-dropdown').classList.add('d-none');  // Ocultar dropdown
                    row.querySelector('.editar-btn').classList.remove('d-none');
                    row.querySelector('.salvar-btn').classList.add('d-none');
                    row.querySelector('.cancelar-btn').classList.add('d-none');
                } else {
                    alert('Erro ao salvar as alterações.');
                }
            })
            .catch(error => {
                console.error('Erro ao salvar:', error);
            });
        }
    });

    // Editar senioridade
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('editar-btn')) {
            const row = event.target.closest('tr');
            row.querySelector('.senioridade-value').classList.add('d-none');
            row.querySelector('.senioridade-input').classList.remove('d-none');
            row.querySelector('.senioridade-dropdown').classList.remove('d-none');
            row.querySelector('.editar-btn').classList.add('d-none');
            row.querySelector('.salvar-btn').classList.remove('d-none');
            row.querySelector('.cancelar-btn').classList.remove('d-none');
        }

        if (event.target.classList.contains('cancelar-btn')) {
            const row = event.target.closest('tr');
            row.querySelector('.senioridade-value').classList.remove('d-none');
            row.querySelector('.senioridade-input').classList.add('d-none');
            row.querySelector('.senioridade-dropdown').classList.add('d-none');
            row.querySelector('.editar-btn').classList.remove('d-none');
            row.querySelector('.salvar-btn').classList.add('d-none');
            row.querySelector('.cancelar-btn').classList.add('d-none');
        }

        if (event.target.classList.contains('salvar-btn')) {
            const row = event.target.closest('tr');
            const newSenioridadeInput = row.querySelector('.senioridade-input').value;
            const newSenioridadeDropdown = row.querySelector('.senioridade-dropdown').value;

            // Prioriza o valor do dropdown se um valor for selecionado
            const newSenioridade = newSenioridadeDropdown || newSenioridadeInput;
            const cargo = row.getAttribute('data-cargo');
            const originalSenioridade = row.getAttribute('data-senioridade');

            // Atualizar somente o valor da célula, sem remover ou reposicionar a linha
            fetch('/editar_senioridade/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    cargo_solides: cargo,
                    old_senioridade: originalSenioridade,
                    new_senioridade: newSenioridade
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Atualiza a célula sem mover a linha
                    row.querySelector('.senioridade-value').textContent = newSenioridade;
                    row.setAttribute('data-senioridade', newSenioridade);
                    row.querySelector('.senioridade-value').classList.remove('d-none');
                    row.querySelector('.senioridade-input').classList.add('d-none');
                    row.querySelector('.senioridade-dropdown').classList.add('d-none');
                    row.querySelector('.editar-btn').classList.remove('d-none');
                    row.querySelector('.salvar-btn').classList.add('d-none');
                    row.querySelector('.cancelar-btn').classList.add('d-none');

                    // Certifique-se de que a linha não seja movida para o final
                } else {
                    alert('Erro ao salvar as alterações.');
                }
            })
            .catch(error => {
                console.error('Erro ao salvar:', error);
            });
        }
    });

    //Editar Squad
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('editar-btn')) {
            const row = event.target.closest('tr');
            row.querySelector('.squad-value').classList.add('d-none');
            row.querySelector('.squad-input').classList.remove('d-none');
            row.querySelector('.squad-dropdown').classList.remove('d-none');
            row.querySelector('.editar-btn').classList.add('d-none');
            row.querySelector('.salvar-btn').classList.remove('d-none');
            row.querySelector('.cancelar-btn').classList.remove('d-none');
        }
    
        if (event.target.classList.contains('cancelar-btn')) {
            const row = event.target.closest('tr');
            row.querySelector('.squad-value').classList.remove('d-none');
            row.querySelector('.squad-input').classList.add('d-none');
            row.querySelector('.squad-dropdown').classList.add('d-none');
            row.querySelector('.editar-btn').classList.remove('d-none');
            row.querySelector('.salvar-btn').classList.add('d-none');
            row.querySelector('.cancelar-btn').classList.add('d-none');
        }
    
        if (event.target.classList.contains('salvar-btn')) {
            const row = event.target.closest('tr');
            const newSquadInput = row.querySelector('.squad-input').value;
            const newSquadDropdown = row.querySelector('.squad-dropdown').value;
            
            // Prioriza o valor do dropdown se um valor for selecionado
            const newSquad = newSquadDropdown || newSquadInput;
            const unidade = row.getAttribute('data-unidade');
            const originalSquad = row.getAttribute('data-squad');
    
            fetch('/editar_squad/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    unidade_solides: unidade,
                    old_squad: originalSquad,
                    new_squad: newSquad
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Atualiza a célula sem mover a linha
                    row.querySelector('.squad-value').textContent = newSquad;
                    row.setAttribute('data-squad', newSquad);
                    row.querySelector('.squad-value').classList.remove('d-none');
                    row.querySelector('.squad-input').classList.add('d-none');
                    row.querySelector('.squad-dropdown').classList.add('d-none');
                    row.querySelector('.editar-btn').classList.remove('d-none');
                    row.querySelector('.salvar-btn').classList.add('d-none');
                    row.querySelector('.cancelar-btn').classList.add('d-none');
                } else {
                    alert('Erro ao salvar as alterações.');
                }
            })
            .catch(error => {
                console.error('Erro ao salvar:', error);
            });
        }
    });

    //Função de excluir nas 3 abas
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('excluir-btn')) {
            const row = event.target.closest('tr');
            let message = '';
            let fetchUrl = '';
            let bodyData = {};

            if (row.closest('#cargos')) { // Aba Cargos
                const [departamento, cargo, departamentoSolides, cargoSolides] = row.getAttribute('data-unique-id').split('|');
                message = `Tem certeza que deseja excluir o cargo ${cargoSolides} do departamento ${departamentoSolides}?`;
                fetchUrl = '/delete_cargo/';
                bodyData = {
                    old_departamento: departamento,
                    old_cargo: cargo,
                    old_departamento_solides: departamentoSolides,
                    old_cargo_solides: cargoSolides
                };
            } else if (row.closest('#senioridades')) { // Aba Senioridades
                const cargo = row.getAttribute('data-cargo');
                const senioridade = row.getAttribute('data-senioridade');
                message = `Tem certeza que deseja excluir a senioridade ${senioridade} para o cargo ${cargo}?`;
                fetchUrl = '/delete_senioridade/';
                bodyData = {
                    cargo_solides: cargo,
                    senioridade: senioridade
                };
            } else if (row.closest('#squads')) { // Aba Squads
                const unidade = row.getAttribute('data-unidade');
                const squad = row.getAttribute('data-squad');
                message = `Tem certeza que deseja excluir o squad ${squad} da unidade ${unidade}?`;
                fetchUrl = '/delete_squad/';
                bodyData = {
                    unidade_solides: unidade,
                    squad: squad
                };
            }

            // Confirmação antes de excluir
            if (confirm(message)) {
                fetch(fetchUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(bodyData)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Remove a linha da tabela
                        row.remove();
                    } else {
                        alert('Erro ao excluir.');
                    }
                })
                .catch(error => {
                    console.error('Erro ao excluir:', error);
                });
            }
        }
    });

    // Função para obter o CSRF token
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
});