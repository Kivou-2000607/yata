// refresh timer target update
window.setInterval(function(){
    $(".update-timer").each(function() {

        // level of the timer (loop of 1, 2, 3, 4, 5)
        const lvl = parseInt($.trim($(this).attr("data-lvl")));

        // timestamp for reaching lvl
        const loot = parseInt($.trim($(this).attr("data-lts")));

        // current timestamp
        const now = parseInt(Date.now() / 1000);

        // time to reach lvl
        const diff = Math.max(loot-now, 0);

        // theoretical time left to reach lvl from previous lvl (30 minutes for lvl 1 since it's not known)
        const lvlt = 30 * (Math.pow(2, Math.max(lvl - 2, 0))) * 60;
        let cd = fancyTimeFormat(diff);
        let cl = "";

        // cl = diff < 60*30 ? "valid" : cl;
        cl = diff < 60*15 ? "orange" : cl;
        cl = diff < 15 ? "red" : cl;
        const p = parseInt(100 * (lvlt - diff) / lvlt)
        // const p = 100


        if(diff < lvlt) {
          const html = '<div class="progress" style="height: 17px;"><div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" aria-valuenow="' + p + '" aria-valuemin="0" aria-valuemax="100" style="width: '+ p +'%">' + cd + '</div></div>'
          $(this).html(html);
        } else {
          $(this).html(cd);
        }

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
