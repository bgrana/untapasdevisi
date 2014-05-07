$(function() {

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
      suggestion: Handlebars.compile('<a href="/usuarios/{{username}}">{{firstname}} {{lastname}} <span class="slug">({{username}})</span></a>')
    }
  },
  {
    name: 'locals',
    displayKey: 'name',
    source: locals.ttAdapter(),
    templates: {
      header: '<h3 class="section-name">Locales</h3>',
      suggestion: Handlebars.compile('<a href="/locales/{{localname}}">{{showname}}</a>')
    }
  });

});