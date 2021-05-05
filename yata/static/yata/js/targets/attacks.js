// toggle target from attack list button
$(document).on('click', '.attack-list-target', function(e){
    e.preventDefault();
    var targetId = $(this).closest("tr").attr("data-tId");
    var attackId = $(this).closest("tr").attr("data-aId");
    var reload = $(".catch-buttons-attack-"+targetId);
    reload.load( "/target/attack/", {
        targetId: targetId,
        attackId: attackId,
        type: "toggle",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    reload.html('<i class="fas fa-spinner fa-pulse"></i>');
});

// toggle attacks from revives list button
$(document).on('click', '.attack-list-paid', function(e){
    e.preventDefault();
    var attackId = $(this).closest("tr").attr("data-aId");
    $(this).closest("td").load( "/target/attack/", {
        attackId: attackId,
        type: "paid",
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html('<i class="fas fa-spinner fa-pulse"></i>');
});

// pay losses
$(document).on('click', '.targets-attacks-losses-payall', function(e){
    e.preventDefault();
    $( "#attack-losses" ).load( "/target/attacks/losses/", {
        payall: $(this).attr("data-val"),
        csrfmiddlewaretoken: getCookie("csrftoken")
    })
});

// send losses
$(document).on('click', '#target-losses-send-all-cash', function(e){
    e.preventDefault();
    $("a.targets-attacks-losses-payall").each(function(index, element) {
        var tid = $(element).attr("data-val");
        var los = $(element).attr("data-los");
        if(!isNaN(parseInt(tid)) ) {
            window.open("https://www.torn.com/sendcash.php#/XID="+tid+"&losses="+los, "_blank");
        }
    });
});
