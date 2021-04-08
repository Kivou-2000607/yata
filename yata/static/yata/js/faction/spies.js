// create database
$(document).on('click', '#spy-database-create', e=>{
    e.preventDefault();
    $( "#content-update" ).load( "/faction/spies/", {
        action: "create-database",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $("#content-update h2").addClass("grey").html(spinner + '&nbsp;&nbsp;Creating database ');
});

// view database
$(document).on('click', '.spy-database-view', e=>{
    e.preventDefault();
    $( "#content-update" ).load( "/faction/spies/", {
        action: "view-database", pk: $(e.currentTarget).attr("data-val"),
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $("#content-update h2").addClass("grey").html(spinner + '&nbsp;&nbsp;Creating database ');
});

// delete database
$(document).on('click', '.spy-database-delete', e=>{
    e.preventDefault();
    $(e.currentTarget).closest("tr").load( "/faction/spies/", {
        action:"delete-database", pk: $(e.currentTarget).attr("data-val"),
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).remove();
});

// change secret
$(document).on('click', '.spy-database-secret', e=>{
  e.preventDefault();
  var td = $(e.currentTarget).parents("tr");
  td.load( "/faction/spies/", {
    action: "change-secret", pk: $(e.currentTarget).attr("data-val"),
    csrfmiddlewaretoken: getCookie("csrftoken")
  }).html('<td colspan="7" style="text-align: center;">' + spinner + '</td>');

});

// change name
$(document).on('click', '.spy-database-name', e=>{
  e.preventDefault();
  var tr = $(e.currentTarget).parents("tr");
  tr.load( "/faction/spies/", {
    action: "change-name", pk: $(e.currentTarget).attr("data-val"),
    csrfmiddlewaretoken: getCookie("csrftoken")
  }).html('<td colspan="7" style="text-align: center;">' + spinner + '</td>');
});

// export database
$(document).on('click', '.spy-database-export', e=>{
  e.preventDefault();
  $(this).load( "/faction/spies/", {
    action: "export-database", pk: $(e.currentTarget).attr("data-val"),
    csrfmiddlewaretoken: getCookie("csrftoken")
  });
});

// update database
$(document).on('click', '.spy-database-update', e=>{
  e.preventDefault();
  $( "#content-update" ).load( "/faction/spies/", {
    action: "update-database", pk: $(e.currentTarget).attr("data-val"),
    csrfmiddlewaretoken: getCookie("csrftoken")
  });
  $("#content-update h2").addClass("grey").html(spinner + '&nbsp;&nbsp;Creating database ');
});

// kick faction
$(document).on('click', '.spy-database-join-kick', e=>{
  e.preventDefault();
  $(e.currentTarget).load( "/faction/spies/", {
    action: "kick-faction", pk: $(e.currentTarget).attr("data-val"),
    faction_id: $(e.currentTarget).attr("data-fac"),
    csrfmiddlewaretoken: getCookie("csrftoken")
  }).remove();
});

// leave database
$(document).on('click', '.spy-database-leave', e=>{
    e.preventDefault();
    $(e.currentTarget).closest("tr").load( "/faction/spies/", {
        action:"leave-database", pk: $(e.currentTarget).attr("data-val"),
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).remove();
});

// join database
$(document).on('focusout', '.spy-database-join', e=>{
  e.preventDefault();
  var secret = $(e.currentTarget).val();
  if(secret.length==16) {
    $( "#content-update" ).load( "/faction/spies/", {
      action: "join-database", secret: secret,
      csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $("#content-update h2").addClass("grey").html(spinner + '&nbsp;&nbsp;Joining database ');
  };
});

// import spies
$(document).on('change', '.spy-database-import', e=>{
  e.preventDefault();
  var file_name = $(e.currentTarget).val().split("\\").slice(-1)[0]
  $('#spy-database-submit-' + $(e.currentTarget).attr("data-val")).attr("value", "Import " + file_name).attr("title", "Click to import " + file_name).show().addClass("valid");

});

// refresh spy extra info from list by clicking on the row
$(document).on('click', '.spy-list-refresh', e=>{
    e.preventDefault();
    $(e.currentTarget).load( "/faction/spies/", {
        target_id: $(e.currentTarget).attr("data-tid"),
        pk: $(e.currentTarget).attr("data-val"),
        action: "refresh-target-data",
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html('<td colspan="8" style="text-align: center;">' + spinner + '</td>');
});
