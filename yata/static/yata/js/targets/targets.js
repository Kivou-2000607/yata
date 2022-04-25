// refresh target from target list by clicking on the row
$(document).on("click", "tr[id^='target-list-refresh-'] > td:not(.dont-touch-me)", (e) => {
    e.preventDefault();
    const reload = $(e.target).closest("tr");
    // const targetId = reload.attr("id").split("-").pop();
    reload.removeClass("old-refresh");
    reload.load("/target/target/", {
        targetId: reload.attr("data-val"),
        type: "update",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    reload.html(`<td colspan="15" class="text-center">${spinner}</td>`);
});

// toggle faction target
$(document).on("click", "a.target-list-faction", (e) => {
    e.preventDefault();
    const reload = $(e.target).closest("td");
    reload.load("/faction/target/", {
        targetId: e.currentTarget.getAttribute("id").split("-").pop(),
        type: "toggle",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    reload.html(spinner);
});

// delete target from target list button
$(document).on("click", "a.target-list-delete", (e) => {
    e.preventDefault();

    // if (confirm("Are you sure you want to delete your list?")) {
      const targetId = e.currentTarget.getAttribute("id").split("-").pop();
      const reload = $(`#target-list-refresh-${targetId}`);
      reload.load("/target/target/", {
          targetId, type: "delete",
          csrfmiddlewaretoken: getCookie("csrftoken")
      });
      reload.remove();
    // }
});

// edit note
$(document).on("focusout", "input.target-list-note", (e) => {
    e.preventDefault();
    const targetId = $(e.target).next("input").attr("value");
    const note = $(e.target).val();
    const reload = $(e.target).closest("td");
    // alert(targetId+notes)
    reload.load("/target/target/", {
        targetId, note, type: "note",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    reload.html("<i class='fas fa-spinner fa-pulse p-1'></i>");
});

// change color
$(document).on("click", "span.target-list-note-color", (e) => {
    e.preventDefault();
    const reload = $(e.currentTarget).closest("td");
    reload.load("/target/target/", {
        targetId: e.currentTarget.dataset.val,
        type: "note-color",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    reload.html("<i class='fas fa-spinner fa-pulse p-1'></i>");
});

// refresh all targets from target list by clicking on title refresh button
$(document).on("click", "#target-refresh", (e) => {
    e.preventDefault();
    let i = 1;
    // get refresh color
    const refresh_color = parseInt(e.target.dataset.val);
    const refresh_colors = [];
    $("i[id^='target-list-refresh-color-']").each((i, e) => {
        if ($(e).hasClass("fa-check-square")) refresh_colors.push(e.dataset.val);
    });
    $("#target-targets").find("tr[id^='target-list-refresh-']").each((useless, e) => {
        // if ((!refresh_color || $(this).find("span.target-color-" + refresh_color).length) && $(this).attr("data-ref") == "1") {
        if (refresh_colors.includes($(e).find("span.target-list-note-color").attr("data-col")) && +e.dataset.ref === 1) {
          const reload = $(e);
          const targetId = reload.attr("id").split("-").pop();
          const wait = i * 500 + parseInt(i / 10) * 3000;
          ((index) => {
              setTimeout(() => {
                  reload.load("/target/target/", {
                      targetId, type: "update",
                      csrfmiddlewaretoken: getCookie("csrftoken")
                  });
                  reload.removeClass("old-refresh");
                  reload.html("<td colspan='15' class='text-center'><i class='fas fa-spinner fa-pulse p-1'></i></td>");
               }, wait);
          })(i);
          i++;
       }
    });
});

// change refresh color
$(document).on("click", "#target-list-refresh-color", (e) => {
    e.preventDefault();
    // get the current color & remove color class
    let color = +e.currentTarget.dataset.val;
    $(e.currentTarget).removeClass(`target-color-${color}`);

    // set the new color (class and data-val)
    color = (color + 1) % 4;
    $(e.currentTarget).addClass(`target-color-${color}`);
	e.currentTarget.dataset.val = color;

    // change refresh link (text and data-val)
    const colors = ["all", "green", "orange", "red"];
    $("#target-refresh").html(`<i class="fas fa-sync-alt"></i>&nbsp;Refresh ${colors[color]}`);
    $("#target-refresh").attr("data-val", color);

    // hide the other colors
    $(".target-list-note-color").each((i, el) => {
      const tr = $(el).parents("tr");
      if (colors[color] !== "all" && +el.dataset.col !== color && color !== undefined && color !== null) tr.hide();
      else tr.show();
    });

    // change select checkbox
    $("i[id^='target-list-refresh-color-']").removeClass("fa-check-square").addClass("fa-square");
    $(`#target-list-refresh-color-${color}`).removeClass("fa-square").addClass("fa-check-square");
    console.log($(`#target-list-refresh-color-${color}`));
});

// // change hover ticks
// $(document).on('mouseenter mouseleave', 'i[id^=target-list-refresh-color-]', function (e) {
//     if ($(this).hasClass("fa-square")) {
//         $(this).removeClass("fa-square").addClass("fa-check-square")
//     } else {
//         $(this).removeClass("fa-check-square").addClass("fa-square")
//     }
// }, function (e) {
//     if ($(this).hasClass("fa-square")) {
//         $(this).removeClass("fa-square").addClass("fa-check-square")
//     } else {
//         $(this).removeClass("fa-check-square").addClass("fa-square")
//     }
// });

// select color
$(document).on("click", "i[id^='target-list-refresh-color-']", (e) => {
    const color = e.target.dataset.val;
    if ($(e.target).hasClass("fa-square")) {
        // add this color
        $(e.target).removeClass("fa-square").addClass("fa-check-square");
        $(".target-list-note-color").each((i, el) => {
            if (el.dataset.col === color) $(el).parents("tr").show();
        });
    } else {
        // remove this color
        $(e.target).removeClass("fa-check-square").addClass("fa-square");
        $(".target-list-note-color").each((i, el) => {
            if (el.dataset.col === color) $(el).parents("tr").hide();
        });
    }
});

// add target manually
$(document).on("click", "#target-add-submit", (e) => {
    e.preventDefault();
    const id = $("#target-add-id").val();
    $("#content-update").load("/target/target/", {
        targetId: id, type: "addById",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $("#content-update h2").addClass("grey");
    $("#content-update h2").html(`${spinner}&nbsp;&nbsp;Adding target id ${id} (1 API call)`);
});

// refresh timer target update
window.setInterval(() => {
    $(".update-timer").each((i, e) => {
        const tr = $(e).closest("tr");
        const status = tr.find(".status");
        tr.attr("data-ref", 1);

        const tsRefresh = parseInt($.trim($(e).attr("data-val")));
        const tsStatus = parseInt($.trim(status.attr("data-val")));
        const tsNow = Date.now() / 1000;

        // transform notations if > 2 hours
        if (tsNow - tsRefresh > 7200) {
            $(e).html("> 2 hrs");
            tr.addClass("old-refresh");
            $(e).removeClass("need-refresh");
            status.removeClass("need-refresh");
        } else {
            // add/remove flash if tsStatus < tsRefresh
            if (tsStatus && tsRefresh) {
				let statusStr;
                if (tsStatus < tsNow) {
                    statusStr = `Out for ${fancyTimeFormat(tsNow - tsStatus)} s`;
                    status.addClass("need-refresh");
                    $(e).addClass("need-refresh");
                } else {
                    status.removeClass("need-refresh");
                    $(e).removeClass("need-refresh");
                    statusStr = status.text().substring(0, 6);
                    statusStr += fancyTimeFormat(tsStatus - tsNow);
                    tr.attr("data-ref", 0);
                }
                // update hosp time
                status.html(statusStr);
            }
            $(e).html(fancyTimeFormat(tsNow - tsRefresh));
        }
    });
}, 1000);
