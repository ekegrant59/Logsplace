import { toast } from 'https://cdn.skypack.dev/wc-toast';

var options1 = {
    searchable: true,
    placeholder: 'Select Service'
};
var op = NiceSelect.bind(document.getElementById("service-id"), options1);

var options2 = {
    searchable: true,
    placeholder: 'Select Server'
};
var op1 = NiceSelect.bind(document.getElementById("server-id"), options2);

function bindServiceChangeListener() {
    const serviceSelect = document.querySelector('#service-id');
    if (!serviceSelect) return;

    serviceSelect.addEventListener('change', function () {
        const selected = this.options[this.selectedIndex];
        const count = selected.getAttribute('data-total-count') || 0;
        document.getElementById('count-display').textContent = count;
    });
}

function updateActiveNumberDisplay(numberData) {
    const cardContainer = document.getElementById('card-container');
    if (!cardContainer) return;

    cardContainer.innerHTML = `
        <div class="panel">
            <center><img src="https://cdn-icons-png.flaticon.com/512/3502/3502688.png" height="100" width="100"></center>
            <div class="flex flex-col items-center justify-center mt-2">
                <h5 class="font-bold text-lg dark:text-white-light">Active Number</h5>
                <p class="text-gray-600 dark:text-gray-300 mt-2">${numberData.number || 'Your new number'}</p>
                <p class="text-gray-600 dark:text-gray-300">Service: ${numberData.service_name}</p>
                <p class="text-gray-600 dark:text-gray-300">Server: ${numberData.server}</p>
                <p class="text-gray-600 dark:text-gray-300">Price: ₦${numberData.service_price}</p>
                <div class="mt-3">
                    <button class="btn btn-primary">Manage Number</button>
                </div>
            </div>
        </div>
    `;
}

$(document).ready(function () {
    $('#sjjjerver-id').change(function () {
        const serverVal = $(this).val();
        const token = $("#token").val();
        $("#service-id").empty().append("<option selected disabled>Loading...</option>");

        if (!serverVal) {
            $("#service-id").append("<option value=''>Select Service</option>");
            if (op && op.update) {
                op.update();
                bindServiceChangeListener();
            }
            return;
        }

        $.ajax({
            type: "GET",
            url: "api/service/getService",
            data: { token, server: serverVal },
            dataType: "json",
            success: function (data) {
                $("#service-id").empty();

                if (data && data.length > 0) {
                    $("#service-id").append("<option selected disabled>Select Service</option>");

                    data.forEach(service => {
                        $("#service-id").append(
                            `<option value="${service['project_code']}" data-price="${service['new_cost']}" data-name="${service['project_name']}" data-total-count="${service['total_count']}">
                                ${service['project_name']} - ₦${service['new_cost']}
                            </option>`
                        );
                    });

                    if (op && op.update) {
                        op.update();
                        bindServiceChangeListener();
                    }
                } else {
                    $("#service-id").append("<option disabled>No services available</option>");
                    if (op && op.update) op.update();
                }
            },
            error: function (e) {
                console.error("Service fetch error:", e);
                toast.error("Could not fetch services.");
            }
        });
    });

    $("#buy-numbers").click(function () {
        const server = $("#server-id").val();
        const key = $("#service-id").val();
        const service_price = $("#service-id option:selected").data("price");
        const service_name = $("#service-id option:selected").data("name");
        const token = $("#token").val();

        if (!server || !key) {
            toast.error('Select both server and service');
            return;
        }

        $('#buy-numbers').prop("disabled", true).html(`
            <span class="animate-spin border-2 border-white border-l-transparent rounded-full w-4 h-4 ltr:mr-1 rtl:ml-1 inline-block align-middle"></span> Finding Number...
        `);

        $.ajax({
            type: "GET",
            url: "/order-s2/",
            data: { key },
            dataType: "json",
            success: function (data) {
                $('#buy-numbers').html("<span class='fa fa-cart-plus' style='margin-right: 8px;'></span>Buy Number").prop("disabled", false);

                if (data.bool === true) {
                    // toast.success(data.message);
                    toast.success("Purchase Successful");
                    window.location.reload()
                    checkOrder(); // your custom function
                    
                    // Update the service count
                    const selected = document.querySelector('#service-id option:selected');
                    if (selected) {
                        const currentCount = parseInt(selected.getAttribute('data-total-count')) || 0;
                        selected.setAttribute('data-total-count', currentCount - 1);
                        document.getElementById('count-display').textContent = currentCount - 1;
                        if (op && op.update) op.update();
                    }
                    
                    // Update the UI with the new number
                    updateActiveNumberDisplay({
                        number: data.number,
                        service_name: service_name,
                        server: $("#server-id option:selected").text(),
                        service_price: service_price
                    });
                    
                } else {
                    toast.error(data.message);
                }
            },
            error: function (e) {
                console.error("Buy number failed:", e);
                toast.error("Something went wrong. Try again.");
                $('#buy-numbers').html("<span class='fa fa-cart-plus' style='margin-right: 8px;'></span>Buy Number").prop("disabled", false);
            }
        });
    });
    
    $("#check_price").click(function () {
        const server = $("#server-id").val();
        const service = $("#service-id").val();
        const service_price = $("#service-id option:selected").data("price");
        const service_name = $("#service-id option:selected").data("name");
        const token = $("#token").val();

        if (!server || !service) {
            toast.error('Select both server and service');
            return;
        }

        $('#check_price').prop("disabled", true).html(`
            <span class="animate-spin border-2 border-white border-l-transparent rounded-full w-4 h-4 ltr:mr-1 rtl:ml-1 inline-block align-middle"></span> Getting Price...
        `);

        $.ajax({
            type: "GET",
            url: "api/service/check.php",
            data: { server, service, token, service_price, service_name },
            dataType: "json",
            success: function (data) {
                // $('#check_price').html("<span class='fa fa-cart-plus' style='margin-right: 8px;'></span>Buy Number").prop("disabled", false);

                if (data.status === "200") {
                    toast.success(`Price: ${data.price}`);
                    toast.success(`Stock: ${data.stock}`);
                    // toast.success(data.stock);
                    $('#check_price').hide()
                    $("#cbuy-numbers").show()
                    $("#price-display").text(data.price)
                    $("#count-display").text(data.stock)
                    
                    
                } else {
                    toast.error("Unable to retrieve price");
                }
            },
            error: function (e) {
                console.error("Buy number failed:", e);
                toast.error("Something went wrong. Try again.");
                // $('#buy-numbers').html("<span class='fa fa-cart-plus' style='margin-right: 8px;'></span>Buy Number").prop("disabled", false);
            }
        });
    });
    
    $("#cbuy-numbers").click(function () {
        const server = $("#server-id").val();
        const service = $("#service-id").val();
        const service_price = $("#price-display").text();
        const service_name = $("#service-id option:selected").text();
        const token = $("#token").val();

        if (!server || !service) {
            toast.error('Select both server and service');
            return;
        }

        $('#cbuy-numbers').prop("disabled", true).html(`
            <span class="animate-spin border-2 border-white border-l-transparent rounded-full w-4 h-4 ltr:mr-1 rtl:ml-1 inline-block align-middle"></span> Finding Number...
        `);

        $.ajax({
            type: "GET",
            url: "api/service/cbuynumber.php",
            data: { server, service, token, service_price, service_name },
            dataType: "json",
            success: function (data) {
                $('#cbuy-numbers').html("<span class='fa fa-cart-plus' style='margin-right: 8px;'></span>Buy Number").prop("disabled", false);

                if (data.status === "200") {
                    toast.success(data.message);
                    checkOrder(); // your custom function
                    
                    // Update the service count
                    const selected = document.querySelector('#service-id option:selected');
                    if (selected) {
                        const currentCount = parseInt(selected.getAttribute('data-total-count')) || 0;
                        selected.setAttribute('data-total-count', currentCount - 1);
                        document.getElementById('count-display').textContent = currentCount - 1;
                        if (op && op.update) op.update();
                    }
                    
                    // Update the UI with the new number
                    updateActiveNumberDisplay({
                        number: data.number,
                        service_name: service_name,
                        server: $("#server-id option:selected").text(),
                        service_price: service_price
                    });
                    
                } else {
                    toast.error(data.message);
                }
            },
            error: function (e) {
                console.error("Buy number failed:", e);
                toast.error("Something went wrong. Try again.");
                $('#cbuy-numbers').html("<span class='fa fa-cart-plus' style='margin-right: 8px;'></span>Buy Number").prop("disabled", false);
            }
        });
    });
});

var settime = 0;