var TableEditable = function () {
    js_data=''
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

            jqTds[0].innerHTML = '<input type="text" readonly="readonly" class="form-control input-small" value="' + ''  + '">';
            jqTds[1].innerHTML = '<input type="text" readonly="readonly" class="form-control input-small" value="' + aData[1] + '">';
            jqTds[2].innerHTML = '<select id="roleinfo" style="width:150px;height:23px;" > <option value=" "   >---请选择---</option>  </select>';
            jqTds[3].innerHTML = '<select id="groupinfo" style="width:150px;height:23px;" > <option value=" "   >---请选择---</option>  </select>';
            jqTds[4].innerHTML = '<input type="text" readonly="readonly" class="form-control input-small" value="' + aData[4] + '">';
            jqTds[5].innerHTML = '<a class="edit" href="">保存</a>';
            jqTds[6].innerHTML = '<a class="cancel" href="">取消</a>';

            console.log('start get exe_group');
            jQuery.get("/newbee/api/exe_group",
                function(data){
                    for(var i in data){
                        console.log(data[i].rolename);
                        $("#groupinfo").append("<option value=" + data[i].id +';'+ data[i].detail+">" + data[i].exe_groupname +"</option>");
                    }
                    //$.each(data.results, function(id, value){
                        //$("#groupinfo").append("<option value=" + value['id'] +';'+ value['detail']+">" +    value['exe_groupname'] +"</option>");
                    //});
                    //var appid = $("#groupinfo").children("option:selected").val();
                    //console.log(appid);
                    //$("#appid").val(appid);
                }
            );

            

            console.log('start get query info');
            jQuery.get("/newbee/api/role",
                function(data){
                    console.log('into the accept func');
                    console.log(data);
                    for(var i in data){
                        console.log(data[i].rolename);
                        $("#roleinfo").append("<option value='" + data[i].id + "'>" + data[i].rolename +"</option>");
                    }


                    //$.each(data.results, function(id, value){
                        //console.log(id);
                        //$("#roleinfo").append("<option value='" + value['id'] + "'>" + value['rolename'] +"</option>");
                    //});




                    // 角色下拉框选中值改变时触发
                    $("#roleinfo").change(function(){
                        get_role_varname ()
                    })

                    // 执行组下拉框选中值改变时触发
                    $("#groupinfo").change(function(){
                        get_role_varname ()
                    })

                    // 根据role 获取若干个role name 并弹出文本框
                    function get_role_varname (){
                        role_value=$("#roleinfo").children("option:selected").val();
                        //获取执行组id和detail信息，需要使用split分拆opition 的value才能获取id和detail
                        str_group=$("#groupinfo").children("option:selected").val();
                        str_value=str_group.split(";");
                        group_value=str_value[0];
                        if(role_value!=" " && group_value!=" " ){
                            //获取role 对应的变量名称列表
                            jQuery.get("/newbee/api/role/?id="+role_value,
                                function(data){
                                    $.each(data.results, function(id, value){
                                        if( trim(value['role_var'])==''){
                                            return
                                        }
                                        arr_vars= value['role_var'].split(';')
                                        //alert(arr_vars.length)
                                        str='<table class="table table-striped table-hover table-bordered" id="sample_editable_1">'
                                        for (var i=0;i<arr_vars.length;i++){
                                            str+= '<tr><td>'+ trim(arr_vars[i])+ ':</td><td><input name='+ trim(arr_vars[i]) + ' type="text" class="input" size="20"></td></tr>'
                                        }
                                        //str+=str+'</table>'
                                        document.getElementById("dt_rolename").innerHTML=str
                                        $("#dianjitan").trigger("click");
                                    });
                                }
                            )
                        }
                    }
                    // 点击commit按钮触发的方法
                    $("#transdb_button").click(function(){
                        send_value=''
                        i=1
                        $("#dt_rolename input ").each(function () {

                            if ($(this).val() == "") {
                                alert($(this).attr("name")+" 不能为空！")
                                i=i*0
                            }
                            send_value+=$(this).attr("name")+'='+$(this).val()+';'
                        })
                        if (i!=0){
                            group_var=send_value.substr(0,send_value.length-1)
                            var data = {};
                            data['group_var']=group_var
                            data["exe_groupname"] =$("#groupinfo").children("option:selected").text();
                            str_group=$("#groupinfo").children("option:selected").val();
                            str_value=str_group.split(";");
                            data['detail']=str_value[1];
                            jsdata=JSON.stringify(data);
                            js_data=jsdata
                            document.getElementById("modal_close").click();
                        }

                    })

                    //去左空格;
                    function ltrim(s){
                        return s.replace(/(^\s*)/g, "");
                    }
                    //去右空格;
                    function rtrim(s){
                        return s.replace(/(\s*$)/g, "");
                    }
                    //去左右空格;
                    function trim(s){
                        return s.replace(/(^\s*)|(\s*$)/g, "");
                    }




                }
            );

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

        function save_roleVars_exeGroup(jsdata){
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
                    msg = xhr.responseText;
                    //alert(msg);
                }
            };
            str_group=$("#groupinfo").children("option:selected").val();
            str_value=str_group.split(";");
           	url='/newbee/api/exe_group/'+str_value[0]+'/';
			var csrftoken = getCookie('csrftoken');
            xhr.open("put", url,true);
            xhr.setRequestHeader("Content-type","application/json");
			xhr.setRequestHeader('X-CSRFToken',csrftoken)  
            xhr.send(jsdata);
        }



        function saveRow(oTable, nRow) {

            var jqInputs = $('input', nRow);
            var data = {};
            data["rolename"] = $("#roleinfo").children("option:selected").text();
            data['exe_groupname'] = $("#groupinfo").children("option:selected").text();
            if(data["rolename"]==''||data['exe_groupname']==''||data["rolename"]=='---请选择---'||data['exe_groupname']=='---请选择---')
            {
                alert('请填写角色名和执行组名');
                retrun;
            }

            data['exe'] = '0';
            data['log'] = '0';
            //console.info(jsdata);
            jsdata=JSON.stringify(data);
            if(js_data!=''){
                save_roleVars_exeGroup(js_data)
            }

            //alert(jsdata);
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
                    if (xhr.status==201||xhr.status==200||xhr.status==400||xhr.status==403||xhr.status==415||xhr.status==401) {
                        msg = xhr.responseText;
                        //alert(msg);
                        location.reload();
                    }
                }
            };

            url='/newbee/api/mission/';
			var csrftoken = getCookie('csrftoken');

            //alert (url);
            // 当前URL
            xhr.open("post",url,true);
            xhr.setRequestHeader("Content-type","application/json");
			xhr.setRequestHeader('X-CSRFToken',csrftoken)  
            xhr.send(jsdata);
        }


        function editsaveRow(oTable, nRow) {

            var jqInputs = $('input', nRow);
            var data = {};
            data["rolename"] = $("#roleinfo").children("option:selected").text();
            data['exe_groupname'] = $("#groupinfo").children("option:selected").text();
            if(data["rolename"]==''||data['exe_groupname']==''||data["rolename"]=='---请选择---'||data['exe_groupname']=='---请选择---')
            {
                alert('请填写角色名和执行组名');
                retrun;
            }
            data['exe'] = '0';
            data['log'] = '0';
            jsdata=JSON.stringify(data);
            console.info(jsdata);
            if(js_data!=''){
                save_roleVars_exeGroup(js_data)
            }
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
                        //location.reload();
                    }
                }
            };


            url='http://127.0.0.1:8000/newbee/api/mission/'+jqInputs[1].value+'/';
            console.info(url);

            xhr.open("put", url,true);
            xhr.setRequestHeader("Content-type","application/json");
            xhr.send(jsdata);


        }

        function cancelEditRow(oTable, nRow) {
            $("#role_exegroup").val("00000")
            var jqInputs = $('input', nRow);
            oTable.fnUpdate(jqInputs[0].value, nRow, 0, false);
            oTable.fnUpdate(jqInputs[1].value, nRow, 1, false);
            oTable.fnUpdate(jqInputs[2].value, nRow, 2, false);
            oTable.fnUpdate(jqInputs[3].value, nRow, 3, false);
            oTable.fnUpdate('<a class="edit" href="">修改</a>', nRow, 4, false);
            oTable.fnDraw();
        }

        var table = $('#sample_editable_1');



        var oTable = table.dataTable({

            // Uncomment below line("dom" parameter) to fix the dropdown overflow issue in the datatable cells. The default datatable layout
            // setup uses scrollable div(table-scrollable) with overflow:auto to enable vertical scroll(see: assets/global/plugins/datatables/plugins/bootstrap/dataTables.bootstrap.js). 
            // So when dropdowns used the scrollable div should be removed. 
            //"dom": "<'row'<'col-md-6 col-sm-12'l><'col-md-6 col-sm-12'f>r>t<'row'<'col-md-5 col-sm-12'i><'col-md-7 col-sm-12'p>>",
            //
            "bLengthChange":false,
            "bPaginate": false,
            "bPaginate":false,
            "bInfo": false,
            "searching": false,
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
            //
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
            //var totalString = new Array();
            //var aiNew = oTable.fnAddData(totalString);
            //var nRow = oTable.fnGetNodes(aiNew[0]);

            var aiNew = oTable.fnAddData(['', '', '','','','','','']);
            //alert(aiNew[0]);
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
            //alert(aData[0]);
            //oTable.fnDeleteRow(nRow);
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

            url='/newbee/api/mission/'+aData[1]+'/';
            //alert(url);

            xhr.open("delete", url,true);
            //xhr.setRequestHeader("Content-type","application/json");
            xhr.send(null);

        });

        table.on('click', '.cancel', function (e) {
            js_data=''
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
            //alert('fan');
            //alert(exitData[0]);

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
                //alert("Updated! Do not forget to do some ajax to sync with backend :)");
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
function search() {
    var a=document.getElementById("szxz").value;
    window.location.href="../mission?exe_groupname="+a
}
