// refresh timer target update
window.setInterval(function(){
    $(".update-timer").each(function() {
        var timeRefresh = $.trim($(this).text());
        if ( timeRefresh.search(" s")!=-1 ) {
            var splitRefresh = timeRefresh.split(" ");
            var sRefresh = 0;
            if (splitRefresh.length == 2) {
                sRefresh = parseInt(splitRefresh[0]);
            } else if (splitRefresh.length == 4) {
                sRefresh = parseInt(splitRefresh[2]) + 60 * parseInt(splitRefresh[0]);
            } else if (splitRefresh.length == 6) {
                sRefresh = parseInt(splitRefresh[4]) + 60 * parseInt(splitRefresh[2]) + 3600 * parseInt(splitRefresh[0]);
            }

            sRefresh --;
            sRefresh = Math.max(sRefresh, 0)
            hRefresh = Math.floor(sRefresh / 3600);
            sRefresh = sRefresh % 3600;
            mRefresh = Math.floor(sRefresh / 60);
            sRefresh = sRefresh % 60;
            if (hRefresh) {
                spad = ("0"+sRefresh.toString()).slice(-2);
                $(this).html(hRefresh.toString()+" hrs "+mRefresh.toString()+" mins "+spad+" s");
            }
            else if (mRefresh) {
                spad = ("0"+sRefresh.toString()).slice(-2);
                $(this).html(mRefresh.toString()+" mins "+spad+" s");
            } else {
                $(this).html(sRefresh.toString()+" s");
            }
        } else {
            if (!tr.hasClass('old-refresh')) {
                tr.addClass('old-refresh');
            }
        }
    });
}, 1000);
