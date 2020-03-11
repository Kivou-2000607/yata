const spinner = '<i class="fas fa-spinner fa-pulse"></i>';

function fancyCountdown(time)
{   // From https://stackoverflow.com/a/11486026
    // days, hours, minutes and seconds
    var days = ~~(time / 86400);
    var hrs = ~~((time % 86400) / 3600);
    var mins = ~~((time % 3600) / 60);
    var secs = ~~time % 60;
    console.log(days, hrs, mins, secs);

    // Output like "1:01" or "4:03:59" or "123:03:59"
    var ret = "";

    if (days > 0) {
        ret += "" + days + " day" + (days != 1 ? "s " : " ");
    }

    ret += (hrs < 10 ? "0" : "")
    ret += "" + hrs + ":" + (mins < 10 ? "0" : "");
    ret += "" + mins + ":" + (secs < 10 ? "0" : "");
    ret += "" + secs;
    return ret;
}

function fancyTimeFormat(time)
{   // From https://stackoverflow.com/a/11486026
    // Hours, minutes and seconds
    var hrs = ~~(time / 3600);
    var mins = ~~((time % 3600) / 60);
    var secs = ~~time % 60;

    // Output like "1:01" or "4:03:59" or "123:03:59"
    var ret = "";

    if (hrs > 0) {
        ret += "" + hrs + ":" + (mins < 10 ? "0" : "");
    }

    ret += "" + mins + ":" + (secs < 10 ? "0" : "");
    ret += "" + secs;
    return ret;
}

const nav = (url) =>{
     window.history.pushState(null, document.title, url);
};

// const nav = (r,s,x,url) =>{
//     console.log(r);
//     console.log(s);
//     console.log(x);
//     console.log(url);
//     window.history.pushState(r, document.title, url);
// };

// parse cookie
const getCookie = (s)=>{
    let parse=RegExp(""+s+"[^;]+").exec(document.cookie);
    return decodeURIComponent(!!parse ? parse.toString().replace(/^[^=]+./,"") : "");
};
