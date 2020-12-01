// refresh timer target update
window.setInterval(function(){
    $(".update-timer").each(function() {
        const lvl = parseInt($.trim($(this).attr("data-lvl")));
        const loot = parseInt($.trim($(this).attr("data-lts")));
        const now = parseInt(Date.now() / 1000);
        const diff = Math.max(loot-now, 0);
        const lvlt = lvl > 1 ? 30 * (Math.pow(2, lvl - 2)) * 60 : 0;
        let cd = fancyTimeFormat(diff);
        let cl = "";

        // cl = diff < 60*30 ? "valid" : cl;
        cl = diff < 60*15 ? "warning" : cl;
        cl = diff < 15 ? "error" : cl;
        const prog = diff < lvlt ? ' <span class="flush-right">'+parseInt(100 * (lvlt - diff) / lvlt)+'%</span>' : ''
        const html = diff > 0 ? 'in <span class="'+cl+'">' +cd+'</span>'+prog : ''

        $(this).html(html);
    });
}, 1000);


// schedule an attack
$(document).on('change', 'select.loot-schedule-attack', e => {
    e.preventDefault();
    const schedule_timestamp = $(e.currentTarget).val();
    const npc_id = $(e.currentTarget).attr("data-val");
    $("#content-update").load("/loot/", {
        type: "npc-schedule",
        schedule_timestamp: schedule_timestamp,
        npc_id: npc_id,
        csrfmiddlewaretoken: getCookie("csrftoken")
    });

    $("h2.title").each(function(i, v) {
      const div = $(v).next("div.module");
      div.html('<div style="text-align: center; height: '+div.css("height")+';">'+spinner+'</div>');
    });
});

// vote
$(document).on('click', 'span.npc-scheduled-vote-click', e => {
    e.preventDefault();
    const schedule_timestamp = $(e.currentTarget).attr("data-ts");
    const npc_id = $(e.currentTarget).attr("data-npc");
    $(e.currentTarget).load("/loot/", {
        type: "npc-vote",
        schedule_timestamp: schedule_timestamp,
        npc_id: npc_id,
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);

});
