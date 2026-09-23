
function model_cancle(ids,element,number) {
           var cardContainer = document.getElementById("my_model");
    cardContainer.classList.remove("hidden");
                   
        cardContainer.innerHTML = '';
        
  cardContainer.innerHTML = `    <div class="fixed inset-0 bg-[black]/60 z-[999] px-4 overflow-y-auto">
        <div class="flex items-center justify-center min-h-screen">
            <div x-transition x-transition.duration.300 class="panel border-0 p-0 rounded-lg overflow-hidden md:w-full max-w-lg w-[90%] my-8">
                <button type="button" onclick="close_btn()" class="absolute top-4 ltr:right-4 rtl:left-4 text-white-dark hover:text-dark" @click="isDeleteNoteModal = false">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="w-6 h-6">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
                <div class="text-lg font-medium bg-[#fbfbfb] dark:bg-[#121c2c] ltr:pl-5 rtl:pr-5 py-3 ltr:pr-[50px] rtl:pl-[50px]">Number Delete Request</div>
                <div class="p-5 text-center">
                    <div class="text-white bg-danger ring-4 ring-danger/30 p-4 rounded-full w-fit mx-auto">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-7 h-7 mx-auto">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-7 h-7 mx-auto">
                                    <path d="M20.5001 6H3.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"></path>
                                    <path d="M18.8334 8.5L18.3735 15.3991C18.1965 18.054 18.108 19.3815 17.243 20.1907C16.378 21 15.0476 21 12.3868 21H11.6134C8.9526 21 7.6222 21 6.75719 20.1907C5.89218 19.3815 5.80368 18.054 5.62669 15.3991L5.16675 8.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"></path>
                                    <path opacity="0.5" d="M9.5 11L10 16" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"></path>
                                    <path opacity="0.5" d="M14.5 11L14 16" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"></path>
                                    <path opacity="0.5" d="M6.5 6C6.55588 6 6.58382 6 6.60915 5.99936C7.43259 5.97849 8.15902 5.45491 8.43922 4.68032C8.44784 4.65649 8.45667 4.62999 8.47434 4.57697L8.57143 4.28571C8.65431 4.03708 8.69575 3.91276 8.75071 3.8072C8.97001 3.38607 9.37574 3.09364 9.84461 3.01877C9.96213 3 10.0932 3 10.3553 3H13.6447C13.9068 3 14.0379 3 14.1554 3.01877C14.6243 3.09364 15.03 3.38607 15.2493 3.8072C15.3043 3.91276 15.3457 4.03708 15.4286 4.28571L15.5257 4.57697C15.5433 4.62992 15.5522 4.65651 15.5608 4.68032C15.841 5.45491 16.5674 5.97849 17.3909 5.99936C17.4162 6 17.4441 6 17.5 6" stroke="currentColor" stroke-width="1.5"></path>
                                </svg>
                        </svg>
                    </div>
                    <div class="sm:w-3/4 mx-auto mt-5">Are you sure you want to delete this Number +${number}</div>
                    <div class="flex justify-center items-center mt-8">
                        <button type="button" class="btn btn-outline-danger" onclick="close_btn()">Cancel</button>
                        <button type="button" class="btn btn-primary ltr:ml-4 rtl:mr-4" onclick="delete_number('${ids}','${element}')">Delete</button>
                    </div>
                </div>
            </div>
        </div>
    </div>`;       

}
function close_btn() {
    var modals = document.getElementById("my_model");
    modals.classList.add("hidden");
}

function delete_number(order_id, element) {
    var modals = document.getElementById("my_model");
    modals.classList.add("hidden");
    
    var order_ids = order_id;
    var elements = element;
            var token = $("#token").val();
            var params = { token: token, order_id: order_id };

            $("#" + elements).prop("disabled", true).html('<span class="animate-spin border-2 border-danger border-l-transparent rounded-full w-4 h-4 ltr:mr-1 rtl:ml-1 inline-block align-middle"></span>Cancel');
            $.ajax({
                type: "GET",
                url: "api/service/cancelNumber",
                data: params,
                error: function (e) {
                    console.log(e);
                    Toastify({
                        text: "An error occurred.",
                        duration: 1000,
                        gravity: "top",
                        position: 'center',
                    }).showToast();
                    $("#" + elements).html("<span class='fa fa-trash-alt' style='margin-right:8px'></span>Cancel");
                    $("#" + elements).prop("disabled", false);
                },
                success: function (data) {
                    $("#" + elements).html("<span class='fa fa-trash-alt' style='margin-right:8px'></span>Cancel");
                    $("#" + elements).prop("disabled", false);
                    var json = JSON.parse(data);
                    if (json.status === "200") {
                        Toastify({
                            text: json.message,
                            duration: 1000,
                            gravity: "top",
                            position: 'center',
                        }).showToast();
                       // Reload the current page
//location.reload();
// Clear all intervals in the array
                     checkOrder();                      
                    } else {
                         Toastify({
                            text: json.message,
                            duration: 1000,
                            gravity: "top",
                            position: 'center',
                        }).showToast();
                        // Reload the current page
//location.reload();
             
                    }
                     user_balance(token);                                       
                }
            });
     
      
}
