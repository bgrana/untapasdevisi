$(function() {

  var results = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    remote: {
      url: '../api/search/users?q=%QUERY',
      filter: function(response) {
        console.log(response)
        return $.map(response, function(user) {
          return { name: user.firstname + " " + user.lastname };
        });
      }
    }
  });

  results.initialize();

  $('#search-bar').typeahead({
    hint: true,
    highlight: true,
    minLength: 1
  },
  {
    name: 'results',
    displayKey: 'name',

    source: results.ttAdapter()
  });
});