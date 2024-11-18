let lastValues = {};

async function fetchMarketData() {
    try {
        const response = await fetch('/api/market-data');
        const data = await response.json();

        const tickerContent = document.querySelector('#market-ticker .ticker-content');
        let allItems = '';
        
        for (const [key, value] of Object.entries(data)) {
            const { valor, variacao } = value;
            
            // Determina a cor baseada na variação percentual
            let colorClass = 'neutral';
            if (variacao > 0) {
                colorClass = 'up';
            } else if (variacao < 0) {
                colorClass = 'down';
            }

            // Formata a variação com sinal + para positivo
            const variacaoFormatada = variacao > 0 ? `+${variacao.toFixed(2)}` : `${variacao.toFixed(2)}`;
            
            // Cria o item com a variação percentual
            const item = `<span class="${colorClass}">${key.toUpperCase()}: $${valor.toFixed(2)} (${variacaoFormatada}%)</span>`;
            allItems += item;
        }

        tickerContent.innerHTML = allItems + allItems;

        // Atualiza animação
        tickerContent.classList.remove('show');
        void tickerContent.offsetWidth;
        tickerContent.classList.add('show');

    } catch (error) {
        console.error('Erro ao buscar dados de mercado:', error);
    }
}

// Atualiza os dados a cada 60 segundos
setInterval(fetchMarketData, 60000);
// Busca os dados imediatamente ao carregar a página
fetchMarketData();