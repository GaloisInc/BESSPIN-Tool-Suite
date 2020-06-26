
function reset_form_errors() {
    $('input, select').removeClass("error");
}

$(document).ready(function(){


    // Voter registration verification
    $("#submit_voter_reg_verification").on('click', function() {
        console.log("Verify voter registration");

        // Reset form status for resubmissions
        reset_form_errors();
        $("#no-results").hide();
        $("[id$=display]").text("");
        $("#results").hide();

        //Verify inputs before submitting
        var verify_fields = ["#voter-givennames", "#voter-lastname", "#voter-birthdate"];
        var has_errors = false;
        $.each(verify_fields, function(index, field) {
            var val = $(field).val();
            if(val == undefined || val.length <= 0) {
                has_errors = true;
                $(field).addClass("error");
            }
        });
        if(has_errors) {
            return;
        }

        $.ajax({
            url : 'voter_check_status', 
            type : "GET",
            data : $("#voter_registration_verification_form").serialize(),
            success : function(result) {
                console.log(result);
                // No results
                if(result["voter_q"][0] == undefined) {
                    $("#no-results").show();
                    return;
                }

                // We have a result: Populate page data
                $.each(result["voter_q"][0], function(index, value) {
                    console.log("voter-" + index + "-display", value);
                    // convert date values
                    if(index.includes("time") || index.includes("date")) {
                        var d = new Date(0);
                        d.setUTCSeconds(value);
                        value = d.toUTCString();
                    }
                    if(index.includes("confidential")) {
                        value = value ? "TRUE" : "FALSE";
                    }
                    $("#voter-" + index + "-display").text(value);
                });
                $("#results").show();
            },
            error: function(xhr, result, text) {
                // Handle Form Errors
                console.log("backend returned an error");
            }
        });
    });

    // Voter registration
    $("form#voter_register_form").submit(function(e){
        e.preventDefault();
        reset_form_errors()
        console.log("Submit voter registration");
        var formData = new FormData(this);
        var url = 'voter_register';
        if(window.location.href.includes("official")) {
            url = 'official_register_voter';
        }
        $.ajax({
            url: url, 
            type : "POST",
            data : formData,
            contentType: false,
            cache: false,
            processData: false,
            success : function(result) {
                // Server returned a result
                // redirect to voter_registration_confirmation.html
                if(window.location.href.includes("official")) {
                    window.location.replace("election_official_home.html");
                } else {
                    window.location.replace("voter_registration_confirmation.html");
                }
            },
            error: function(xhr, result, text) {
                if(xhr.status == 401) {
                    window.location.href = "election_official_login.html"
                    return;
                }
                resp = xhr.responseJSON;
                console.log(resp);
                if(resp.hasOwnProperty("errors")) {
                    // Response has errors
                    $.each(resp.errors, function(index, value) {
                        console.log(index, value);
                        $('input[name ="' + index + '"]').addClass("error");
                        $('select[name ="' + index + '"]').addClass("error");
                        $('label[for ="' + index + '"]').addClass("error");
                    });
                }
            }
        })
    });

});