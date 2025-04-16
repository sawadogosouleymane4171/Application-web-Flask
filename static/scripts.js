// Exemple : Afficher une alerte lorsque l'utilisateur clique sur un bouton
$(document).ready(function () {
    // Exemple d'interaction : bouton de calcul
    $(".btn-calculate").on("click", function () {
        alert("Vous allez effectuer un calcul !");
    });

    // Exemple : Animation pour les alertes
    $(".alert").fadeTo(3000, 500).slideUp(500, function () {
        $(this).remove();
    });

    // Exemple : Confirmation avant déconnexion
    $(".btn-logout").on("click", function (e) {
        if (!confirm("Êtes-vous sûr de vouloir vous déconnecter ?")) {
            e.preventDefault();
        }
    });
});
