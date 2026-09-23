console.log("Hi, From The Function JS");

$(document).ready(function() {
    $(document).on("click", ".buy-button", function() {
        console.log("Seen");

        let id = $(this).attr("data-id")
        
        console.log("This is the id:", id);

        $.ajax({
            url: '/add-to-cart/',
            data: {
                "id": id,
            },
            success: function(response) {
                    $.ajax({
                        type: 'GET',
                        url: '/popup/',
                        success: function(res) {
                                $("#popup").html(res);
                                console.log("Done");
                        }
                    })
            }
        })

        $(document).on("click", "#to_pay", function() {
            console.log("To Pay Button");
            
            let balance = $("#in_balance").val()
            let price = $("#span_bal").text()

            console.log("Balance:", balance);
            console.log("Price:", price);
            
            $.ajax({
                url: '/place-order/',
                data: {
                    "price": price,
                    "balance": balance,
                },
                success: function(res) {
                    if (res.bool === true){
                        console.log("Can Order");
                        
                    }
                    if (res.bool === false){
                        console.log("Can't Order");
                        $("#low_balance").empty()
                        $("#low_balance").append("Low Balance")
                    }
                    if (res.qty === true){
                        console.log("Order Successful");
                        $("#purchased").empty()
                        $("#purchased").append("Account Purchased")

                        // $.ajax({
                        //     url: '/order-email/',
                        // })
                    }
                }
            })
        })
        
    })

    $(document).on("click", ".view_log", function() {
        console.log("View Log");

        let id = $(this).attr("data-log")
        
        console.log("This is the id:", id);

        $.ajax({
            url: '/check-log/',
            data: {
                "id": id,
            },
            success: function(response) {
                    $.ajax({
                        type: 'GET',
                        url: '/view-log/',
                        success: function(res) {
                                $("#popup").html(res);
                                console.log("Done");
                        }
                    })
            }
        })
    })

    $(document).on("click", "#contact_form_submit", function() {
        console.log("Contact Form");

        let name = $("#c-name").val()
        let email = $("#c-email").val()
        let subject = $("#c-subject").val()
        let message = $("#c-message").val()

        console.log(name);
        console.log(email);
        console.log(subject);
        console.log(message);

        $.ajax({
            url: '/contact-form/',
            data: {
                "name": name,
                "email": email,
                "subject": subject,
                "message": message,
            },
            success: function(res){
                if (res.bool === true) {
                    console.log("Form Submitted");
                    $("#contact_js_details").empty
                    $("#contact_js_details").append("Form Submitted Successfully")
                }
                if (res.bool === false) {
                    console.log("Form Field Not Complete");
                    $("#contact_js_details").empty
                    $("#contact_js_details").append("Error, kindly fill all the fields")
                }
            }
        })
    })

    $(document).on("click", "#flu_paynow", function() {
        console.log("Flutterwave Click");

        let amount = $("#dep_amount").val()

        console.log("This is the amount to pass:", amount);
        

        $.ajax({
            url: '/deposit-amount/',
            data: {
                "amount": amount,
            }
        })
        
    })

    // $.ajax({
    //     type: 'GET',
    //     url: '/popup/',
    //     success: function(res) {
    //         if (res.bool === true){
    //             $("#popup").empty();
    //             $("#popup").html(res);
    //         };
    //         if (res.bool === false){
    //             console.log("Error");
                
    //         };
    //     }
    // })
})