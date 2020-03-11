// refresh member from member list by clicking on the row
$(document).on('click', 'tr.faction-member-refresh > td:not(.dont-touch-me)', function(e){
    e.preventDefault();
    var reload = $(this).closest("tr");
    var memberId = reload.attr("data-val");
    reload.load( "/faction/members/update/", {
        memberId: memberId,
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html('<td colspan="7" style="text-align: center;">'+spinner+'</td>');
});

// toggle member shareE
$(document).on('click', '.faction-member-shareE', e=>{
    e.preventDefault();
    var td = $(e.currentTarget.offsetParent);
    td.load( "/faction/members/toggle/", {
        type: "energy",
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});

// toggle member shareN
$(document).on('click', '.faction-member-shareN', e=>{
    e.preventDefault();
    var td = $(e.currentTarget.offsetParent);
    td.load( "/faction/members/toggle/", {
        type: "nerve",
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});


// refresh all members from member list by clicking on title refresh button
$(document).on('click', '#member-refresh', function(e){
    e.preventDefault();
    var i=0;
    $("#faction-members").find('tr.faction-member-refresh').each(function() {
        var reload = $(this);
        var memberId = reload.attr("data-val");
        var wait = 0;
        if(i) { wait = 1000; }
        (function(index) {
            setTimeout(function() {
                reload.load( "/faction/members/update/", {
                    memberId: memberId,
                    csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
                }).html('<td colspan="7" style="text-align: center;">'+spinner+'</td>');
            }, wait);
        })(i);
        i++;
    });
});
