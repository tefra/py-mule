Object.defineProperty(Object.prototype, "getResource", {
  value: function (type, code) {
    key = "".concat(type, '.', code);
    return key.split(".").reduce(function (o, x) {
      return (typeof o == "undefined" || o === null) ? o : o[x];
    }, this, type, code);
  }
});

//First, checks if it isn't implemented yet.
if (!String.prototype.format) {
  String.prototype.format = function () {
    var args = arguments;
    return this.replace(/{(\d+)}/g, function (match, number) {
      return typeof args[number] != 'undefined'
          ? args[number]
          : match
          ;
    });
  };
}

function parse_response(obj) {
  resourceId = obj.resourceId
  provider = ''
  for (var i = 0; i < obj.data.length; i++) {
    id = obj.data[i].id
    provider = obj.data[i].provider['name']
    presentationName = obj.data[i].provider['presentationName']
    message = "";
    var legs = obj.data[i].legs
    var resources = obj.data[i].resources
    for (var j = 0; j < legs.length; j++) {
      var segments = legs[j].segments
      for (var x = 0; x < segments.length; x++) {
        seg = segments[x]

        dep = seg.route.departure.location
        arr = seg.route.arrival.location

        dep = resources.getResource('locations', seg.route.departure.location);
        dep = dep != null ? "{0} ({1}, {2})".format(dep.name, dep.city,
            dep.country) : seg.route.departure.location;
        arr = resources.getResource('locations', seg.route.arrival.location);
        arr = arr != null ? "{0} ({1}, {2})".format(arr.name, arr.city,
            arr.country) : seg.route.arrival.location;

        number = seg.transport.number
        airline = seg.transport.carriers.marketing
        message += airline + number + " - " + dep + " > " + arr + " <small>"
            + seg.route.departure.datetime + "</small><br />"
      }
    }
    price = obj.data[i].passengers.adults.price.total
    currency = obj.data[i].passengers.adults.price.currency
    formattedPrice = price + currency
    redirectUri = "api/v1/redirect?resourceId=" + resourceId + "&id=" + id
        + "&provider=" + provider

    $("#trips").append(
        "<div class=\"col-4\"<h3>" + message
        + "<small class=\"text-muted\">"
        + "<a href=" + redirectUri + ">" + formattedPrice + "</a>"
        + " | " + presentationName
        + "</small></h3><hr /></div>"
    );
  }

  if (obj.data.length > 0) {
    var classes = [
      'primary', 'secondary', 'success', 'danger',
      'warning', 'info', 'dark'
    ];
    var randomNumber = Math.floor(Math.random() * classes.length);

    var providerBadge = $('#provider-tpl')
    .text()
    .replace('@provider', presentationName)
    .replace('@random', classes[randomNumber])
    .replace('@total', obj.data.length);
    $('#providers').append(providerBadge);
  }
}

function search(id) {
    var source = new EventSource("search/async?id=" + id);
    source.addEventListener('message', function (event) {
        console.log(event);
        var obj = jQuery.parseJSON(event.data);
        parse_response(obj)
    });

    source.addEventListener('stop', function (event) {
        source.close();
        console.log(event);
    });

    source.addEventListener('error', function (event) {
        source.close();

        console.log(event);
    });

    source.onopen = function (event) {
        console.log(event);
    }
    console.log(source);
}

$("#search").click(function (e) {
    $("#trips").html('');
    $('#providers').html('');
    $('#errors').html('').hide()
    var form = $('#search-form');
    $.ajax({
        type: "POST",
        url: form.attr('action'),
        data: JSON.stringify(form.serializeJSON({
            parseAll: true, useIntKeysAsArrayIndex: true
        })),
        success: function (id) {
            search(id)
        },
        error: function (xhr, testStatus, error) {
            $('#errors').html(xhr.responseText).show()
        }
    });
    e.preventDefault();
});

$("#add-itinerary").click(function () {
  var itins = $('.itinerary-row');
  var html = $('#itinerary-tpl').text();
  var regexIndex = new RegExp('index', 'g');
  html = html.replace(regexIndex, itins.length);
  $('#itineraries').append(html);
  $('.datepicker').datepicker({
    format: "yyyy-mm-ddT00:00:00"
  });

  return false;
});

function removeItin(index) {
  $('#itinerary-row-' + index).remove();
}

$(document).ready(function () {
  $('.datepicker').datepicker({
    format: "yyyy-mm-ddT00:00:00"
  });
});