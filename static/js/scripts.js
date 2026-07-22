/*!
* Start Bootstrap - Clean Blog v6.0.9 (https://startbootstrap.com/theme/clean-blog)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-clean-blog/blob/master/LICENSE)
*/
window.addEventListener('DOMContentLoaded', () => {
    let scrollPos = 0;
    const mainNav = document.getElementById('mainNav');
    const headerHeight = mainNav.clientHeight;
    window.addEventListener('scroll', function() {
        const currentTop = document.body.getBoundingClientRect().top * -1;
        if ( currentTop < scrollPos) {
            // Scrolling Up
            if (currentTop > 0 && mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-visible');
            } else {
                console.log(123);
                mainNav.classList.remove('is-visible', 'is-fixed');
            }
        } else {
            // Scrolling Down
            mainNav.classList.remove(['is-visible']);
            if (currentTop > headerHeight && !mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-fixed');
            }
        }
        scrollPos = currentTop;
    });
})

function sendLiketoServer(slug){
    var xhr = new XMLHttpRequest();
    //Configure the request
    xhr.open("POST", "/likes", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    //definr the data to send in the request body
    var data = JSON.stringify({post_slug : slug});
    //define the function to handle the response
    xhr.onreadystatechange = function(){
        if (xhr.readyState === XMLHttpRequest.DONE){
            if (xhr.status === 200){
                console.log("like sent successfullu");
            } else{
                console.log("Error sending like:", xhr.status);
            }
        }
    };
    console.log(data)
    // send the request with the data
    xhr.send(data);

    // change the text of button
    var label = document.getElementById('like_button').innerHTML;
    console.log(label);
    if (label==="Like"){
        document.getElementById("like_button").innerHTML = "Dislike";
        document.getElementById("like_button").style = "background-color: red;"
    }else{
        document.getElementById("like_button").innerHTML = "Dislike";
    }
}

function sendDisliketoServer(slug){
    var xhr = new XMLHttpRequest();
    //Configure the request
    xhr.open("POST", "/dislikes", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    //definr the data to send in the request body
    var data = JSON.stringify({post_slug : slug});
    //define the function to handle the response
    xhr.onreadystatechange = function(){
        if (xhr.readyState === XMLHttpRequest.DONE){
            if (xhr.status === 200){
                console.log("dislike sent successfullu");
            } else{
                console.log("Error sending dislike :", xhr.status);
            }
        }
    };
    console.log(data)
    // send the request with the data
    xhr.send(data);

    // change the text of button
    var label = document.getElementById('dislike_button').innerHTML;
    console.log(label);
    if (label==="Dislike"){
        document.getElementById("dislike_button").innerHTML = "Like";
        document.getElementById("dislike_button").style = "background-color: green;"
    }else{
        document.getElementById("dislike_button").innerHTML = "Like";
    }

}

function Request_for_Downloads(slug){
    var xhr = new XMLHttpRequest();
    //Configure the request
    xhr.open("POST", "/post/" + slug +"/downloadpdf", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    //definr the data to send in the request body
    var data = JSON.stringify({post_slug : slug});
    //define the function to handle the response
    xhr.onreadystatechange = function(){
        if (xhr.readyState === XMLHttpRequest.DONE){
            if (xhr.status === 200){
                console.log("Request sent successfullu");
            } else{
                console.log("Error sending Request :", xhr.status);
            }
        }
    }
    console.log(data);
    // send the request with the data
    xhr.send(data)
}
