$(function() {

  var URL = '127.0.0.1:5000'

  var users = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('username'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    remote: {
      url: '../api/search/users?q=%QUERY'
    }
  });

  var locals = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    remote: {
      url: '../api/search/locals?q=%QUERY'
    }
  });

  users.initialize();
  locals.initialize();

  $('#search-bar').typeahead({
    hint: true,
    highlight: true,
    minLength: 1
  },
  {
    name: 'users',
    displayKey: 'name',
    source: users.ttAdapter(),
    templates: {
      header: '<h3 class="section-name">Personas</h3>',
      suggestion: Handlebars.compile('{{firstname}} {{lastname}} <span class="slug">({{username}})</span></a>')
    }
  },
  {
    name: 'locals',
    displayKey: 'name',
    source: locals.ttAdapter(),
    templates: {
      header: '<h3 class="section-name">Locales</h3>',
      suggestion: Handlebars.compile('{{name}}')
    }
  });

  $('#search-bar').on('typeahead:selected', function(event, suggestion, dataset) {
      if (dataset == 'users') {
          window.location.replace('/usuarios/' + suggestion.username)
      } else {
          window.location.replace('/locales/' + suggestion.slug)
      }
  })

  // subtmit on enter
  $('#search-bar').keypress(function (e) {
      if (e.which == 13) {
          $('#search').submit();
      }
  });


  $('#search-local').typeahead({
    hint: true,
    highlight: true,
    minLength: 1
  },
  {
    name: 'locals',
    displayKey: 'name',
    source: locals.ttAdapter(),
    templates: {
      header: '<h3 class="section-name">Locales</h3>',
      suggestion: Handlebars.compile('{{name}}')
    }
  });

  $("img#chooser").click(function(){
    $("#image").trigger("click");
  });
});

function show_score(score) {
  $("#rating").text(score);
}

function vote(score) {
  $("#points").attr("value", score);
  $("#submit_vote").click();
}