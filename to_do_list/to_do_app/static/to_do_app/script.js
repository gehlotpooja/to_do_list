$(document).ready(function () {
    $("#tag_line").fadeIn("slow");
    var upd_task_prev;
    /* Refreshes the Content of Tables when any AJAX Call is Successful */
    function refreshData() {
        /* Method - 1: Makes an AJAX Request, gets the updated data in JSON format. Using the JSON data, updates the
        tables accordingly */
        $.ajax({
            type: 'POST',
            url: '/refresh_data/',
            cache: false,
            success: function (data) {
                // Removes all the rows except the first row from the Main Table
                $('#maintable tbody').find("tr:gt(0)").remove();
                // Removes all the rows except the first row from the Completed Table
                $('#completed-table tbody').find("tr:gt(0)").remove();
                // Parsing the JSON Data

                response = JSON.parse(data);
                console.log("response *******", response)
                // Resets the Add Task input field
                $('#maintable tbody').find('tr:eq(0)').find('input').val("");

                var dates = []
                for (var i = 0; i < response.length; i++) {
                    dates.push(new Date(response[i].fields['date_posted']));
                }
//                var maxDate = new Date(Math.max.apply(null, dates));
                //console.log(maxDate);

                // Updating the timestamp - Last modified date
//                $('.timestamp').text("Last modified on: " + maxDate.toLocaleString('en-US', { month: 'long', day: '2-digit', year: 'numeric' }));

                // Loading the tables using JSON data
                for (var i = 0; i < response.length; i++) {
                    var task_id = response[i].pk;
                    var task_title = response[i].fields['task_title'];
                    var is_checked = response[i].fields['is_checked'];

                    //console.log('Id: ' + task_id + ' Name: ' + task_title);
                    // Loading Active Tasks Table
                    if (is_checked == false) {
                        var active_row = `<tr class="task_` + task_id + `">
				<td><input type="checkbox" title="Mark as Complete" class="form-check-input mark_as_done"
						id="`+ task_id + `"></td>
				<td colspan="2">
					<h4 class="text-left" id="title'+ task_id +'">` + task_title + `</h4>
				</td>
				<td><i class="fa fa-pencil-square-o update_btns" title="Edit Task" style="color:#0ba8c1;"></i>
					<i class="fa fa-check update_task_btn" title="Update"
						style="color: rgb(16, 172, 211); display: none;"></i>
					<i class="fa fa-close deleterow delete_existing_row" title="Delete Task"
						style="color:red; float:right;"></i>
			</tr>`;
                        $('#maintable tbody').append(active_row);

                    }
//                     Loading Completed Tasks Table
                    else {
                        var completed_row = `<tr class="task_` + task_id + `">
                    <td>

                        <input type="checkbox" title="Mark as Incomplete" class="form-check-input mark_as_undone"
                            id="`+ task_id + `" checked></td>
                    <td>
                        <h4 class="text-left completed_tasks" id="title`+ task_id + `">` + task_title + `</h4>
                    </td>
                    <td class="button-row"></td>
                </tr>`;
                        $('#completed-table tbody').append(completed_row);

                    }
                }
            }
        });

        /* Method - 2:  Refreshes both the tables using jQuery. NO AJAX Calls are made. */
        //$("#maintable").load(window.location.href + " #maintable");
        //$("#completed-table").load(window.location.href + " #completed-table");
    }
    refreshData();

/* Adding a New Task to the Database and show the same in the Active Task Table */
    $("table").on('click', "#add_task_btn", function () {
        console.log("iniside script ")
        var task_name;
        // Getting the Task Name - Stripping the leading and trailing whitespaces
        task_name = $.trim($('#add_task').val());

        if (task_name != "") {
            console.log("**********hello******", task_name)
            $.ajax(
                {
                    type: "POST",
                    url: "/add_new_task/",
                    data: {
                        task_title: task_name,
                    },
                    success: function (data) //This will get the data returned by the /add_new_task end point in JSON Format.
                    {
                        //'data' variable is in JSON Format. {key: value}
                        // The task_id that is generated for the newly added Task is present in the task_id variable
                        task_id = data.id;
                        task_name = data.task_title;

                        //Remove the current row
                        //$("#add_task_btn").parent().parent().remove();

                        //Add the added task to the Active Tasks Table
                        //var row = '<tr><td><input type="checkbox" title="Mark as Complete" class="form-check-input mark_as_done" id="' + task_id + '"></td><td colspan="2"><h4 align="left" id="title' + task_id + '">' + task_name + '</h4></td><td><button class="btn btn-side deleterow delete_existing_row" title="Delete this Task" style="float: right;"><i class="fa fa-close"></i></button></td></tr>';
                        //$('#maintable').append(row);
                        refreshData();
                    }
                })
        }
        else {
            alert('Enter a Valid Task Name!');
        }
    });

    $("table").on('click', ".mark_as_done, .mark_as_undone", function () {
        if ($(this).hasClass('mark_as_done')) {
            // Script to Move the task from Active Table to Complete Table
            var check_id;
            check_id = $(this).attr("id");
            class_name = $(this).attr("class");

            //alert('Class: ' + class_name)

            task_name = $("#title" + check_id).html();
            //alert('Task is: ' + task_name);
            $.ajax(
                {
                    // Method of sending the Data.
                    type: "POST",
                    // URL to which the Data should be sent to.
                    url: "/move_tasks/",
                    // Data - We're sending the selected Task's ID and CLASS Name to the URL.
                    data: {
                        task_id: check_id,
                        task_state: class_name
                    },
                    success: function () {
                        //Remove from the Active Table
                        //$("#"+check_id).parent().parent().remove();
                        //Append to the Complete Table
                        //var row = '<tr><td><input type="checkbox" title="Mark as Incomplete" class="form-check-input mark_as_undone" id="'+ check_id +'" checked></td><td><h4 align="left" id="title'+ check_id + '" class="completed_tasks">'+ task_name + '</h4></td><td class="button-row"></td></tr>';
                        //$('#completed-table').append(row);
                        refreshData();


                    }
                })

        }
        else {
            //Script to Move the Tasks from Complete Table to Active Table
            var un_check_id;
            un_check_id = $(this).attr("id");
            task_name = $("#title" + un_check_id).html();
            class_name = $(this).attr("class");
            //alert('Task is: ' + task_name);
            $.ajax(
                {
                    type: "POST",
                    url: "/move_tasks/",
                    data: {
                        task_id: un_check_id,
                        task_state: class_name
                    },
                    success: function () {
                        //Remove from the Completed Table
                        //$("#"+un_check_id).parent().parent().remove();
                        //Append to the Active Table
                        //var row = '<tr><td><input type="checkbox" title="Mark as Complete" class="form-check-input mark_as_done" id="' + un_check_id + '"></td><td colspan="2"><h4 align="left" id="title' + un_check_id + '">' + task_name + '</h4></td><td><button class="btn btn-side deleterow delete_existing_row" title="Delete this Task" style="float: right;"><i class="fa fa-close"></i></button></td></tr>';
                        //$('#maintable').append(row);
                        refreshData();

                    }
                })

        }

    });


});