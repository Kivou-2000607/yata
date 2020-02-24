{% comment %}
Copyright 2020 kivou.2000607@gmail.com

This file is part of yata.

    yata is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    yata is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with yata. If not, see <https://www.gnu.org/licenses/>.
{% endcomment %}


<script>
$(document).ready(function() {
    $( "i.fas, i.far, i.fa" ).each( function( id1, el1 ){
      var classes = $(el1).attr("class").split(/\s+/);
      $.each(classes, function( id2, el2 ){
        if (el2 == "far") { $(el1).removeClass("far"); $(el1).addClass("fas"); }
        if (el2 == "fa") { $(el1).removeClass("fa"); $(el1).addClass("fas"); }
        if (el2.substring(0, 3) == "fa-") { $(el1).removeClass(el2); $(el1).addClass("fa-poo"); }
      });
    });
 });
</script>
