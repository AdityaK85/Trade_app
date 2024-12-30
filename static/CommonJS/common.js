export const log = console.log;
///////////////////////////////////////// call ajax function
export async function callAjax(url, data, _this=null, loading_text=null, comp_text=null, formData=false, show_page_loader = false) 
{
	try {
		var response;
		if (_this)
		{
			$(_this).prop("disabled", true);
			_this.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> ${loading_text}...`;
		}
		
		if (formData)
		{
			console.log(data,'......formdata')
			await $.ajax({
				method: "POST",
				url: url,
				enctype: "mutipart/form_data",
				processData: false,
				contentType: false,
				cache: false,
				data: data,
				mode: 'same-origin',
				success: function (resp) 
				{			   
					if (_this)
					{
						$(_this).prop("disabled", false);
						_this.innerHTML = comp_text;
					}
					response = resp;
				}
			});
			try {

			}catch {

			}
		}
		else
		{
			await $.ajax({
				method: "POST",
				url: url,
				cache: false,
				data : data,
				success: function (resp) 
				{			   
					if (_this)
					{
						$(_this).prop("disabled", false);
						_this.innerHTML = comp_text;
					}
					response = resp;
				}
			});
		}
		
		return response;
	} 
	catch (error) 
	{
		
		return false;
	}
}

///////////////////////////////////////// Email validator
export async function emailValidator(field)
{
	try 
	{
		var emailfilter = /^\b[A-Z0-9._%-]+@[A-Z0-9.-]+\.[A-Z]{2,4}\b$/i;
		var val = $(`#${field}`).val();
		if ((val == '') || (!emailfilter.test(val)))
		{
			$(`#${field}`).addClass("error_class");
			$(`#${field}`).focus();
			return false;
		}
		
		return val;
	} 
	catch (error) 
	{
		log(error);
		return false;
	}
}
export async function emailValidatortoast(field)
{
	try 
	{
		var emailfilter = /^\b[A-Z0-9._%-]+@[A-Z0-9.-]+\.[A-Z]{2,4}\b$/i;
		var val = $(`#${field}`).val();
		if ((val == '') || (!emailfilter.test(val)))
		{
			showToastMsg('Invalid Email', 'Please enter a valid email', 'error')
			$(`#${field}`).focus();
			return false;
		}
		
		return val;
	} 
	catch (error) 
	{
		log(error);
		return false;
	}
}

export async function filedValidator(field)
{
	try 
	{
		
		var val = $(`#${field}`).val();
		
		if (val == '')
		{
			$(`#${field}`).addClass("error_class");
			$(`#${field}`).focus();
			return false;
		}
		
		return val;
	} 
	catch (error) 
	{
		log(error);
		return false;
	}
}

export async function filedValidatorToastmsg(field)
{
	try 
	{
		
		var val = $(`#${field}`).val();
		
		if (val == '')
		{
			showToastMsg('Password', 'Please enter a your password', 'error')
			$(`#${field}`).focus();
			return false;
		}
		
		return val;
	} 
	catch (error) 
	{
		log(error);
		return false;
	}
}

///////////////////////////////////////// loop through fields and show error msg
// export async function fieldsValidator(fields) 
// {
// 	try 
// 	{
// 		var values = {}
// 		for (var field of fields)
// 		{
// 			var val = $(`#${field}`).val()
// 			if (val == '' || val == null)
// 			{
// 				$(`#${field}`).addClass("error_class");
// 				$(`#${field}`).focus();
// 				return false;
// 			}
// 			else
// 			{
// 				values[field] = val;
// 			}
// 		}	
// 		return values;
// 	} 
// 	catch (error) 
// 	{
// 		log(error);
// 		return false;
// 	}
// }


export async function fieldsValidator(fields, allowedFileTypes = null) {
    try {
        var values = {};
        for (var field of fields) {
            
			if (field == 'redirect_link') {
				var val = $(`#${field}`).val();
				if (val.trim() == '' || val.trim() == null) {
					$(`#${field}`).addClass("error_class");
					$(`#${field}`).focus();
					return false;
				}
				else if(/^(http(s):\/\/.)[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)$/g.test(val)) {
					values[field] = val;
				} else {
					showToastMsg('URL Error', 'Please enter a valid url.', 'error');
					return false;
				}
			}
			else {

                var val = $(`#${field}`).val();
                if (val.trim() == '' || val.trim() == null) {
                    $(`#${field}`).addClass("error_class");
                    $(`#${field}`).focus();
					
                    return false;
                } else {
                    values[field] = val;
                }
            }
        }
        return values;
    } catch (error) {
        return false;
    }
}


///////////////////////////////////////// Remove error class

export function removeError(element)
{
	$(`#${element}`).removeClass("error_class");
}

//////////////////////////////////////// Sweetalerts

export async function sweetAlertMsg(title, text, icon, withCancel='nocancel', confirmText='Ok', cancelText="Cancel")
{
	var cancel = (withCancel == 'cancel') ? 0 : 1;
	var userPreference = false;
	await Swal.fire({title:title, text:text, icon:icon, showCancelButton:!cancel, confirmButtonColor:"#556ee6", cancelButtonColor:"#f46a6a", allowOutsideClick: false,
		allowEscapeKey : false, 
		confirmButtonText: confirmText,
		cancelButtonText: cancelText,}
	).then((result) => 
	{
		if (result.isConfirmed) {userPreference=true;}
	});
	return userPreference;
}

/////////////////////////////////////// Reset cotrols
export function resetControls(fields)
{
	for (var field of fields)
	{
		var val = $(`#${field}`).val('');
	}	
}

/////////////////////////////////////// check all checkboxes using class

export async function checkAllCheckBoxes(_this, check_class, table_id)
{
	var table = $('#'+ table_id).DataTable();
	var rows = table.rows({ 'search': 'applied' }).nodes();
	$('.'+ check_class, rows).prop('checked', _this.checked);
};

////////////////////////////////////// Toast Messages

export function showToastMsg(title, message, type='error')
{
	if (type == 'error')
	{
		
		iziToast.error({
			title: title,
			message: message,
			timeout: 3000,
			position: 'bottomRight'
		});
	}
	else if (type == 'success')
	{
		
		iziToast.success({
			title: title,
			message: message,
			timeout: 3000,
			position: 'bottomRight'
		});
	}
	else
	{
		iziToast.warning({
			title: title,
			message: message,
			timeout: 3000,
			position: 'bottomRight'
		});
	}
}

////////////////////////////////// Check file size 

export async function validateFile(input, size)
{
	var ext_arr = ['xlsx'];
	var f = $('#'+input)[0].files[0];
	var sizeInMb = f.size/1024;
	var sizeLimit= 1024*size;
	var filename = f.name;
	var ext = (/[.]/.exec(filename)) ? /[^.]+$/.exec(filename) : undefined;
	
	if ((!ext) || (!ext_arr.includes(ext[0])))
	{
		showToastMsg('Error', 'You can only select .xlsx files...');
		$('#'+input).val('');
		return false;
	}
	// else if (sizeInMb > sizeLimit) 
	// {
	// 	showToastMsg('Error', `Sorry the file exceeds the maximum size of ${size} MB!`);
	// 	$('#'+input).val('');
	// 	return false;
	// }
	return f;
}

///////////////////////////////// common function for row level editing

async function handleCellEditAnalyst(event) 
{
	const cell = event.target;
	const row = cell.parentNode;
	const value = cell.innerText;
	
	var script_id = row.dataset['script_id'];
	
	if (value == '--'){}
	if (isNaN(value) || value == '') 
	{
		var type = cell.dataset['type'];
		cell.innerHTML = `${value} <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>`
		var response = await callAjax('/update_analyst_wathlist_aj/', {'script_id' : script_id, 'value' : null, 'type' : type});
		cell.innerText = '--';
		showToastMsg('Error', 'Please enter a valid number...', 'error');
	} 
	else 
	{
		var type = cell.dataset['type'];
		cell.innerHTML = `${value} <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>`
		var response = await callAjax('/update_analyst_wathlist_aj/', {'script_id' : script_id, 'value' : value, 'type' : type});

		if (response.status == 1){
			cell.innerText = response['value'];
		}
		else{
			cell.innerText = '--';
		}
		showToastMsg('Success', response.msg, 'success');
	}
}

async function handleCellEditOperator(event) 
{
	const cell = event.target;
	const row = cell.parentNode;
	const value = cell.innerText;
	var order_id = row.dataset['order_id'];
	var type = cell.dataset['type'];
	if (value == '--'){}
	if (isNaN(value) || value == '') 
	{
		cell.innerHTML = `${value} <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>`
		var response = await callAjax('/update_client_order_aj/', {'order_id' : order_id, 'value' : null, 'type' : type});
		cell.innerText = response['value'];
		showToastMsg('Error', 'Please enter a valid number.', 'error');
	} 
	else 
	{
		cell.innerHTML = `${value} <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>`
		var response = await callAjax('/update_client_order_aj/', {'order_id' : order_id, 'value' : value, 'type' : type});

		if (response.status == 1 || response.status == 2){
			cell.innerText = response['value'];
		}
		else{
			cell.innerText = '--';
		}
		showToastMsg('Success', response.msg, 'success');
	}
}

export function rowLevelEditing(data_table, user_type, cellIndexVal)
{
	const editableCells = data_table.cells('[contenteditable]');
	
	editableCells.every(function () {
		this.node().addEventListener('focus', function (event) {
			if (this.textContent.trim() === '--') {
				this.textContent = '';
			}
		});

		if(user_type == 'Analyst')
			this.node().addEventListener("blur", handleCellEditAnalyst);
		else
			this.node().addEventListener("blur", handleCellEditOperator);

		this.node().addEventListener('keydown', function (event) {
			if (event.keyCode === 13) {
				event.preventDefault();
				this.blur();
			}
			else if (event.keyCode === 9) 
			{
				event.preventDefault();
				this.blur();
				const currentCell = event.target;
				const currentRow = currentCell.parentElement;
				var currentCellIndex =currentCell.cellIndex;
				var currentRowIndex = currentRow.rowIndex;
				if (currentCellIndex === cellIndexVal) 
				{
					currentRowIndex++;
					currentCellIndex = 1;
				} else 
				{
					currentCellIndex++;
				}
				$('tr:eq(' + currentRowIndex + ') td:eq(' + currentCellIndex + ')').focus();
			}
			else if (event.keyCode === 8){}//allow backspace
			else if ((!/^[0-9\.]+$/.test(event.key))) 
			{
				event.preventDefault();
			}
			else
			{
				try{
					if (event.target.innerHTML.split('.')[1].length > 1)
					{
						event.preventDefault();
					}
				}catch{}
			}
		});
	});
}

export async function removespace(fields) 
{
	
	try 
	{
		
		for (var field of fields)
		{
			var val = $(`#${field}`).val().trim()
			
			if (val  === "")
			{
				
				$(`#${field}`).addClass("error_class");
				$(`#${field}`).focus();
				
				return false;
			}
			
		}	
		return true;
	} 
	catch (error) 
	{
		log(error);
		return false;
	}
}







