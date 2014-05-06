$(function() {

  var users = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    remote: {
      url: '../api/search/users?q=%QUERY',
      filter: function(response) {
        return $.map(response, function(user) {
          return { name: user.firstname + " " + user.lastname, username: user.username };
        });
      }
    }
  });

  var places = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    remote: {
      url: '../api/search/places?q=%QUERY',
      filter: function(response) {
        return $.map(response, function(place) {
          return { name: place.localname, slug: place.localname};
        });
      }
    }
  });

  users.initialize();
  places.initialize();

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
      suggestion: Handlebars.compile('<a href="/usuarios/{{username}}">{{name}} <span class="slug">({{username}})</span></a>')
    }
  },
  {
    name: 'places',
    displayKey: 'name',
    source: places.ttAdapter(),
    templates: {
      header: '<h3 class="section-name">Locales</h3>',
      suggestion: Handlebars.compile('<a href="/locales/{{slug}}">{{name}}</a>')
    }
  });

});