 // Initialise mobile menu trigger
 $(document).ready(function(){
    $('.sidenav').sidenav();
  });

$(function() {

    // Setup Pred Array and Index value to increment
    var predarray = [];
    var predindex = 0;

    // Add selected teams to array if array is empty
    $('.team').on('click', function(event){
        event.stopPropagation();
        if (predarray.length == 0){
              // Add logic
              $(this).toggleClass('chosenwinner');
              predarray[predindex] = {};
              predarray[predindex]['pred_game'] = $(this).parent().parent().attr('id');
              predarray[predindex]['pred_winner'] = $(this).attr('id');
              predindex += 1;
              console.dir(predarray);
              console.dir(typeof(predarray)); 
        }
        // If array is not empty, check for Game ID
        else {
            var gamecount = 0;
            // Initial loop to identify if Game ID exists
            for (var i = 0; i < predarray.length; i++) {
                if (predarray[i].pred_game == $(this).parent().parent().attr('id')){
                    gamecount += 1;
                    var duplicategame = i;
                }
            }
            // If Game ID not found, add prediction
            if (gamecount == 0){
                // Add logic
                $(this).toggleClass('chosenwinner');
                predarray[predindex] = {};
                predarray[predindex]['pred_game'] = $(this).parent().parent().attr('id');
                predarray[predindex]['pred_winner'] = $(this).attr('id');
                predindex += 1;
                console.dir(predarray);
                console.dir(typeof(predarray));
                }
            // If Game ID is found...
            else{
                console.log("already exists! "+duplicategame);
                // If same team is selected again
                if(predarray[duplicategame].pred_winner == $(this).attr('id')){
                    $(this).toggleClass('chosenwinner');
                    predarray.splice(duplicategame,1);
                    predindex -= 1;
                    console.log($(this).attr('id'));
                    console.dir(predarray)
                    }
                // Else, if different winner is chosen
                else{
                    // Remove existing entry
                    predarray.splice(duplicategame,1);
                    predindex -=1;
                    // Add this entry to array
                    $(this).toggleClass('chosenwinner');
                    predarray[predindex] = {};
                    predarray[predindex]['pred_game'] = $(this).parent().parent().attr('id');
                    predarray[predindex]['pred_winner'] = $(this).attr('id');
                    predindex += 1;
                    console.dir(predarray);
                    console.dir(typeof(predarray));    
                    // Toggle previous entry off
                    $(this).siblings().toggleClass('chosenwinner');
                    }
                }
            }
    });


    // Submit predictions when Submit button clicked
    $('#predict-submit').on('click', function(event){
        event.preventDefault();
        console.log("Submit button pressed");  // sanity check
        $('.hideme').hide();
        $('#submitted').html('<h2>Prediction Submitted, Good Luck!</h2>');
        var jsonstring = JSON.stringify(predarray);
        var predjson = JSON.parse(jsonstring);
        loop_predictions(predjson);
    });

    // Loop through JSON Array and submit each entry
    function loop_predictions(jsonobject) {
        console.log("loop_predictions is called") // sanity check
        for(var i = 0; i < jsonobject.length; i++) {
            var loop_string = JSON.stringify(jsonobject[i]);
            add_prediction(loop_string);
        }
    };

    // AJAX for posting each prediction as JSON
    function add_prediction(pred_string) {
        console.log("add_predictions is called!") // sanity check
        $.ajax({
            url : "../addprediction/",
            type : "POST",
            headers: {
                "X-CSRFToken": csrftoken,
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            data : pred_string,
            // handle a successful response
            success : function(json) {
                $('#post-text').val(''); // remove the value from the input
                console.log(json); // log the returned json to the console
                $("#talk").prepend("<li><strong>"+json.text+"</strong> - <em> "+json.author+"</em> - <span> "+json.created+
                    "</span> - <a id='delete-post-"+json.postpk+"'>delete me</a></li>");
                console.log("success"); // another sanity check
            },
            // handle a non-successful response
            error : function(xhr,errmsg,err) {
                $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                    " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
                console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }
        });
    };


    // This function gets cookie with a given name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    /*
    The functions below will create a header with csrftoken
    */

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});