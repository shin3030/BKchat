
$(document).ready(function () {


    $(window).scroll(function () {
      let value = $(window).scrollTop();
      $('#cloud').css('left', value * 0.3 + 'px');
      $('#cloud').css('top', value * 0.15 + 'px');
      $('#sunrisecloud').css('left', value * 0.3 + 'px');
      $('#sunrisecloud').css('top', value * 0.3 + 'px');
      $('#sunsetcloud').css('left', value * 0.2 + 'px');
      $('#sunsetcloud').css('top', value * 0.25 + 'px');
      $('#sun').css('top', value * 0.4 + 'px');
      $('#sun').css('left', value * 0.4 + 'px');
      $('#sunset').css('top', value * 0.4 + 'px');
      $('#mount').css('top', value * 0.3 + 'px');
      if (value > 500) {
        $('#sun').css('display', 'none');
      } else {
         $('#sun').css('display', 'block');
         }

      // if (value > 200) {
      //   if ($(".ChatBox").hasClass("hide")) {
      //     $(".ChatBox").toggleClass("hide");
      //   }
      // } else {
      //   $(".ChatBox").addClass("hide");
      // }
      if (value > 480) {
        $(".chat-container").removeClass("hide");
      } else {
        $(".chat-container").addClass("hide");
        $(".chat-floating-button").removeClass("active");
      $('.chat-iframe').removeClass("showchat");
      }
      if (value > 1400) {
        if ($(".yuko").hasClass("hideimg")) {
          $(".yuko").toggleClass("hideimg");
        }
      } else {
        $(".yuko").addClass("hideimg");
      }
      // console.log(value);
    });
  

    $(".back-top").on("click", function (event) {
      $("html, body").animate(
        {
          scrollTop: 0
        },
        50
      );
    });
    $(".chat-floating-button").click(function(){
      $(".chat-floating-button").toggleClass("active");
      $('.chat-iframe').toggleClass("showchat");
      $(".chat-floating-button").toggleClass("show");
      var chatIframe = $('.chat-iframe')[0].contentWindow.document;
        chatIframe.getElementById('messageFormeight').scrollTop = chatIframe.getElementById('messageFormeight').scrollHeight;
  })
    AOS.init();


    
  });
  
    
