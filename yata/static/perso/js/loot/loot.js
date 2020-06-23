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
