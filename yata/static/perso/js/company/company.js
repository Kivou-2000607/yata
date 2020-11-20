$(document).ready(function () {
    const h = $($(location).attr('hash'));
    if (h.length) {
        toggle_h(h);
    }
});

// nav link
$(document).on('click', 'table.company-categories td', function (e) {
    e.preventDefault();
    var l = $(this).children("a").attr("href").split("/")[2];
    $("#content-update").load("/company/" + l + "/", {
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
    }, nav("/company/" + l + "/"));
    $("#content-update h2").html(spinner + '&nbsp;&nbsp;Loading')
    $("#content-update h2").addClass("grey");
    $("div.error").hide();
});

// select a company
$(document).on('change', '#company-select-form', e => {
    e.preventDefault();
    const reload = $("#company-details");
    console.log(reload)
    const company_id = $(e.currentTarget).children("select").val();
    reload.load("/company/browse/", {
        type: "company-details",
        company_id: company_id,
        csrfmiddlewaretoken: getCookie("csrftoken")
    });

    reload.children("div.module").html(spinner);
});

// show hide logs details
$(document).on('click', 'tr.company-logs > td:not(.dont-touch-me)', function(e){
    e.preventDefault();
    var timestamp = $(this).parent("tr").attr("data-val");
    $( "#company-employees-details" ).load( "/company/supervise/", {
        type: "show-details", timestamp: timestamp, csrfmiddlewaretoken: getCookie("csrftoken"),
    });
});
