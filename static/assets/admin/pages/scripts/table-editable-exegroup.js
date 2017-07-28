var TableEditable = function () {
    var check_flag = 0;
    var handleTable = function () {

        function restoreRow(oTable, nRow) {
            var aData = oTable.fnGetData(nRow);
            var jqTds = $('>td', nRow);

            for (var i = 0, iLen = jqTds.length; i < iLen; i++) {
                oTable.fnUpdate(aData[i], nRow, i, false);
            }

            oTable.fnDraw();
        }

        function editRow(oTable, nRow) {
            var aData = oTable.fnGetData(nRow);

            var jqTds = $('>td', nRow);
            jqTds[0].innerHTML = '<input type="text" readonly="readonly" class="form-control input-small" value="' + aData[0] + '">';
            jqTds[1].innerHTML = '<input type="text" id="lab_exe_groupname" class="form-control input-small" value="' + ((nRow.children)[1]).innerText + '">';
            jqTds[2].innerHTML =  '<input type="text" readonly="readonly" class="form-control input-small" value="' + aData[2] + '">';
            jqTds[3].innerHTML = '<input type="text" class="form-control input-small" value="' + aData[3] + '">';
            jqTds[4].innerHTML = '<input type="text" readonly="readonly" class="form-control input-small" value="' + aData[4] + '">';
            jqTds[5].innerHTML = '<a class="edit" href="">保存</a>';
            jqTds[6].innerHTML = '<a class="cancel" href="">取消</a>';
            //Jane.Hoo start，检查执行组名
             $('#lab_exe_groupname').change(function (e) {
                 checkRow(oTable, nRow);
            })
            //Jane.Hoo end
        }
        //written by Jane.Hoo
        //实现执行组名唯一判断
        function checkRow(oTable, nRow) {
            var jqInputs = $('input', nRow);
            var data = {};
            data["exe_groupname"] = jqInputs[1].value;
            data['group_var']=jqInputs[2].value;
            data['detail']=jqInputs[3].value;
            jsdata=JSON.stringify(data);
            var xhr;
            // code for IE7+, Firefox, Chrome, Opera, Safari
            if (window.XMLHttpRequest) {
            	xhr = new XMLHttpRequest();
            }
            else {
            	// code for IE6, IE5
            	xhr = new ActiveXObject("Microsoft.XMLHTTP");
            }
            url_check='/newbee/api/exe_group/?exe_groupname='+data["exe_groupname"]
            xhr.open("get",url_check,true);
            xhr.setRequestHeader("Content-type","application/json");
            xhr.send(jsdata);
            xhr.onreadystatechange=function() {
            	if (xhr.readyState==4) {
                    //0：未初始化  1：读取中   2：已读取   3：交互中    4：完成
                    msg = xhr.responseText;
                    check_flag = msg.split(',')[0].split(':')[1];
                    if( check_flag == 1 ){
                        alert("该执行组名已存在，请检查！")
                    }
          	  	}
            }
        }
        function getCookie(name) {  
			var cookieValue = null;  
			if (document.cookie && document.cookie != '') {  
				var cookies = document.cookie.split(';');  
				for (var i = 0; i < cookies.length; i++) {  
					var cookie = cookies[i].trim();  
					// Does this cookie string begin with the name we want?  
					if (cookie.substring(0, name.length + 1) == (name + '=')) {  
						cookieValue = decodeURIComponent(cookie.substring(name.length + 1));  
						break;  
					}  
				}  
			}  
			return cookieValue;  
		}  

        function saveRow(oTable, nRow) {
            var jqInputs = $('input', nRow);
            //alert("check_flag:"+check_flag)
            if(jqInputs[1].value!=''&& jqInputs[3].value!=''&& check_flag!='1')
            {
                oTable.fnUpdate(jqInputs[0].value, nRow, 0, false);
                oTable.fnUpdate(jqInputs[1].value, nRow, 1, false);
                oTable.fnUpdate(jqInputs[2].value, nRow, 2, false);
                oTable.fnUpdate(jqInputs[3].value, nRow, 3, false);
                oTable.fnUpdate(jqInputs[4].value, nRow, 4, false);
                oTable.fnUpdate('<a class="edit" href="">修改</a>', nRow, 5, false);
                oTable.fnUpdate('<a class="delete" href="">删除</a>', nRow, 6, false);
                oTable.fnDraw();
                var data = {};
                data["exe_groupname"] = jqInputs[1].value;
                data['group_var']=jqInputs[2].value;
                data['detail']=jqInputs[3].value;
                jsdata=JSON.stringify(data);
                var xhr;
                // code for IE7+, Firefox, Chrome, Opera, Safari
                if (window.XMLHttpRequest) {
            	    xhr = new XMLHttpRequest();
                }
                else {
            	    // code for IE6, IE5
            	    xhr = new ActiveXObject("Microsoft.XMLHTTP");
                }

                xhr.onreadystatechange=function() {
                    console.log('---------------------------------------')

            	    if (xhr.readyState==4) {
				        //0：未初始化  1：读取中   2：已读取   3：交互中    4：完成
            		    if (xhr.status==201||xhr.status==200||xhr.status==400||xhr.status==403||xhr.status==415||xhr.status==401) {
            			    msg = xhr.responseText;
                            console.log(msg);
                            //location.reload();
          		  	    }
          	  	    }
                };

                //url = window.location.href;
                url='/newbee/api/exe_group/';
                // 当前URL
				var csrftoken = getCookie('csrftoken');
				xhr.open("post",url,true);
                xhr.setRequestHeader("Content-type","application/json");
				xhr.setRequestHeader('X-CSRFToken',csrftoken)  
                xhr.send(jsdata);
            }else{
                alert('请按要求填写执行组名和详细信息，并确保执行组名唯一！');
                return;
            }
        }
        function editsaveRow(oTable, nRow) {

            var jqInputs = $('input', nRow);
            //alert(jqInputs[1].value);
            if(jqInputs[1].value==''||jqInputs[3].value==''|| check_flag=='1')
            {
                alert('请按要求填写执行组名和详细信息，并确保执行组名唯一');
                return;
            }
            oTable.fnUpdate(jqInputs[0].value, nRow, 0, false);
            oTable.fnUpdate(jqInputs[1].value, nRow, 1, false);
            oTable.fnUpdate(jqInputs[2].value, nRow, 2, false);
            oTable.fnUpdate(jqInputs[3].value, nRow, 3, false);
            oTable.fnUpdate(jqInputs[4].value, nRow, 4, false);
            oTable.fnUpdate('<a class="edit" href="">修改</a>', nRow, 5, false);
            oTable.fnUpdate('<a class="delete" href="">删除</a>', nRow, 6, false);
            oTable.fnDraw();


            var data = {};
            data["exe_groupname"] = jqInputs[1].value;
            data['group_var']=jqInputs[2].value;
            data['detail']=jqInputs[3].value;
            jsdata=JSON.stringify(data);

            var xhr;
            // code for IE7+, Firefox, Chrome, Opera, Safari
            if (window.XMLHttpRequest) {
            	xhr = new XMLHttpRequest();
            }
            else {
            	// code for IE6, IE5
            	xhr = new ActiveXObject("Microsoft.XMLHTTP");
            }

            xhr.onreadystatechange=function() {
            	if (xhr.readyState==4) {
				        //0：未初始化  1：读取中   2：已读取   3：交互中    4：完成
            		if (xhr.status==201||xhr.status==200) {
            			msg = xhr.responseText;
                        location.reload();
                        //alert(msg);
          		  	}
          	  	}
            };

            url='/newbee/api/exe_group/'+jqInputs[0].value+'/';

            xhr.open("put", url,true);
            xhr.setRequestHeader("Content-type","application/json");
            xhr.send(jsdata);


        }

        function cancelEditRow(oTable, nRow) {
            var jqInputs = $('input', nRow);
            oTable.fnUpdate(jqInputs[0].value, nRow, 0, false);
            oTable.fnUpdate(jqInputs[1].value, nRow, 1, false);
            oTable.fnUpdate(jqInputs[2].value, nRow, 2, false);
            oTable.fnUpdate(jqInputs[3].value, nRow, 3, false);
            oTable.fnUpdate('<a class="edit" href="">Edit</a>', nRow, 4, false);
            oTable.fnDraw();
        }

        var table = $('#sample_editable_1');

        var oTable = table.dataTable({

            // Uncomment below line("dom" parameter) to fix the dropdown overflow issue in the datatable cells. The default datatable layout
            // setup uses scrollable div(table-scrollable) with overflow:auto to enable vertical scroll(see: assets/global/plugins/datatables/plugins/bootstrap/dataTables.bootstrap.js).
            // So when dropdowns used the scrollable div should be removed.
            //"dom": "<'row'<'col-md-6 col-sm-12'l><'col-md-6 col-sm-12'f>r>t<'row'<'col-md-5 col-sm-12'i><'col-md-7 col-sm-12'p>>",
            //
            //"lengthMenu": [
            //    [5, 15, 20, -1],
            //    [5, 15, 20, "All"] // change per page values here
            //],

            // Or you can use remote translation file
            //"language": {
            //   url: '//cdn.datatables.net/plug-ins/3cfcc339e89/i18n/Portuguese.json'
            //},

             //set the initial value
            //"pageLength": 10,
            "bLengthChange":false,
            "bPaginate": false,
            "bPaginate":false,
            "bInfo": false,
            "searching": false,
            //"language": {
            //    "lengthMenu": " _MENU_ records"
            //},
            "columnDefs": [{ // set default column settings
                'orderable': true,
                'targets': [0]
            }, {
                "searchable": true,
                "targets": [0]
            }],
            "order": [
                [0, "asc"]
            ] // set first column as a default sort by asc
        });

        //var tableWrapper = $("#sample_editable_1_wrapper");
        //
        //tableWrapper.find(".dataTables_length select").select2({
        //    showSearchInput: false //hide search box with special css class
        //}); // initialize select2 dropdown

        var nEditing = null;
        var nNew = false;



        $('#sample_editable_1_new').click(function (e) {
            e.preventDefault();
            if (nNew && nEditing) {

                if (confirm("Previose row not saved. Do you want to save it ?")) {
                    saveRow(oTable, nEditing); // save
                    $(nEditing).find("td:first").html("Untitled");
                    nEditing = null;
                    nNew = false;

                } else {

                    oTable.fnDeleteRow(nEditing); // cancel
                    nEditing = null;
                    nNew = false;

                    return;
                }
            }

            var aiNew = oTable.fnAddData(['', '', '','','','','','']);
            var nRow = oTable.fnGetNodes(aiNew[0]);
            editRow(oTable, nRow);
            nEditing = nRow;
            nNew = true;
        });

        table.on('click', '.delete', function (e) {
            e.preventDefault();

            if (confirm("Are you sure to delete this row ?") == false) {
                return;
            }

            var nRow = $(this).parents('tr')[0];
            var aData = oTable.fnGetData(nRow);
            var jqTds = $('>td', nRow);
            oTable.fnDeleteRow(nRow);
            var xhr;
            if (window.XMLHttpRequest)
              {// code for IE7+, Firefox, Chrome, Opera, Safari
            	xhr = new XMLHttpRequest();
              }
            else
              {// code for IE6, IE5
            	xhr = new ActiveXObject("Microsoft.XMLHTTP");
              }
                        xhr.onreadystatechange=function() {
             	  if(xhr.readyState==4) {
   				      //0：未初始化  1：读取中   2：已读取   3：交互中    4：完成
             		    if(xhr.status==200||xhr.status==405) {
             			      msg = xhr.responseText;
                              //alert(msg);
             		    }
             	  }
            };

            var dedata = {};

            url='/newbee/api/exe_group/'+aData[0]+'/';

            xhr.open("delete", url,true);
            //xhr.setRequestHeader("Content-type","application/json");
            xhr.send(null);

        });

        table.on('click', '.cancel', function (e) {
            e.preventDefault();
            if (nNew) {
                oTable.fnDeleteRow(nEditing);
                nEditing = null;
                nNew = false;
            } else {
                restoreRow(oTable, nEditing);
                nEditing = null;
            }
        });

        table.on('click', '.edit', function (e) {
            e.preventDefault();
            /* Get the row as a parent of the link that was clicked on */
            var nRow = $(this).parents('tr')[0];
            var exitData = oTable.fnGetData(nRow);

            if (nEditing !== null && nEditing != nRow) {

                /* Currently editing - but not this row - restore the old before continuing to edit mode */
                restoreRow(oTable, nEditing);
                editRow(oTable, nRow);
                nEditing = nRow;
            } else if (nEditing == nRow && this.innerHTML == "保存") {
                /* Editing this row and want to save it */
                if(exitData[0]){
                   editsaveRow(oTable, nEditing);
                }else{
                    saveRow(oTable, nEditing);
                }
                //editsaveRow(oTable, nEditing);
                nEditing = null;
            } else {
                /* No edit in progress - let's start one */
                editRow(oTable, nRow);
                nEditing = nRow;
            }
        });

    }

    return {
        //main function to initiate the module
        init: function () {
            handleTable();
        }
    };


}();

//#搜索框功能函数
function search() {
    var a=document.getElementById("szxz").value;
    window.location.href="../exe_group?exe_groupname="+a
}
//弹框功能函数
function openwins(val_id ,var_name) {
        window.open("../host_exe_group?id="+val_id+"&exe_groupname="+var_name, "newwindow","height=600, width=400, top=100,left=100,toolbar=no, menubar=no, scrollbars=no, resizable=no,location=no,status=no")

}
