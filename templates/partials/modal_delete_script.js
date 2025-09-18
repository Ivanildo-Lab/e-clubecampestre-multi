// templates/partials/modal_delete_script.js

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Pega todos os botões com a classe 'js-delete-btn'
    const deleteButtons = document.querySelectorAll('.js-delete-btn');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();

            // Pega a URL e o nome do item dos atributos 'data-*' do botão
            const deleteUrl = this.dataset.url;
            const itemName = this.dataset.nome;

            // Pega os elementos do modal
            const deleteForm = document.getElementById('deleteForm');
            const itemNameModal = document.getElementById('itemNameModal');

            // Atualiza o formulário do modal com os dados corretos
            deleteForm.action = deleteUrl;
            itemNameModal.textContent = `"${itemName}"`;

            // Exibe o modal
            $('#deleteModal').modal('show');
        });
    });
});
</script>