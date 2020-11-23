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

// simu roles
$(document).on('change', '.company-employee-position-form', e => {
    e.preventDefault();
    // change tr values
    const employee = $(e.currentTarget).parents("tr");
    employee.attr("data-pos", $(e.currentTarget).val())

    // get all employees and positions
    employees_postion = {}
    $("#company-details-employees > tbody > tr").each(function(i, v) {
      employees_postion[$(v).attr("data-emp")] = $(v).attr("data-pos")
    });
    console.log(employees_postion);
    const reload = $("#company-reload-employees");
    reload.load("/company/supervise/", {
        type: "employees-simu",
        employees_postion_simu: JSON.stringify(employees_postion),
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    employee.html('<td colspan="11" style="text-align: center;">' + spinner + '</td>');
});

// reset simu
$(document).on("click", "#company-employees-reset", e => {
  e.preventDefault();
  const reload = $("#company-reload-employees")
  const divspinner = '<div style="text-align: center; height: '+reload.css("height")+';">'+spinner+'</div>'
  reload.load("/company/supervise/", {
      type: "employees-simu",
      csrfmiddlewaretoken: getCookie("csrftoken")
  }).html(divspinner);
});

// show hide simu
$(document).on("click", "#company-employees-show-simu", e => {
  e.preventDefault();
  $("#company-employees-simu").toggle()
});
