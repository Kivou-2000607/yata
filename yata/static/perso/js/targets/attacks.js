// toggle target from attack list button
$(document).on('click', '.attack-list-toggle', function(e){
    e.preventDefault();
    var targetId = $(this).closest("tr").attr("data-val");
    var reload = $(".catch-buttons-attack-"+targetId);
    reload.load( "/target/target/", {
        targetId: targetId,
        type: "toggle",
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
    });
    reload.html('<i class="fas fa-spinner fa-pulse"></i>');
});
