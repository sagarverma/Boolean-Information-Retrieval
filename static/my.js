
$(function() {
    //hang on event of form with id=myform
    $("#searchForm").submit(function(e) {

        //prevent Default functionality
        e.preventDefault();

        //get the action-url of the form
        var actionurl = e.currentTarget.action;

        //do your own request an handle the results
        $.ajax({
                url: "/search",
                type: 'post',
                dataType: 'json',
                data: $("#searchForm").serialize(),
                success: function(data) {
                    $('#nav').empty();
                    var arr = data['result']
                    //console.log(links)
                    var table = "<table id='searchResTable'><th>#</th><th>Results</th>";

                    $("#nav").append("<h2><i><b>Did you mean : </b>" + arr[0] + "</i></h2>\n");
                    for(var i=1;i<arr.length;i++){
                        table += "<tr><td>"+(i)+"</td><td>" + arr[i] + "</td></tr>";
                    }

                    $("#nav").append(table);
                }
        });

    });

});
