

function empty_table(){
	var div = document.getElementById("queryDataInner");

	div.innerHTML = `<table cellspacing="0" cellpadding="5" id=queryTable>
            <tr>
            	<th> Select </th>
            	<th> Voter ID </th>
                <th> First Name </th>
                <th> Last Name </th>
                <th> Residential Address </th>
                <th> Mailing Address </th>
                <th> Registered Party </th>
                <th> Birthdate </th>
                <th> Initial Reg. Time </th>
                <th> Last Reg. Update </th>
                <th> Status </th>
                <th> Confidential </th>
            </tr>
        </table>`;
}

$(document).ready(function(){

    // Keeps local UI state since we're re-using the login
    // form for the update form.
    var voter_session_active = 0;

    // Voter - Update form
    function voter_update(formData) {
        $.ajax({
            url  : 'voter_update_info',
            type : "POST",
            data : formData,
            contentType: false,
            cache: false,
            processData: false,
            xhrFields: { withCredentials: true },
            success : function(result) {
                voter_session_active = 0;
                window.location.replace("voter_registration_confirmation.html");
                return;
            },
            error: function(xhr, result, text) {
                console.error("Error updating status: " + xhr.status);
            }
        });
    }

    // Voter - Voter update login form
    $("form#voter_login_form").submit(function(e){
        e.preventDefault();
        clearError();
        var formData = new FormData(this);
        if(voter_session_active) {
            voter_update(formData);
            return;
        }
        $.ajax({
            url  : 'voter_update_login',
            type : "POST",
            data : formData,
            contentType: false,
            cache: false,
            processData: false,
            success : function(result) {
                // voter successfully logged in.  Let them know they
                // Can now change things on this form.
                showInfo("Voter verified. Now update the information below as you want saved.");
                console.log("logged in voter update session");
                voter_session_active = 1;
                $('#extra-fields').html(
                    '<label class=firstColLabel for="voter-confidential">Mark My Information as Confidential:</label>'
                    + '<input class=formButton type="checkbox" value="1" id="voter-confidential" name="voter-confidential">'
                    + '<br><br>');
            },
            error: function(xhr, result, text) {
                if(xhr.status == 401) {
                    console.error("Voter registration does not match.  See election official.");
                    showError("Voter registration does not match.  See election official.");
                    return;
                } else if(xhr.status == 400) {
                    console.error("400 error, Must fill in all fields");
                    showError("Please fill-in all fields just as you registered previously.");
                    return;
                }
            }
        });
    });

    // Offical - Voter update form
    $("form#offical_update_voters").submit(function(e){
        e.preventDefault();
        clearError();
        console.log("Update voter clicked");
        var ids = $('input:checked[name^="vsel_"]')
            .map(function(){ return this.id}).get();
        console.log(ids);
        console.log(ids.join());
        var form_action = $('input[name="form-action"]:checked').val();
        if(form_action == undefined || form_action.length == 0) {
            showError("Must select a form action");
            return;
        }

        $("#voter-ids").val(ids.join());
        $("form#offical_update_voters").trigger("change");
        console.log($("form#offical_update_voters").serialize());
        $.ajax({
            url  : 'official_update_voters',
            type : 'GET',
            data : $("form#offical_update_voters").serialize(),
            success : function(result) {
                $("form#official_query_form").submit();
            },
            error: function(xhr, result, text) {
                if(xhr.status == 401) {
                    window.location.href = "/bvrs/election_official_login.html"
                } else {
                    showError();
                }
            }
        });
    });


    // Official - query form
    $("form#official_query_form").submit(function(e){
    	e.preventDefault();

        console.log("Query Clicked");
        // Clear previous errors
        clearError();

        // Preserve any checked items
        var checked = [];
        $("[name^=vsel_]:checked").each(function(){checked.push(this.id)});

        $.ajax({
            url : 'official_query_voters', 
            type : "GET",
            data : $("#official_query_form").serialize(),
            success : function(result) {
                // console.log(result);
                // No results
                if(result["voter_q"] == undefined || result["voter_q"][0] == undefined) {
                    console.log("GET from server returned no results");
                    empty_table();
                }

                
                console.log("GET Query from server succeeded");
                console.log(result);

                empty_table();
				
                $.each(result["voter_q"], function(index, value) {
                	console.log("Adding Voter To Table");
                	console.log(value);
                	addVoterToTable(value);
                });
                // Restore checked items
                $(checked).each(function(i,v ) { $("#" + v).attr("checked", "checked") });
            },
            error: function(xhr, result, text) {
                // Handle Form Errors
                if(xhr.status == 401) {
                    window.location.href = "/bvrs/election_official_login.html";
                } else {
                    console.log("Server returned an error");
                    showError();
                }
            }
        });
    });

});




function addVoterToTable(voter){

	var div = document.getElementById("queryTable");

	var ID = String(voter["id"]);

    var status;
    var confidential;
    var regstatus = ["Active", "Inactive", "Pending Review"];

    status = "<td> " + regstatus[voter["status"]] + " </td>";

    if (voter["confidential"] == 0){
		confidential = "<td> No </td>";
	}
	else{
		confidential = "<td> Yes </td>";
    }

	div.innerHTML += "<tr>" + 
					'<td><input type="checkbox" id="' + ID + '" name="vsel_' + ID + '"></td>' +
					"<td>" + ID + "</td>" +
					"<td>"+ voter["givennames"] + "</td>" +
					"<td>" + voter["lastname"] + "</td>" +
					"<td>" + voter["resaddress"] + "</td>" +
					"<td>" + voter["mailaddress"] + "</td>" +
					"<td>" + voter["registeredparty"] + "</td>" +
					"<td>" + formatDate(voter["birthdate"]) + "</td>" +
					"<td>" + formatDate(voter["initialregtime"]) + "</td>" + 
					"<td>" + formatDate(voter["lastupdatetime"]) + "</td>" +
                    status +
                    confidential +
					"</tr>";

}

function formatDate(epoch_time) {
    var d = new Date(0);
    d.setUTCSeconds(epoch_time);
    month = '' + (d.getMonth() + 1);
    day = '' + d.getDate();
    year = d.getFullYear();

    if (month.length < 2) 
        month = '0' + month;
    if (day.length < 2) 
        day = '0' + day;

    return [year, month, day].join('-');
}

function clearError() {
    $("#errors").text("");    
}

function showInfo(msg){
    $("#messages").text(msg);
}

function showError(msg){
    if(msg != undefined) {
        $("#errors").text(msg);
    } else {
        $("#errors").text("Server returned an error. See console for details"); 
    }
}


function reset_form_errors() {
    $('input, select').removeClass("error");
}

$(document).ready(function(){


    // Voter registration verification
    $("#submit_voter_reg_verification").on('click', function() {
        console.log("Verify voter registration");
        clearError();
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
                $("#no-results").hide();
            },
            error: function(xhr, result, text) {
                if(xhr.status == 404) {
                    $("#no-results").show(); 
                    console.error("NO matching results");
                } else {
                    showError("Unknown error: " + xhr.status);
                    console.error("backend returned an error status: " + xhr.status);
                }
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