// templates/partials/modal_recibo_quitacao_script.js
// Abre a confirmação "Deseja imprimir Recibo de Quitação?" quando a página
// é carregada com os parâmetros ?recibo=<tipo>&recibo_ids=<ids> (após a baixa).

<script>
document.addEventListener('DOMContentLoaded', function() {
    const modalEl = document.getElementById('reciboQuitacaoModal');
    if (!modalEl) return;

    const params = new URLSearchParams(window.location.search);
    const tipo = params.get('recibo');
    const ids = params.get('recibo_ids');
    if (!tipo || !ids) return;

    const baseUrl = "{% url 'financeiro:recibo_quitacao' %}";
    const pdfUrl = baseUrl + '?tipo=' + encodeURIComponent(tipo) + '&ids=' + encodeURIComponent(ids);
    const qtd = ids.split(',').filter(Boolean).length;

    document.getElementById('reciboQuitacaoInfo').textContent =
        (tipo === 'conta' ? 'Conta a receber' : 'Mensalidade') + ' quitada(s): ' +
        qtd + ' título(s).';

    function limparParametros() {
        params.delete('recibo');
        params.delete('recibo_ids');
        const query = params.toString();
        history.replaceState({}, '', window.location.pathname + (query ? '?' + query : '') + window.location.hash);
    }

    document.getElementById('reciboQuitacaoSim').addEventListener('click', function() {
        limparParametros();
        $(modalEl).modal('hide');
        // Abre o PDF em nova aba do navegador (visualizador com imprimir/baixar)
        window.open(pdfUrl, '_blank', 'noopener');
    });

    document.getElementById('reciboQuitacaoNao').addEventListener('click', function() {
        limparParametros();
    });

    $(modalEl).modal('show');
});
</script>
