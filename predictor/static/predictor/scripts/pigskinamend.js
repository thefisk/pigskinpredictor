 // Initialise mobile menu trigger
 $(document).ready(function(){
    $('.sidenav').sidenav();
  });

$(function() {

    // Initialise chosenbanker variable
    var chosenbanker;

    // Read in used bankers
    var usedbankers = [];
    $('#bankers li').each(function(){
        usedbankers.push($(this).attr('id'));
    });

    // Double click action
    $('.team').on('dblclick', function(event){
        if ($(this).attr('id') == "Away"){
            // If same banker is double-clicked
            if($(this).parent().parent().attr('id') == chosenbanker){
                // pass    
            }
            else{
                // If No Banker set
                if (chosenbanker == null){
                    event.stopPropagation();
                    
                    $(this).toggleClass('chosenbanker');
                    // Turn off chosenwinnerclass if present
                    if($(this).hasClass('chosenwinner')){
                        $(this).removeClass('chosenwinner')
                    }
                    chosenbanker = $(this).parent().parent().attr('id');
                    // Add to array if not already in there
                    var gamecount = 0;
                    for (var i = 0; i < predarray.length; i++) {
                        if (predarray[i].pred_game == $(this).parent().parent().attr('id')){
                            gamecount += 1;
                        }
                    }
                    if (gamecount == 0){
                    predarray[predindex] = {};
                    predarray[predindex]['pred_game'] = $(this).parent().parent().attr('id');
                    predarray[predindex]['pred_winner'] = $(this).attr('id');
                    predindex += 1;
                    }
                    else {
                    
                    }
                    
                    
                }
                /// If other Banker exists
                else {
                    // Turn previous banker Green
                    $('#'+chosenbanker).find('#Away').toggleClass("chosenbanker");
                    $('#'+chosenbanker).find('#Away').addClass("chosenwinner");
                    
                    // Change chosenbanker variable
                    chosenbanker = $(this).parent().parent().attr('id');
                    // Change new Banker to orange class
                    $(this).toggleClass('chosenbanker');
                    // Turn off chosenwinnerclass if present
                    if($(this).hasClass('chosenwinner')){
                        $(this).removeClass('chosenwinner')
                    }
                    // Add to array if not already in there
                    var gamecount = 0;
                    // Initial loop to identify if Game ID exists
                    for (var i = 0; i < predarray.length; i++) {
                        if (predarray[i].pred_game == $(this).parent().parent().attr('id')){
                            gamecount += 1;
                        }
                    }
                    if (gamecount == 0){
                    predarray[predindex] = {};
                    predarray[predindex]['pred_game'] = $(this).parent().parent().attr('id');
                    predarray[predindex]['pred_winner'] = $(this).attr('id');
                    predindex += 1;
                    }
                    
                    
                }
            }   
        }   
    })

    // Setup Pred Array and Index value to increment
    var predarray = [];
    var predindex = 0;

    // Count number of games for pre-submission verification
    var numberOfGames = $('.card').length;

    // PigskinAmendSpecific
    // Read in already chosen teams by class
    $('.chosenwinner').each(function(){
        predarray[predindex] = {};
        predarray[predindex]['pred_game'] = $(this).parent().parent().attr('id');
        predarray[predindex]['pred_winner'] = $(this).attr('id');
        predindex += 1;
        
    });
    // Also read in chosen banker
    $('.chosenbanker').each(function(){
        chosenbanker = $(this).parent().parent().attr('id');
        
        predarray[predindex] = {};
        predarray[predindex]['pred_game'] = $(this).parent().parent().attr('id');
        predarray[predindex]['pred_winner'] = $(this).attr('id');
        predindex += 1;
        
    });

    // Single click action
    $('.team').on('click', function(event){
        event.stopPropagation();
        // Check if a Banker has been single-clicked, if so, do nothing
        if ($(this).hasClass('chosenbanker')){
            // pass
        }
        else {
            // Add selected teams to array if array is empty
            if (predarray.length == 0){
                  // Add logic
                  $(this).toggleClass('chosenwinner');
                  predarray[predindex] = {};
                  predarray[predindex]['pred_game'] = $(this).parent().parent().attr('id');
                  predarray[predindex]['pred_winner'] = $(this).attr('id');
                  predindex += 1;
                  
                   
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
                    
                    
                    }
                // If Game ID is found...
                else{
                    
                    // If same team is selected again
                    if(predarray[duplicategame].pred_winner == $(this).attr('id')){
                        $(this).toggleClass('chosenwinner');
                        predarray.splice(duplicategame,1);
                        predindex -= 1;
                        
                        
                        }
                    // Else, if different winner is chosen
                    else{
                        // If other team is Banker
                        if($(this).siblings().hasClass('chosenbanker')){
                            // Turn off orange class
                            $(this).siblings().toggleClass('chosenbanker');
                            // Make chosenbanker null
                            chosenbanker = null;
                            // Remove existing entry
                            predarray.splice(duplicategame,1);
                            predindex -=1;
                            $(this).toggleClass('chosenwinner');
                            predarray[predindex] = {};
                            predarray[predindex]['pred_game'] = $(this).parent().parent().attr('id');
                            predarray[predindex]['pred_winner'] = $(this).attr('id');
                            predindex += 1;
                            
                        }
                        // If other team is NOT Banker
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
                            
                                
                            // Toggle previous entry off
                            $(this).siblings().toggleClass('chosenwinner');
                            }
                        }
                    }
                }
        }
    });


    // Submit predictions when Submit button clicked
    $('#predict-submit').on('click', function(event){
        event.preventDefault();
        if(chosenbanker == null){
            window.alert("Please choose a banker");
            }
        else{
            if(usedbankers.includes(chosenbanker)){
                window.alert("Banker already used - please choose another")
                }
            else{
                // Initiate Banker Object
                var bankerobj = [];
                bankerobj[0]= {};
                bankerobj[0]['bank_game']=chosenbanker;
                var jsonbanker = JSON.stringify(bankerobj[0]);
                if(predarray.length == numberOfGames){
                    $('.hideme').hide();
                    $('#submitted').html('<h3>Predictions Amended, Good Luck!</h3>');
                    var jsonstring = JSON.stringify(predarray);
                    var predjson = JSON.parse(jsonstring);
                    loop_predictions(predjson);
                    // Post banker
                    add_banker(jsonbanker);
                    }
                else{
                    window.alert("Please fill in all predictions");
                    }
                }
            }
        });

    // Loop through JSON Array and submit each entry
    function loop_predictions(jsonobject) {
        for(var i = 0; i < jsonobject.length; i++) {
            var loop_string = JSON.stringify(jsonobject[i]);
            add_prediction(loop_string);
        }
    };

    // AJAX for posting each prediction as JSON
    function add_prediction(pred_string) {
        $.ajax({
            url : "../ajaxamendprediction/",
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
                 // log the returned json to the console
                $("#talk").prepend("<li><strong>"+json.text+"</strong> - <em> "+json.author+"</em> - <span> "+json.created+
                    "</span> - <a id='delete-post-"+json.postpk+"'>delete me</a></li>");
            },
            // handle a non-successful response
            error : function(xhr,errmsg,err) {
                $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                    " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
                 // provide a bit more info about the error to the console
            }
        });
    };

        // AJAX for the individual Banker as JSON
        function add_banker(bank_string) {
            $.ajax({
                url : "../ajaxamendbanker/",
                type : "POST",
                headers: {
                    "X-CSRFToken": csrftoken,
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                data : bank_string,
                // handle a successful response
                success : function(json) {
                    $('#post-text').val(''); // remove the value from the input
                     // log the returned json to the console
                    $("#talk").prepend("<li><strong>"+json.text+"</strong> - <em> "+json.author+"</em> - <span> "+json.created+
                        "</span> - <a id='delete-post-"+json.postpk+"'>delete me</a></li>");
                },
                // handle a non-successful response
                error : function(xhr,errmsg,err) {
                    $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                        " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
                     // provide a bit more info about the error to the console
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