// Submit post on submit
$('#searchbar').on('submit', function(event){
    event.preventDefault();
    console.log("searchbar submitted!")  // sanity check
    create_post();
    //var CSRF_TOKEN = "{{ csrf_token }}";
});

