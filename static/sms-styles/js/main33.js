function copyToClipboard(text) {
    // Convert to string and ensure it's not null or undefined
    text = String(text);
    if (!text) {
        return;
    }

    // Extract the first two characters
    var copy = text.slice(2, 12);

    // Create a textarea element to hold the text
    var textarea = document.createElement("textarea");
    textarea.textContent = copy;

    // Make the textarea invisible
    textarea.style.position = "absolute";
    textarea.style.left = "-9999px";

    // Add the textarea to the document
    document.body.appendChild(textarea);

    // Select and copy the text
    textarea.select();
    document.execCommand("copy");

    // Remove the textarea from the document
    document.body.removeChild(textarea);

    // Show toast message
    Toastify({
        text: "Copied: " + copy,
        duration: 1000,
        gravity: "top",
        position: 'center',
    }).showToast();
}


function user_balance(token){
     //       var token = $("#token").val();
            var params = { token: token};

             $.ajax({
                type: "POST",
                url: "api/auth/session",
                data: params,
                error: function (e) {
                    console.log(e);
                    },
                success: function (data) {
                    var json = JSON.parse(data);
                   // Get a reference to the <span> element by its ID
var spanElement = document.getElementById("current_balance");
var spanElement2 = document.getElementById("popup_balance");

// Set the data (text) you want to display in the <span>
spanElement.textContent = json.balance;
spanElement2.textContent = json.balance;
 
                }
            });
}
  function countdownTimer(milliseconds, elementId) {
    // Convert milliseconds to minutes
    const totalMinutes = Math.floor(milliseconds / 60000);
    const element = document.getElementById(elementId);

    if (element) {
  //    element.textContent = `${totalMinutes}`;
                  $(element).empty().append('<i class="fa fa-clock"></i> 00:00');
      // Create a countdown interval
      const countdown = setInterval(() => {
        milliseconds -= 1000; // Decrease by one second (1000 milliseconds)

        if (milliseconds >= 0) {
const remainingMinutes = String(Math.floor(milliseconds / 60000)).padStart(2, '0');
const remainingSeconds = String(Math.floor((milliseconds % 60000) / 1000)).padStart(2, '0');
      //    element.textContent = `${remainingMinutes}:${remainingSeconds}`;
                  $(element).empty().append('<i class="fa fa-clock"></i> ' + remainingMinutes + ":" + remainingSeconds + '');
        } else {
          clearInterval(countdown); // Stop the countdown when time expires
          element.textContent = "Number Expired!";
        }
      }, 1000); // Update every second (1000 milliseconds)
    }
  }
  
  
      const synth = window.speechSynthesis;

 function playTextToSpeech(text) {
  const voice = new SpeechSynthesisUtterance(text);
  voice.lang = "en-US";
  voice.volume = 1;
  voice.rate = 1;  // Set the speech rate to 0.7
  voice.pitch = 1; // Can be 0, 1, or 2
  synth.speak(voice);
}

function getsms(elementId, order_id, token) {
  const element = document.getElementById(elementId);

  if (element) {
    // Create a unique interval identifier
    let smsInterval = "interval_" + elementId;

    smsInterval = setInterval(() => {
      var params = {
        order_id: order_id,
        token: token,
      };

      $.ajax({
        type: "GET",
        url: "api/service/getMessage",
        data: params,
        error: function (e) {
          console.log(e);
          $("#" + elementId).text(e); // Use .text() to set the text content
        },
        success: function (data) {
          var json = JSON.parse(data);
          if (json.status === "200") {
                      $("#" + elementId).text(json.sms);

             var audio = new Audio('/notification.mp3');
            audio.play();

            // Play speech 5 times
            for (var i = 0; i < 5; i++) {
              playTextToSpeech(json.sms);
            }

            // Optionally, clear the interval if you want to stop fetching after a successful request
            clearInterval(smsInterval); // This stops the interval after the first successful SMS fetch
          } else {
            $("#" + elementId).text(json.message);
          }
        }
      });
    }, 2000); // Update every 2 seconds (2000 milliseconds)
  }
}

function cancel(order_id, element, number) {
    var order_ids = order_id;
    var elements = element;
    Notiflix.Confirm.show(
        'Number Cancel Request',
        'Do you Really Cancel This Number: +' + number,
        'Yes',
        'No',
        function okCb() {
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
        },
        function cancelCb() {
            
        },
        {} // You can add additional options here if needed
    );
}

function buy(order_id,element){
  Toastify({
  text: "This Feature Not Active Yet",
  duration: 1000,
  gravity: "top",
  position: 'center',
}).showToast();
}
function getImageUrlBasedOnDigits(inputString) {
  const firstTwoDigits = inputString.substring(0, 2);

  if (firstTwoDigits === "91") {
    return "data:image/png;base64,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";
  } else if (firstTwoDigits === "84") {
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAACXBIWXMAAAsTAAALEwEAmpwYAAADO0lEQVR4nO1ZzWsTURBf1Hrw6MfJj3NJ2ZltN0nT5hBF8ODZ4Ne/YA9FQamCntpePNmSqnjw4kGxHrSiiBQP3sSS9za2BUXStIG0aUWqkortk9l8qLUx+/F2N0IGfoewyc7v997MvHkTRWlZy1rm2u4nk9tZZ2cPV9UBhviQAWQ44goH+G4CcYUBGPSMvpNW1ZhQlG1K0MY7Og5ygGEOMM8RhU3kOOJQWlUP+E78rabt4wA3GeKaA+J/gJXfkZrR9b2+kE9r2hmGuOyW+F9CAIoc4JRnxN/oehtDvC2bON8MgDHyJZv8Lo741HPyWBMxQT5lkW/zlTzWRLwwQqGdrgX4EjZYFym35M8GSF5UduKkI/Lv2tv3MICloAUwxGVHJZbqfNDkeVUEwKgt8nQ6yjikJO7CmqHrh+ys/rAMxzNHNROShAxZIk9NVqVPce00fy0s8lfDcgQAzFPT2FCA2VVK2vovL2MmZL3PQIw2Dh9VHZDhbPqwJjYKcSEKcTF9pFOKAAZwyUr8j8twtnAlLMRS3MTCZTlhxBAfNA4hAEOGs9XnsZqA1WfSwog1FmCzVZ7r08WPj701slaxnu0VuQv2doYOVisCbNf/2WOa+PqqxzL5b697xOxx+3nBEEueCCAYXSgK1yNm0tYlvxgXxVtRYYQd50BJeghtRvacXlcAPXPzbmYphFwmca6/voC5/rD3ScxdltHP4901whv5Mqqf6ZnnZZS7OMgyURTruXJFWjN6xYfTXeL9iS5Rmion+Pp8XGS6nfdGDPFiQwE0dHIc/33l8Pl0LyoysV9EMxE0k9d1HmhaxFIzxxDnnDhYudstcuf1fwpcvhN1tvoAWcvTPGpdnTiZTmhSvsO3xqAl8k16oSlNIe63LKCyC6mgifMqAG4ods0IhXY3xaUeoOh4bkqzysAFaFrSEfnfRIwFuPojilujeygHeBRA3D+ZTCR2KNKGuwATvq084mNpw91NQ96UH2EzKWvltzKaVXpSnQAWXSeszbnpKB0wEsKlRHWeyrbit9HpSG2Hk96p8ptB2yesF0ZNFg2daG5DPTtdPOhmR+1IBXTLS9Mzaompq2yKv1lb1jLl/7efUJhWdqcQueQAAAAASUVORK5CYII=";
   } else if (firstTwoDigits === "97") {
   return "data:image/png;base64,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";
     } else if (firstTwoDigits === "20") {
     return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAfQAAAH0CAMAAAD8CC+4AAACvlBMVEUAAACGCxgAAADOESYAAADOESbOESbOESYAAAAAAADOESYAAADOESbOESYAAADOESbOESbOESbOESYAAAAAAAAAAADOESYAAADOESYAAADOESYAAAAAAADOESb////OESYAAADOESYAAAAAAADOESYAAAAAAAAAAADOESYAAAAAAADOESbOESbOESbOESYAAAAAAAAAAAAAAAD///8AAAD///////////8AAADOESb///8AAAD////OESYAAADOESbOESbOESbOESbOECUAAAD////////////////////OECUAAAAAAADOESb///////////////8AAAD///////////////////8AAAD////////////////////////////////////////OESb///////8AAAD///////////////////9mZmbbTl5paWneXWz///8AAADOESbAkwC9jgBhYWHMBhzbTl6/kgC8jQC+jwC+kAD///3DmAz+/vvv5L3MpzDWuVnClgj9+/T9/PbQrkDNqDPGnRn48+H69ujYu1/+/fn17dXIoSHVtlTu4bjOqzjavmb38t7y6Mnt4LTn1ZvSsknLpi3Emg/z6szHnx3279nq26nm05ffx3vUtVHBlQXRr0Pw5cDo16HgyX/8+fHhzIbRsEbIoB7PrDv+/Pj7+O/NqjXJoyW7igD07NLdxXXcwm/XulzTs0zFmxLl0pTZvWPJoiPx58bp2qbjzovexnjGnBX58+PdxHLKpCfizYnhy4PbwWzLpSv69urs37Hj0I7PrT3KpSnv47vHnhr38Nvn1p7IoCT7+O379+z59eXw5cLk0ZHr3a38+vLz687JoinAkwi6iQDawGr27tfUtE7VuFbp2KO5hwD069Dx5sS4hQDr3a/DmBTBlALClg/NqDnFmhjq3KvaTFwRIFLEAAAAcHRSTlMAA/juysD0CQ3XyQj528CwYyNS3hXs5a09Hx3y0TXumWRHMibQt2vioKCAeBAXt4lIPDf9VgT34JWBYlw1LubUqZGIWyz61cnAuG1PQycb0bCKcSb0qJN/dy0LCNtTSeR1bj8rIumQn2damRXJwrWuCSYeZQAAL/5JREFUeNrs3UnKo0AUB/AnYgmiOCxEBBHBhWDiPovgtAvkFLlB3X/RNN1NT8kXk1haw/93haJevSmG9Oce43NWRe00NkPYOV4fpKn9U5oGved04dCMUxtV2Tk+ugTKcvNbNp/KwQlsxhfz7cAZyinKzjlOXyFWXiSnsgtsn3+CBV0zzUWMs5dcXkRj2DO+IhaEY1TkFoF0rDiLxppxQVg9RhUuvUTyrB16xoXzg+GU5QQ7s+JkdGy+IeaV8xXBfjfXuax9vgO/byIc/PbcqvR8viO/LpMDwVbcou0CLoG0OxVI7jZwTEopDvyXoEmQ2wmVR4PNpWOHUUwgRBx1jEuKORec++pyiU/8Bx/nvqpDImNU/x8L5yPBCqysTLky7KZCPv+puK25YvrTleB9VSj5Q36f3yXo170nPnlcWfWE6/4yqxqUvOS/+WGF6/6KQ6TwJf+tviCZXx7XpWq0fiJFlF/kVipRky/FmoLga0Wj+FN+R1cRPJaFXEsOSrhHEodry5tx7IYdOY79rkrzI//OSwh+yzpuBAcp3S+FpunbPV1GQBSXPjdJcyPTHU5atWKWYKPZzVkr0qbh+or0YvCihQkp+321qYl83HCDhUY+7ZFxj/nf2MW4Zo25kd3YZk1udGT/bTBoUz5SaKdZLNuUGH8zpOe6jGPCjoXVGp7A/cs/aV+0n5HA/cfTux9vtfotQ+Gyf+2Ga/6Ap+3LfsFr/hBrtUzjc4Om5u/oNKzZE9TmT9gz6cUdOTxVavWNsrMWP00Tr9YonzN9oLYcu5Ae3JLDYoMWIf6G0P6SXoMQnyC0v4hFpLgTh5eNSndlj2jIvMVR+HOzRc/hLYGygzc85+Y97C2HD0wKTmBc7D5+KFSuYs8xOv+Yp9jc7Wzkb9TWliqVzlWYo66CKfRziNmsX5yLpMwABmn7iiZSwsRhRaUCpZuFUm1lofSdeBfd9tU5khfsB5TnAnhSf6TmiIUJIXqJ2zS5cn+yo4pA2s/GH3HmwgSS3nXE9j8Ycuox7rlQwZmkE2PEIlgq3Zos3vP/aH/qeM+3kEoV4VGrbSOVqHJDbP+Cpjn8AbF9M70kG/Eu+u0b8qSYvliYq23KkWHSivn5xsL9tyqwJ7O5ht6AfTjFTbSrmcNSuuzIVth13kdCuznjZ6k7YRnt5IjB2m7SmJZDU0YT9YEWQoGuj4XlOoo1rYy0uYTDziJ6Dom7ZvyMnkHirp00p2cwWdPOgokbvgOpnZK+giROTxFt5IokThqsoE24WImTSHCgLeCb/VIZ6AGM0DV2IeFueNAlc7dHgwddc8Kfdfy/moQa+hcqdP3NJFCOb75Kyb6SOGi5S8qxSJQLB0m1JMiVcZCUX5AQFhYhJVa79CcsxRlhIgHOCO5S+9GYQ3A3S+8SIbibZiJC5m6a1TP4joP0PIvWFHFQQEsrOqLnrgQWExF+q2iYkFZTcVBEQmvBtowyggOyOPN8Y+f+XpqMwjiAHxEbxCTbhcjAJPAu87ILaViIWEFhJIQVIlQQRfSw96XO2doEIy1RQxaG2fwRjhJjKGGlQbGbUYnT2MW8CHUXI/ovsgIN3NbWdvOe5/u5eP+Dc97n13mKlKw7MQppIXaXKIZjbrCQelEEVW6wFIcoWAmiOIsptyGK46fgulwdanGWU+rE+gF+apCu8WN34VkyPwWV4F3Y8mxNVXjRwk8Z6jIMOcT/wgCsZdWWoI3OTxMOOj+NNhx0firQaeGn0YaDzk8F/uj81JYgR+fHgWIcP3tFnqrdYHkH8aaFn3qRl9Nor+mgGn10fvLqqzuxgkAL9suYjOOnBiOw/JQexqw7P4fQauGn3IYKLD8OPFPlp0zkZD/yNY3YXcjX+DkuclHrBo1U1mFihp8KNNL5KcshjEN/TTP2aqz45uefoZyt0Q2aqbShGsePA9MT/OxDU5WfPU6RTdNt0NApkc2tH3dAPzdFFmfaCDR05JzIrIFAS50is5MEWmrB7U601L/qJ0aa20Um10hvocdT78fmny/dm0tM+D4NTm2GiItOrrf7yPJaMrke9nYPGFJKj6nk06GvxEML09vd36Mmp6JDvUp6DcPwmFsfr/K+GCEOmtt5xu4jvs2NxWD/wyFTGoacHjZ+kSr1mTjIdL+3ktYWx+OJsJKTgYWUkt0z5DOVaXo8a70xYuCESOvGAdLa3LQvbErDTARHxxOq74NcfhOMdz2KpiLEQNsVkU4H6S2yPjH8rdc0pBqj/nkz+SpEvz37yCJ7axDpXCe9vesJEK0OKkOqRaKFuVH6I/ZlgxhoFWlcvER6W4nRFv+4aUjZRX+5HyQGrl4Qux0lHmbeer3hgRDt6JslDjrEbueJiah6+SQ1e5e2RV4TB2f5leN2BL4/8K8E/LQt3kMc/CTvzJoaK8IwzC/xT1hKleWtOt44WpZaLqOOZZV691alL85JDiGQfSOBQCALMIQlbBkmbAECBAiBsIQdHGAoUszmz/D06UQmEMbMZZ88N9M1kJOL93T3973f1839Mlt6LaqEUOwIJWy0S6gCyhTVf34fVYJ90IYS9turImcrk7R9i2rBHmxBCTPpYVQD39zU/IP7qBZa3Kt4g+oRvfaDmlK+/gTVwlisHyXstztRDbz/cU0pf6Fq2E/rUUJ9dQRywMMq82DfoG0IqF9A0je8xcT2GFAdfFm1WzqmV6BPZODeGDM4EbZVkei1P5aI/nv1bOnUal8I7pncZ8dZJ7LhKlreb2zqD1A1jAQDmElJe4M7l1kTetoAX9qE6uDPKs3SsZ9wonMIrphzLGtE0wDgSlRLV2xppn4PVUOyGxhfRD6NS1n05hVq0bWgOvj0g+rpgy3B0gZ4t5ExwBXrx1wPoM96UB2U2O+/oWo4m7fDHgxhwC+LPgIPDeKiVdFFQXlQc82vUAH6kG8m0KLH20n6gUhKj+lFhBI7uIwZgek43oZkO57xnanCqv2u5ppvwD1bpyfubDrlTp0fnOFujMFWINkEnK+hJbGL3UEXsO3Fndh6n6WDqXQ6l3OMgXvuvWHNfAreOXj+LLNqGjbaW5fXN4c6d3AHbSkJGOoELGEsuPcA7wUw5j5CWUxh/6YlebVgHB7e8Tie94F3an9UkTWz/HwD/2FbswQXbSiHM7YN7Fm3sBo8w+pgCGjoAkyJepRhZ+nkpMuF//BZ4+Cc9z9WTxwXaTxGCRv+13E7btMZ0wO9BiCQMOEoEQAO1gF0J3EL40DwVdiJN2mpC4Nz/lLNITa9ZQA3yUetBxJucGSlqkX7gO3RQqp2PHjEXoMbbOcsmdv/Oci7d3fdHfkV+CZiNeI2rSeGK5TyxAvANhkCHHEAo2G6tHsA+6YLJdS/ym3jNvoY71P9nmpKbM0OlMO0FHw1a8Q1Y8oukOwBJMMsoBjvaFgBcP4E1zivzK+7jlCOJ93gm9of1eLHeXsB5JdMKEUJxXKnkX4UsMQBrE7WAyGrHUD3EgDP4DDg2TSBYZyJn+T67LiJfq0ewH6K8yabD79WydmW3eAW8n7t/HAZQfSt4zm3f/HQF9obWXabAKnpHEDfBGQWT0ED+l5Abxjot28FMsmJXK7pn2HcwomsaN6AfXAPfPNAJXGcK7t1KhBtGmfNw7iNKT/XYEglcu4XASBjeWkHfH/PQSb+sgXAdnABiGhibnfK0LRUb8RtpPgMegjRjYfSvN9X8lAlddXLSasoaLQGnBH/Dspj2glZ10wXr2LtfqBt0mHdAJY2Ha8vALQ/H/8ndB5z7RpRHmPD03r4iUYjzj9vBd/8oZIbKALKJTLEizHNY0sI5ZHGdU3u9JJx/GCk4XUr2hp9bXU+XATXD42dwUVDbPOpA3ewsC6SVnQTelsJyYBvPlOJCTsjaGTIOnyChlj3UZbIesNyRII+68hNLACY+rsuD2Cn7yRhCQIjgasIyhNKixpyiAaifAvvOVvtD+oI3iM6RY4o8rL62pdhCWWQoDCmPZmFwkAvFJz5g1kJd7NvldUms5gWlW/pBd8UwvePeT/F1srmYBM2tPTfTSPuJt9pwrsxSsUm2zhlonNfev9ZHU2Rs4ro4jTCdKBLVCZraA4VMUSo1lNYVEQXD8A5f6rjNoJOJvoTNtCm9Qhf4v/YSLxM4v+wzwI9hD58Dkkm+hI4h7nvf4BzBpgcy2ygNUhYeb6Pt7LlCGb614cCeCuhkwmgibCHL7Nv4f7+sc/VcQVFV2EOsgHxAvGnjdu4G58jF++PzOnncuNvk91jfdoNFsCJSRywb+H+fpr7qsjYrndbZUDWgWZRIIsmlMU2ZT7pstvj3c3doZGuk+jFLsqin/pbS/yFp4vN6CUaNuCc2h/UkLFhpRBXswGJAg558NiD24yt+U+6r/S2ZLRTQms0bhu+6Ek3zdpwm4VHWg0xA33KQ58hU8wROOdDenXk97xnbNcZtDxgsjyTBdLWw3Yl4T9MYxeO0XTD7MhRq2OizQgZ5/bEdMS5NxU9McdbtyRc0+rC7qRs7VokLLE36doN4J3f1NArhfGiV9ZAWOqGc3kg+DBDXs2GPL5Ln2eq2W9on1gLSMb8qT9ejyJSa/N535ne6Okyp0e7Vzo3fJcBz9iV+fE/GLHKoseG2V5Ohq59P975SwU1NqCJiZ5BNymEWlGiER65ZJ2Itq5j1Dtknl46bJGMoammeXHpCCXYvSQ2HbY59a7wwLh5yDs62SgQEoZxUKcRrP0sDySjCAgaNuCdh2pI0zGhiK71wF/IrjCk1Qh1NmVFfjzttK3u7rlmF/3zgkgEbR43GBd1InmRa+q6OtvbXbXrFx8re4UpIYvescoCOK0BYy8EZcD9seavVHEHRVQRXbcPM2Gpm9Quiz65qvizYnN/cLJDnrwioaLRrb4UtikIOvoLjR2Tg0dJUYkKnVn65iwgrIieReiRInqa++vHvlTF6RZ5XlMuYaEDcgCTm67MI8okJdP9dVpB0DDuFJ0hCNrGkSei8hDJIIve2IIM83YlW6NABzHujzd9poZTynRea2R9tqSUInobRuYFjS54hCkqerexg6pVgegUocN0KjK31UIDgzN4tFTroNNep4g+aATnyOeVP+D+xm95XlO16laHN3UsdbPLMuvcJsU5JWZnUPcOolslBykEBrLoLy5ZqibMG3fou6MsIJzzyw8q+CMe8rxmsowospAwbHWy6CmnUiPRjkoWbeWi6xI4JywFMLO875gtALtG9jWTu+Cc976o+f1DcI6dTcHNYbYAazPYkrdfbbukOKi6FPykQtFZdO7VsmR/goq+rzyMbu5SYUGxgXPe/1gFhtwC22zdNNRiqZvrETXTgFORrgDO8XcQnfSYrAKz9ejHtBv0nWJhIgsdHrnAOz9z3/QOtLCwOkWTKpa6HWsEDfEW/dmWpFi56OLKaqNAtWevDDmkuwd7KksSBB9454EK/kbTGUug2+FS7BM59vJR2cwFOUl977uI3hkSmO2KLlFJBY42C+tHlBQ+zzsfqcCFLVhlFgQElrphXyfL5UfBlt0ee4eUjXjCYsFtXWapG0sOyFXR+OO98R14qILrZgqmuBd5RfQOOzw0P28Ai+BertgbhcpEZ5tB0W2do6J3wZlSRA8XLf5D8M533B9TBvLF8le9VkndRpROSfGUtbfpoj2mlK5S0XWDUpNBYG7rFEvdmPdDtovFvFnwzrfcn2lCsdDtx6FiohecODEJjMpykUVvfwOpVHTS0z/0RMdaatsIjetQMHc70SxqmPq88w3/bZHFlpYGbNMBdeIGRMVT02ep6G3nGwdipaKLAy7zBWFuay9h+bqX0B+sYUUlje/4XAX1lkLz2qmyCStOXBcLwWhFXEPCyT6XUPFMj6yt5AlzW2l5jYyjULsbgFyIYerzzj3uTy+i2KaaZN1sRSeOHNCGJxp2R8xGa6VVtknTefhYx9zWDGEmzYQiehd9lZj6vPMZ/w3QSmp1PRWLThzpZF4ayRyl+p+RykQnPcas/Vhgbistr5EJsABOXCm21/N/mdx9/iurxaMnc1gptr07qOi9tO6i5NXRq9kKRRc78xbq5ylua0THnDn22IbiQRru75LDpzWfgXdY2zuZYq5r0YkjYVoqUURuGqfWaiWiP7KtWKhzr7itAfrpURSOUPgRZqI7wDs/1XB/1KF4nLSNrcPknDlxJFNQL4DuDn2UVCI68UqDlsK7soEzWqvLOtmyTtbpcs+ezzu1Ndz3UMDBRL8onDpzMCdO28rW6cYzdD/dv6hIdPFf7s6sJ7UriuN+kn6JpmnS9LXTS5umUzq3D03at3/ieTiH6aKAIggCMggoFEQBZ8F5REUmJ0St1dr5tr0fo2fvtU9sm06v219ywzUEXv6cvdde67/WXp7XZrBNu4L+Sv6bGu0aLLlLK4nsfNwl/726JJryRITZi3TIMmUxzCOyAUS/9lxa1f8WXe2tLn5tR5XHfxc4XVJ5FE+9sH3s66gUIzufdX0G2UmT6GHRVJwDt8qocZwz0bcmkNFGHB7tv0VX0t5+pQF+wFPWMaG/qiNtHFMDNK66H4jx/bMu6d1SwhhjamLGREe3qVkTD7+bJuZodGBG0SJX5v8hevaJYp612WZNLNtK3Q7WENbJDquHCA/E+P7UAxA9w0VT19DgotdYQxI/aD9RmFhey4HJFENA+S/RTTEUFXPBiT4m+hics2YeElxw0Qu2IzLmNCSfGfkwRJ/hUfXjQRtzvVJShjbjiMI0skz5zPoOf/ifomvjV9TI5FL4b8fWYAvGPMIm7oKdErasVdkHQT8E0W0Nsr27HUsqVcGYOix5vqHxfqSJLZUlWXZN/yI6VVXTCq/MlhW+S1jsFBpQxXZpokqiJy4hOQ9AdLb1Mu/E9Bk5oNfZQZuXyXIaP2pRNB5f1/5ddC2S5NF+G2kmegqYUdiuQVG7at2+fCjG9wcg+tkS2d6dtPwqP7GIi6/CvD+pzh/8L/15xEz/LDoZ3ktWfcVIoiQK6UUWE2RFjufxrbefjO9VSM4DEJ0syuYEBVpGUsbUsGGRiR5lblk1MW0fGlL+TXTtYm13OqYvGlcIapTjcVFiz21VyQU7a+KPvPTXNT4A0d2G7V0cqR5hWKWTFRNPKTG3rJLGRQN55Z9FV4roO2afMJ/zCotSptEGyrFYSkxN9JHxXfqbup6SPzlzZNjeWUlUJGUoh+KhZXr+S1WLAK5O6Fr9J9FVdXA8ZmGnM9MQbQsuyu9qNZ6k4Y983TgbSs5n8qdhxQMeo4CL9Zk2TVRhvWOi5xBX2WkbkV5HTvsn0bUF7y/7QNuqmg4pACxSTVXLiUhRGb3PAknOZ/IXXK66he09a6YomydlFBeoE7HChpCwLNr51z2IKX8vumkWN9/VAGTY4JGaxr+PXFebmJoVzbDfPBDj+8fyl1aNOgjCCg+uTxFRaE/OM9E7yJr5xL+4L3Exf63+neiqOtxsBMbAXDi6uOMKd12Rv3IRtgNhh717IMb3Z+U3UZyT6C6uFc+oVSiAQ13hWg0pShhA0n7Rmqhpfye6lnO2mpl1AHFVieBQ4f5K6nYIUpKG/Xo8iqjhSs4H8tulmuRtKFPd2+xz0LK8T2Ip4xjVtqYBnBUGUi6Uv87iL/R8l0F5H74fADhW55aRNXMnNQ2y8Bge6AqChltDcl6U3xh5Qc9fCTlNzITZoX4kVmxjZfbI11HoWGJDyOxNtS7wF/w/T9QCljbdw+TRt/Y1lbKtEWGHrYuS7aLhy5Kc1+S3QDNp+JO9SQ5oG0Xdk3TUMoWx8SPJ5BqHZy77fb2KP3HaNxxXyridvYTO+neTiIvuqG9FbJAR5owFw4EpOS/J3+xQIylSWDQc0Csal6Y6Ql63lDYPhn9yxX7c7x7NO/EHvOXxgf5xV3nIboOO25xih0DWB0mngLxhfPc8GOP7S/K3NeUMKYKGA7qk8EV420qu1sWWBYyUqa+Kjs/Z8dsAA0tpz7a7B0fmlyj9bV9h6R7e8Xyobw+mIuAXhssN4+clOa/I38BodBtRcK3UhRk2glAv+ddXPGA4fz2ZBrDYh1yPBQYrC6ivsHeL/F1g5xuW2OWzDYZMtF2Qy9ZlbCQ3kJy35G9VpvDKOEYrUfJPKeNsGgmvlBbHoDNR/zkDRimKzR4biJUd+NNgbF73VaHz0y7tC+YfcG6mTkZjCXlidEpKztvyj4Y1OohRVoQkLup1mGeibznO1DKAaiz9iHbtmuZHyu+Ejre0AI/JA0a6EjzZBuBRQs4tlRstr8QIsX0KFozDYRSS847840eE7X2dimjajWhLP+QdKmrLcpFoDaL9VRpJHp8/sp6no9iIVoHpcg7+fLLFw3HXt/AkjtD2nYxh1cS/MNlLAd0CHQsezPDvT+QfNGQkR1E0UfOqd5ftxUN03PahZ8OzMOArAe2CG9huLcNbzljGi8lQfQzRjBNr1nNmuhoC9vtDG+VI1HBGtq1ksExRAuB+zonkPCf/SDFRBhlCTDigL1tsL85SYu3AcXAVH0ncAJiazQLFAgBL9NfL80DgkbOesQFTS1tnGCgcAUj1L4XbvqkMmeROt1TupKloVLCfN0o7kvOh/MMDRcEzCz4Fyjifq3FegDEFhndtFtciGMVvkfrNtw1g87uvbtvuUOzHIIBHjXIGyVUevOf6bBZ7008muYkWD/+pxUVteZOiiCu78f0j+ceEuhTyTkxxgwudz5lfnRJq+VwPYAOnfPyo99YVAa+g/jyU/U0xH1iAmxWnb3LwwAuGFwhucvfFjiikx7FO5TuHMaVQcuP7089LPxDYIkxMSRoHTOdzXlZf5qJnjmGw0pMYx2YaqOq/D7b28x3bElvH1dJNEQbhIjkjqZCurmGIvHEDA8KYJfnw7zdf7XpfchfF1OyfJFG+ZZ44Xlaf1Nie3nDDIPfjDjBccAqPjUrx322rCnz7XRkGZ/aimY0YokK6CA7uf1ZqS3Lj+8fvST/kf6LFJVm6pMVXecImSLKyOgXdvS7A4DBvA5y+pkjXi2EitTp0gnuAgZ/KdqI2G8aaMN85hdlacuO7PuRf9jJbVbQgTIkwK4y4Som0Hc0oj+S+xz13OzyvSigZ5Cdxzzn7Y8y43m1G4UtHvFuEigkyZLUhNS/Jf3FPW9yyYRyomvhBpbL6via8qys/0mM8ybVft3tj5vuZ/tuFK+is1cAI/rgAJB+rVFMtUuVm3vg5iQaqJKRGv7hH9uR7SLQVso2aRH5k4mM+WYVVVXxeBGOVAHSOqa7e9g3xjxC9KWo93vkxDGAqVitswtZ3beI11Qxd7JHspe2fpfoYV5Ca1+W/jE+s6g38wNfex/O4UKjXoaSYrbESgomBar8bmO/vC4JRPnmsjxTq1f/pr93XC2D4f024gasEkks5BIMlTSkCaRo36jZCxIxxF5jUfCr/tZti7bXz0c/8Tq1jhXod7uZ+eeT/NsUEnzmGc3ayaQejMscCv4LavWRlm/4hdLy7a/sBC/bywLy1li1ic64BeMgO2zYOg1Ej+Sc1X8h/wW5cDAURKZSRKmqiVyHw8/BUI504ArBzB08Ag6uXALzM56gWEqpaiJmNaVFHhdOp2U24agDiIwsHbnSuL7BIdljRDttBmkQ/hNR8JP9V2muG7X1MoUZialDJI/XzMLLKz/PQeRQb7T3CaYJFchtLbGbBbr8uesakb+rd3wLINmyI916s8lAva70eBY67mxvUyXjZEgneHuMmX5l54Q1d9PflbmwSg78z2NNoZAC1on2z2D8PLOjCM6YL6jqAwDiQXOqwUWGZlqr2l836xr6SGAA2MgBqikirN6+DAEa3flVZgZ7KdiyiE1XcccgMy810SW6CFiP90tjUxHCQRf6fmJu5nr8BcVeCTk8KlkBqlAV6Qd0qa/UwUcdWvuHvAMz9TtT7beyre020/Pdx0RcehvGd5Wa6JLdGGsM7saPRGCBqL8+fAgh1F7zgTNigU8mjk7Cx99VNPbv2OPUlS8JcLo2ieAydKQc4A62ROHTW+hVulHHRveyGM6sDmXm5q0v6g7oxphc3Gg38YgZJ7c7J3ws0svgDWfutNctP248rVl35SX49J0b7k6tX+AMXAf8eGIMnmqkuqreK3xg9XIHMvM1F/wIyUyEhcnzDpaOapt1YwCiPeVL4A6HZgxts9zLr3DrbAjoFVd/UB+H/yu7AH/BsHhbFJ2Jf94GidiVjuK33IDOfMs0l986kjKfPGCiB6Nc5cCZWQ+MBMIaE9rMJB5pmtuP/ZGabs8vEky4DP8+As8jjPlsjrDe+gTPwq9WBO/pqo69iATLzIdNcchuFYXuH8TiGf+mAyDZw1GLiOX2PJ6AzaK7Rr8SU4Q6LiHBLYP96GzpujYs/2DpFYB3EhKvuDYpF5Ji2kiAk5oV3meaSV9SN63TExlt60jsOwc4KLPZRAKk+O9PQ4volKFohgmNM7uWURjuC/xc/dGozu8sAOkVgwQOBMx8tKZT0+4nO6XeQGDqxSV5cNWzv1Fuq/rZ1CIOZUSC4AiR7B/fKAGqxn2JwsPqo1qnwJseIxkcGO2fDCTrHn48MAOU9ILtrgcCW1rppqk2Wjod5SMxrpLncnU0lI0tmN7HXkzgMjnxnQFgXr76I+dYZBq3x00T1lgzTOd7DPmzmBZTkKsJLbST727hLY7owDDhmf4CBbVHhbuoHYXx/q4v4HBLjJ9EPscqe4JltwGAsA+Cs5f625YDFPo4ZNqdgaJQv1cN8xlw6xKo1WmS9CNyVMZlhU+my8VUbgHQQ9+yZVN0mZbt6AMb3T7q65A/fy2Lkk003qWvRadzzTQU60QXfEwCpu0jBAdxVWA5HtZ55+DCiUz5BtBRcYGbJi8wygGV7sAQdNmHsnmWzqm5NDYqrfGX2QH/YRbwqc/ieJ9HXHCNmrTSFeyYo4TI254fO4EhvE0DHVTexlZqHc6YZm535XXdj6wDWv+xvA7DU536CjnskiT8wfq2MnB5RGffABmnRg3fimdcgL+Iq+/lL69wi7qHCmU5HDUHHcuCBzlXvl9SkkucTpLj23Aitk3eBcXVdAsO1jD/y07U60O5VxYQTaXn2/S75IzlLjGzv1XMlhz/AD2w6g1brLRjuS+hMb5kpo9pn4h4rakg9sEDndAA6zPg8Dp2NMv5E85eKQ/jxJDa+v0yKy+2Yoivt1a3IUgd/whIYBeA9yFEa/XICnLJCiVT2MbWFDY1KdBwvV32tMWpNAvieGp3uWdsKbqliapm0vE6Ky+2YmmY6sEd9HPcwUUKFKoBFOyIz0OlxgUPXeI3bllRms3E2TZRg5UyeTAHY8WPfbmMbwiMADhtgMK8X3UTLurQ812XwxguQFRr8rXemQTCxVrP7Mhu3Y1GwingSof5tYK17pA0dR4sF79r5pdXMfikDRyrLvi+dAiyE0yrgh7up3U0AO/uh429Ovkr9UIXAbdfEJFJZ0fvYdGRPxPJpQkoiDsGy70TbmY+Uv1LtT0LbhXUAMxFdyUqex2VXq3lF6e3YLHvc82ixjP+saK5YGDqDq6NLbiT7q4B7q+kOR80nrtrVsnaSqEAwUNe6eSOrrPAkLCHxXDHWzKQcHEFQ+yUcn3Xf3IzeDu3EfD+ry+duTH6DsQY6Lugsf+PMfzUMwJLWNJcXwGDfzKUnB51cGStpLOfRXov0q76DlSdHQzue7b6L8982IZiIMtWHISsv3Wsu8eCZ215VK7YhcI+c4/uGI7vw1UkWmGh2Ml8l7AHrnjV3NMyeYJQ2AC8Yp77f3GBYbDiOQqevFjrsXtj1zSR265XmGRD69SQY9s4cYt76PQTOO40NkpYVPY57AJHcfPdceRoGexngaNUCILuGnzxjR4C7uZCpB+w+n9qIpnusMz130UBPCMAwk+50P5D392Qe9/ijAbV/9SBQr++EQ0Do2BPB4KEXgH0I8O/AwBLUFHmHf3/RJZDaBr025/ECBukNhPza3SGPtAaOPbFiBMtf/eqa9nq34+HIxt5GZbJzvF5KTN5CJ/Q7e3fSm0QYxgF8vpPRi17VeNJo1MS4JyYmGvM3jgmUbcoybMMOLdgWVDbFMtAqCBRKW4vVtkBrWxhcUKxSP4bDFrFVE4+D/i4kMJnLmzzDvO+zZEZHPvjfhEKZwJyr4NBFjOqndGUe40ujwxN28BYVNZKKwW/FD/G6YHOgD5wifhBuA/A1F/oM22zb4UztxT2rbZyRAnBsjLtTas1s+cNUbd4OnkqvB3xDO+OARSuhAb1+s32judqUSx+iVB+zLss6eCvOKc29ynTGvD0dX0KfVcFWMJ7fT/QIv3S1Z44TWQBIx1ZtlCk6wkfq9uG4gnI1aZqags5XydO+YK74xplVS02rfu1Y5P3kq8pIDPMUTTddSx8A1yRyFu+7F49GpxMfjQA+KbkABsJpomsAkiN7jLb6DHrKrzPDo8Vo1QnYn0fQpiowESD4PCkF3Vx6DsS1OcA4VlhER+uQJqaMmkbNoYIePZn6ewHvvPa5QvQ7JeyCto50RcKOA1K7nZmzo630kJoHPkms7wwLgYT/s2LDFUhWHgAwNxqTrY9i0uvaUBT8E4EFw7vH5AbgMr1exE9SJFkUdoVDx76rRL/9gh/lAkyQ7HKFAYJ562OJHV0KmT13b/ZDxmvzPbDS9OSSOV5r1bRZA4kXUoxFDTPvNZP89xqfbSbjD2Tf6t3f0JIyV4oBOVpy1D0xK/iO3z9vzQi/zKVFIRKHgkYA+pB+lgJ64q+iC/hZ4KurpNWrl3Xj21O7f3pEG9C2LtFo6m/QJlclJMIf2INjRNsgHLS16RRabhZtCZGOegn0RNwj2M2y3NQAPlq7dyENd4LoYICKBj0h7qtTB2G7TBCD9FB3VvlKQznaIoxDNgZmBV3Dq+CpP0/pneix1AvAet2PNil+sDwAdOia1RrRYyBFEmEPavrxSB+E7Blg/R4pW0NHwbxtRai6Aej04D2RO94COiXNVF3oUn1uX/kEQERtm8APxhLSWj06XCIdeoLZoR3hbsUBvayZAXpT36RZC9ocktFqCLZqSR3vLlKavVcCwsm3Qy+xh8vkHFrATwKcEx2evlYjWxKTwBvInSB2uwBhm23MoK3WkElcQY0GUqsysuFHzCDTkmkYo4nPz+TYw+M1mh/jJ7H71PwiAIcKj8J2l28NLZmGAcJ2ndjt3CUI2mtxMYIWe8K8c0fGmt9uLmmkWgqaRpTJf02pvowHouAFJ+zoEyt64nmgFMQmeJuLiG2TIo6WI1kf/TRSF4mrH9BCc2kIWi8Rtkf4DSmgpjjzClqMAc+35Iv7IjeXgS+LnLf64hlrWxM9TE5CHcN8oy/Il+S6+JPVZVh2/FJrGvznCMyVkbylOpMYyphY2dJMoQxezsY+Enh0P0J0DcSZekfqK9s59o4VLdaCfCUdf8Agzk6na2I2ymw+FK1oDEhmIwrJfWs4/D45q4BjeMcCPKTcEUf1Taqel3uyzWXd83fe6vB9UiwJV80rW00neDotWxV4JzGcIfoMQp1LS6zCFtAilb+JIbMEYNG0/Vwr8obFZiYhW9R68bRu0UlGRx7T0Wz9vU6pFLuwfr8qK+PBSMnGvg5UDXeU/HKTy1b3w9lKchOO5mvwPJId4abLdF0k9jon7C5TPDP3Geh5PSffMuwUGal6DVs11j/zQidOYKwa1YgXPB9jsbKVMoje3PeilrWJ39eqeTwRzae3tZLJhNNR3KnQ6OchBT/E49oNom3AdmJtDS/6lQrfguh4VtxeMCbsULlFz7J3SJKUWAwsOySpxzHNuU3PnzdnYCenYHSSDgCOZuUj+r2p+yBwxwjewL204bWY31PHL81VaTt482KnqjS27kxU3xWL4xsbn3NgnONbihTANL96SrVKAG1G9FFt7LCCzZbpuU78guAHewALHKv1zXlK2GtRCuQWHldD6Eg2yFV0GN2TpjAWzb4YVKkcdlEzq9MmMTcs4KJFXi9Tqt8AdKRoc1Giep3MjkyNb61hj4inYEeXemIdXdJUzq7DL5QZp9dsEnF1MpoR+prjKLHLIDQn6JAyfkPlC9fgJErKPPXSsmUvS//6Hk/sHxWJqeHHbhHbqEvuPZ1wCHw+U8tlYo8BaDOFHvnKt9DTilvMNers0Bf3aPi9LR5atax7YmM6fTmoNu66XB0s63VjjOeTxR+asQ2HKfcXCVtvcKyyqJnxb6kxCDrbcXsJfoZPP3n5UzpT04zekw1xXL3Br7+YFPGt/WXZR3mKtmq6rDSVN2VlfNW6aEjMcvx1HEcql18sJef8ipyA69B3O078zhUMGqlK77GkJ+bi02Er9cq0/Eym/CIaIkm2S0zy3WSUsmfLpjxlfTAdD018cDrWNgX/BN/jLEEMdnz/Hbla9aS0Zme2HClFV8rhYVZy5Scq9eCtc7/DhwjiH4jv//Xjo/s/FN//4/0mug9Cn6n/fov/7/4Ht+7+N4BuEn9y8PZ/A+gk8Sff2bVjlIWhIAjA835SJAT+RkVEC1ESiY0iKQTBC+hl5v6NIgixyXuvzO58d1h2ltn5gmLOeoVRHcWcBuOeFHN6jKsrijH3EhFHijFXxOz/KLZcENVQTCkQ96CY0iIuKMqZspgjwYliSIc3RTlfLkiypJhRIM2ZYsYNaeoNxYhDiUQtxYgjBlSwuvAtVXW1OdLhQ1ebJzv80C+FAw1y7CgGnDGgrs2FIuCX3qbs65En/FMmrgoYUq3uwRa5QkGZtKpGtp4yaS3yBdUukzYrAY26My3etNVd+W50BXhHtoBG/cXe3euoCkRxAD8YCggJjRhDtCAa10izaixITKzstNrKJ9ie929u4t2b9SqowADnnPn/XmEyH+djZixTMNHRN6Xdjm4gA28F16HatjmItKY7qKurt6AHaKHRbkuNfOcgzoqaiQ45CFPeAoseeLVSKoXrLkrdVlqQobHEnp7CJVaFQocMmE9yEGOwpSuc5SySUQH00Kh2iOgBCuvKJXSFs5xFQjInxllOhMGRrnCWs0hKT+GWk0LTgIyaocbK35kqwpPg4mV0B4UX9YYeGbfFAs/bmq6wwFskozYEuPvAmO/RD5zgrXGmllxyYOqTbiFFYwM3oNbEeDSWpcmMmsEHvPJ80Eu456TMmNrl4S8ndpYRFUBiTrU1FUNpXa+USqF3SqmFQ8Wwrau1jKkTM3TMsTE4UzlE6zpdqDNZDiysqDsBkvAsTD3qULzMoXejOXVqgxxN/07UsSSH6qQe4vBLIxMr6p6DzFyvwoB64KFRskd+RO/CEV6J0ZF6skE+tieDNRmBb14ESagyFNeFS6kqBG7SZVQLOiUFGztUC8J1ucKAeueh4tYpNyIGIiRpOuTHxEKEprnODOfERDzMoROHI7Exx6h3YjQjRmKs8B0YbYkVzPX2TTbEzBHfOrVsciZ2thj1W1aMOdEM5fUWjdit7X8dMeqtOTAdc5zm2nNgFashcuvCkFFO5lGMPHwLfDa512IRam7GuUxqLOU81NcNC1nUUp9z0Etj1NgjCdA3Z1DWe28UemTfoqfvtYodbkEYMUhIkA0S8QaM1iTKHAF7Yz7jNFyxCKFbQyH78PyR851DAysG7e01JHiXRtTbImacUWutaXQisWJk4muZsq6qvRLgbckaVjIyr9jYzRmI3c5/bdBYUcmQZQMkIvY2LQRG54W+sMQrLLBgiTdjKCzZ/lyEzoo3jLUs7f8k+LHzhckXqXNEouYpV1xN7R1OivNcuU+Z9ZXXNiiyl/BVBOfFvE9M9iKZgC7nBjbTHO74qgI1THZM8x9b7Ow3pop381vBBR3SPwap9Crq+46owVwtVMbmpXZ4vyBfirrKYEJk+4FuYMUB7t5skVssZPuITMt21lZch3uylnexsvY2SW1c2X/FmX1b+4r5EzIdmFkWvi1s3cz/d7ao0u4Kvrpi2MmSzOx0L+UxkS44ewuqb36itVGiriBRPuz+hz1p9irDrniRx5CXcU5Kj3RTLOzPrBXmZt0dhvyFzVhXumahvhnKiFmmJjk7WTH7YImx+KKiFDNMtd1TalewE7+5h3sc2Cvbfgt+dnKUIcVeT5QIDeHcD7trp42nu7hmuiUmeWPebiyoY3qy2GOSGxF/hDJid/cL/REGHS8u93GfpnZ1sf9p5wxWIAShKErhQgnc2CCRC1FMamNFO6FVu2blar7A//+E2bUfZjJj3vmFy3nPxwWToHLOXQwzVOXnsAWa4X4v0UtB4mfSSJ7VN8OrkbDHE4BHJ/IY9CLu8FZPRqElv/iAZ1xuMNRTU83dVcEzEyboyNNzBN+TpKO+JLyboEm5mkIvA02ivEXOazA8G7DyjrLTnC8ZdX4GwTOk0nvokS1/rHcflg38zhus984ZYdsv5V4Fjd2+gd43AjdPHxxH5LP0W0uQccGPGsNBdlsKXKtxkWGI3FAkCGN2fRysljEiEKU8DkEuo6r/IOs3pW5TUbGHSzsAAAAASUVORK5CYII=";     
     } else {  
    // Default image URL if none of the conditions match
    return "data:image/png;base64,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";    
}
}

function checkOrder() {
    var token = $("#token").val();
    var params = { token: token };
           var cardContainer = document.getElementById("card-container");
               
        cardContainer.innerHTML = '';
        
cardContainer.innerHTML = `<div class="loadernum">
  <div class="wrapper">
    <div class="circlenum"></div>
    <div class="line-1"></div>
    <div class="line-2"></div>
    <div class="line-3"></div>
    <div class="line-4"></div>
  </div>
</div>`;

//    clearInterval(smsInterval);

    // AJAX call for checking the order
    $.ajax({
        type: "GET",
        url: "api/service/ActiveNumber",
        data: params,
        dataType: "json", // Set the expected data type
        error: function (e) {
            console.log("AJAX error:", e);
     //       toast.error("Something Went Wrong");
            location.reload();
        },
        success: function (data) {
user_balance(token);               
            cardContainer.innerHTML = '';

if (data.data.length === 0) {
 cardContainer.innerHTML = `   <div class="panel dark:bg-[#1b2e4b]" >
               <center><img src="https://cdn-icons-png.flaticon.com/512/5089/5089767.png" height="100" width="100"></center>
                <div class="flex items-center justify-center mt-2">
                    <h5 class="font-bold text-lg dark:text-white-light">No Any Active Numbers</h5>
                  
                </div>
              </div>`;
}
    
            // Iterate through the JSON data and create cards
            data.data.forEach(function (item) {
                var card = document.createElement("div");
                card.className = "card shadow-white col-md-12";
                card.style.borderRadius = "18px";

                card.innerHTML = `
     <div class="panel shadow dark:bg-[#1b2e4b] dark:border-0 flex flex-col p-4 mt-3 mb-2">
    <div class="card-text space-y-3">
        <div class="flex items-center mb-0">
            <img id="flag_${item.id}" src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ6os1cbe84_XbWy76cW9R8uszpM9ASmrG17Q&usqp=CAU" height="45" width="45" class="me-2">
            <div class="flex-grow-1 mb-0">
                <div class="flex items-center">
                    <p id="num" class="ml-2">${item.number}</p>
                    <span id="copy" onclick="copyToClipboard(${item.number})" class="copy-icon ml-2 cursor-pointer"><i class="far fa-copy me-2"></i></span>
                </div>
                <p id="service-name" class="inline-block text-sm mb-0 ml-2">${item.app} - ₦${item.amount}</p>
            </div>
        </div>
        <div class="relative">
            <textarea id="sms_${item.id}" class=" dark:bg-[#0e1726] form-control shadow w-full mt-0" placeholder="Searching for otp" rows="4" disabled>${item.sms}</textarea>
               <p id="t_${item.id}" class="dark:text-[#0e1726]" style="position: absolute; bottom: 10px; right: 10px; border-radius: 20px; background: #e1e3e5; padding-right: 10px; padding-left: 10px; padding-top: 5px; padding-bottom: 5px;"><i class="fa fa-clock"></i>20:00</p>
        </div>

        <div class="text-center mt-2">
            <div class="flex">
                <button id="buy_${item.id}" onclick="buy('${item.id}', 'buy_${item.id}','${item.number}')" class="btn btn-rounded color-primary btn-outline-primary mr-2"><span class="fa fa-history mr-2"></span>Buy New</button>
                <button id="cancel_${item.id}" onclick="model_cancle('${item.id}', 'cancel_${item.id}','${item.number}')" class="btn btn-rounded color-danger btn-outline-danger lh-normal mb-0"><span class="fa fa-trash-alt mr-2"></span>Cancel</button>
            </div>
        </div>
    </div>
</div>
                `;

                 cardContainer.appendChild(card);
            });
             data.data.forEach(function (items) {
             
               countdownTimer(items.left_time, "t_" + items.id);
               getsms("sms_" + items.id,items.id,token);
               const imageUrl = getImageUrlBasedOnDigits(items.number); // Replace with your logic to get the image URL
               const imageElement = document.getElementById("flag_" + items.id);
               imageElement.setAttribute("src", imageUrl);
        
        
        
            });
            var jsonResponse = JSON.parse(data);
var intervaldata = [];

// Check if the 'data' key exists in the JSON response
if (jsonResponse && jsonResponse.data) {
    // Iterate through the 'data' array and store 'id' values in the 'idArray'
    jsonResponse.data.forEach(function(item) {
        intervaldata.push(item.id);
    });
}

        }
    });
}



checkOrder();



