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

    // Supprimez le bouton "Se déconnecter" sur la page unifac_method
    if (window.location.pathname === "/unifac_method") {
        $(".btn-logout").remove();
    }

    // Ajoutez une animation pour les boutons sur mobile
    $(".btn").on("touchstart", function () {
        $(this).addClass("btn-active");
    }).on("touchend", function () {
        $(this).removeClass("btn-active");
    });
});
