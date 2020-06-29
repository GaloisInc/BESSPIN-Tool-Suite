
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

function showError(msg){
    if(msg != undefined) {
        $("#errors").text(msg);
    } else {
        $("#errors").text("Server returned an error. See console for details"); 
    }
}
